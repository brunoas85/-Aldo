from alembic import command
from sqlalchemy import inspect, text

from app.database import engine
from app.migraciones import aplicar_migraciones


def test_base_vieja_sin_alembic_se_migra_sin_perder_datos(client, alembic_cfg):
    """Simula una aldo.db creada con create_all antes de Alembic: tiene el esquema
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
        assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0002"
        assert conn.execute(text("SELECT count(*) FROM configuraciones_mensuales")).scalar() == 1
    indices = {i["name"] for i in inspect(engine).get_indexes("configuraciones_mensuales")}
    assert "uq_config_usuario_ciclo" in indices


def test_aplicar_migraciones_es_idempotente(client):
    aplicar_migraciones()
    aplicar_migraciones()
    with engine.connect() as conn:
        assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0002"
