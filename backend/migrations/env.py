from alembic import context

from app import models  # noqa: F401  (registra las tablas en Base.metadata)
from app.database import Base, engine

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _migrar(connection):
    # render_as_batch: SQLite no soporta ALTER TABLE completo, Alembic recrea la tabla.
    context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # Quien llama puede pasar su propia conexión (ej. scripts/migrar_a_neon.py migra
    # otra base dentro de su transacción); si no, se usa la base de la app.
    connection = context.config.attributes.get("connection")
    if connection is not None:
        _migrar(connection)
        return
    with engine.connect() as connection:
        _migrar(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
