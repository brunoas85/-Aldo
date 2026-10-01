from datetime import date

import pytest
from sqlalchemy import create_engine, text

from scripts.migrar_a_neon import ErrorMigracion, migrar

CONFIG = {
    "ingresos_mensuales": 400_000,
    "dia_cobro": 1,
    "meta_ahorro": 50_000,
    "gastos_fijos": [{"nombre": "Alquiler", "monto": 80_000, "categoria": "Alquiler"}],
}


@pytest.fixture
def origen_con_datos(client, fijar_hoy):
    """La base de los tests (SQLite) con config, un gasto y un ingreso."""
    fijar_hoy(date(2026, 9, 1))
    client.post("/api/config", json=CONFIG)
    client.post("/api/gastos", json={"monto": 1500, "descripcion": "café"})
    client.post("/api/ingresos", json={"monto": 20_000})
    from app.database import SQLALCHEMY_DATABASE_URL

    return SQLALCHEMY_DATABASE_URL


def _contar(url, tabla):
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            return conn.execute(text(f"SELECT count(*) FROM {tabla}")).scalar()
    finally:
        engine.dispose()


def test_copia_todo_con_los_mismos_ids(origen_con_datos, tmp_path):
    destino = f"sqlite:///{tmp_path / 'destino.db'}"

    copiadas = migrar(origen_con_datos, destino)

    assert copiadas == {
        "usuarios": 1,
        "configuraciones_mensuales": 1,
        "gastos_fijos": 1,
        "ingresos_variables": 1,
        "transacciones_diarias": 1,
    }
    engine = create_engine(destino)
    with engine.connect() as conn:
        gasto = conn.execute(text("SELECT fecha, monto, descripcion FROM transacciones_diarias")).one()
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    engine.dispose()
    assert tuple(gasto) == ("2026-09-01", 1500.0, "café")
    assert version == "0005"


def test_no_copia_si_el_destino_ya_tiene_datos(origen_con_datos, tmp_path):
    destino = f"sqlite:///{tmp_path / 'destino.db'}"
    migrar(origen_con_datos, destino)

    with pytest.raises(ErrorMigracion, match="ya tiene datos"):
        migrar(origen_con_datos, destino)
    assert _contar(destino, "transacciones_diarias") == 1


def test_no_copia_si_el_origen_no_esta_migrado(tmp_path):
    origen = f"sqlite:///{tmp_path / 'vieja.db'}"
    create_engine(origen).connect().close()  # crea el archivo vacío

    with pytest.raises(ErrorMigracion, match="Levantá el backend"):
        migrar(origen, f"sqlite:///{tmp_path / 'destino.db'}")
