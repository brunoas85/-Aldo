"""Copia todos los datos de la base local (SQLite) a otra base, pensado para Neon.

Uso (desde backend/, con el venv activado):

    python -m scripts.migrar_a_neon                 # te pide la URL de Neon sin mostrarla
    python -m scripts.migrar_a_neon --origen otra.db

Crea las tablas en el destino con las migraciones de Alembic y copia las filas con
los mismos ids. Todo pasa en una sola transacción: si algo falla, el destino queda
como estaba. Se niega a copiar si el destino ya tiene datos.
"""

import argparse
import getpass
import sys
from pathlib import Path

from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, func, inspect, select, text

from app import models  # noqa: F401  (registra las tablas en Base.metadata)
from app.database import BACKEND_DIR, Base, normalizar_url
from app.migraciones import config_alembic


class ErrorMigracion(Exception):
    pass


def _version(conn) -> str | None:
    if "alembic_version" not in inspect(conn).get_table_names():
        return None
    return conn.execute(text("SELECT version_num FROM alembic_version")).scalar()


def migrar(origen_url: str, destino_url: str) -> dict[str, int]:
    """Devuelve cuántas filas copió por tabla."""
    cfg = config_alembic()
    head = ScriptDirectory.from_config(cfg).get_current_head()

    origen = create_engine(normalizar_url(origen_url))
    destino = create_engine(normalizar_url(destino_url))
    # sorted_tables respeta las foreign keys: primero usuarios, después configs, etc.
    tablas = Base.metadata.sorted_tables

    try:
        with origen.connect() as src:
            version = _version(src)
            if version != head:
                raise ErrorMigracion(
                    f"La base de origen está en la migración {version!r} y la última es {head!r}. "
                    "Levantá el backend en local una vez (aplica las migraciones) y volvé a correr esto."
                )
            filas = {t.name: [dict(r._mapping) for r in src.execute(select(t).order_by(*t.primary_key))] for t in tablas}

        with destino.begin() as dst:
            cfg.attributes["connection"] = dst
            command.upgrade(cfg, "head")

            con_datos = [t.name for t in tablas if dst.execute(select(func.count()).select_from(t)).scalar()]
            if con_datos:
                raise ErrorMigracion(
                    f"El destino ya tiene datos en: {', '.join(con_datos)}. No copio nada para no mezclar."
                )

            for t in tablas:
                if filas[t.name]:
                    dst.execute(t.insert(), filas[t.name])

            # Insertamos con ids explícitos: en Postgres hay que avanzar las secuencias
            # o el próximo gasto que cargues choca con un id existente.
            if dst.dialect.name == "postgresql":
                for t in tablas:
                    dst.execute(
                        text(
                            f"SELECT setval(pg_get_serial_sequence('{t.name}', 'id'), "
                            f"COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM {t.name}"
                        )
                    )

            copiadas = {t.name: dst.execute(select(func.count()).select_from(t)).scalar() for t in tablas}
            esperadas = {nombre: len(f) for nombre, f in filas.items()}
            if copiadas != esperadas:
                raise ErrorMigracion(f"Las cantidades no coinciden: origen {esperadas}, destino {copiadas}.")
    finally:
        origen.dispose()
        destino.dispose()

    return copiadas


def main() -> int:
    parser = argparse.ArgumentParser(description="Copia los datos de $Aldo de SQLite a Neon (Postgres).")
    parser.add_argument("--origen", default=str(BACKEND_DIR / "aldo.db"), help="archivo SQLite (default: aldo.db)")
    args = parser.parse_args()

    origen = Path(args.origen)
    if not origen.exists():
        print(f"No encuentro {origen}.")
        return 1

    # Se pide con getpass para que la contraseña no quede en el historial de la terminal.
    destino = getpass.getpass("Pegá la connection string de Neon (no se ve al escribir): ").strip()
    if not destino.startswith(("postgres://", "postgresql://", "postgresql+psycopg://")):
        print("Eso no parece una URL de Postgres (tiene que empezar con postgresql://).")
        return 1

    try:
        copiadas = migrar(f"sqlite:///{origen.resolve()}", destino)
    except ErrorMigracion as e:
        print(f"No se copió nada. {e}")
        return 1

    print("Listo, se copió todo:")
    for tabla, cantidad in copiadas.items():
        print(f"  {tabla}: {cantidad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
