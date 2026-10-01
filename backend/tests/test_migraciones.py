from alembic import command
from sqlalchemy import inspect, text

from app.database import engine
from app.migraciones import aplicar_migraciones


def test_base_vieja_sin_alembic_se_migra_sin_perder_datos(client_anonimo, alembic_cfg):
    """Simula una mango.db creada con create_all antes de Alembic: tiene el esquema
    de 0001 con datos, pero no tiene la tabla alembic_version."""
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "0001")
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE alembic_version"))
        conn.execute(text("INSERT INTO usuarios (id, nombre, dia_cobro) VALUES (1, 'Bruno', 1)"))
        conn.execute(
            text(
                "INSERT INTO configuraciones_mensuales (usuario_id, anio, mes, ingresos_mensuales, meta_ahorro) "
                "VALUES (1, 2026, 9, 400000, 0)"
            )
        )

    aplicar_migraciones()

    with engine.connect() as conn:
        assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0005"
        assert conn.execute(text("SELECT count(*) FROM configuraciones_mensuales")).scalar() == 1
    indices = {i["name"] for i in inspect(engine).get_indexes("configuraciones_mensuales")}
    assert "uq_config_usuario_ciclo" in indices


def test_aplicar_migraciones_es_idempotente(client_anonimo):
    aplicar_migraciones()
    aplicar_migraciones()
    with engine.connect() as conn:
        assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0005"


def test_usuarios_de_google_conservan_sus_datos_sin_contrasena(client_anonimo, alembic_cfg):
    command.downgrade(alembic_cfg, "0003")
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO usuarios (id, nombre, dia_cobro, google_sub, email) "
                "VALUES (1, 'Bruno', 1, 'google-bruno', ' Bruno@Gmail.com')"
            )
        )

    command.upgrade(alembic_cfg, "head")

    with engine.connect() as conn:
        fila = conn.execute(text("SELECT id, email, password_hash FROM usuarios")).one()
    assert tuple(fila) == (1, "bruno@gmail.com", None)
    assert "google_sub" not in {c["name"] for c in inspect(engine).get_columns("usuarios")}
