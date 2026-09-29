from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from .database import BACKEND_DIR, engine

# Revisión que representa el esquema que creaba create_all antes de usar Alembic.
REVISION_BASE = "0001"


def config_alembic() -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    return cfg


def aplicar_migraciones():
    """Lleva la base a la última migración al levantar el server.

    Si la base ya tiene tablas pero nunca pasó por Alembic (creada con create_all),
    se marca como REVISION_BASE sin tocar nada y se aplica solo lo nuevo."""
    cfg = config_alembic()

    tablas = inspect(engine).get_table_names()
    if "usuarios" in tablas and "alembic_version" not in tablas:
        command.stamp(cfg, REVISION_BASE)

    command.upgrade(cfg, "head")
