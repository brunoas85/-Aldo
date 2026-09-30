import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Por defecto la base vive en backend/mango.db, sin importar desde dónde se levante el server.
# Los tests y producción (Postgres en Neon) la cambian con la variable de entorno MANGO_DATABASE_URL.
BACKEND_DIR = Path(__file__).resolve().parent.parent


def normalizar_url(url: str) -> str:
    """Neon (y casi todos los proveedores) dan la URL como postgres:// o postgresql://;
    SQLAlchemy necesita que le digan el driver, que acá es psycopg 3."""
    for prefijo in ("postgres://", "postgresql://"):
        if url.startswith(prefijo):
            return "postgresql+psycopg://" + url[len(prefijo) :]
    return url


SQLALCHEMY_DATABASE_URL = normalizar_url(
    os.environ.get("MANGO_DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'mango.db'}")
)
ES_SQLITE = SQLALCHEMY_DATABASE_URL.startswith("sqlite")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if ES_SQLITE else {},
    # Neon suspende la base cuando no se usa: se descartan las conexiones que murieron.
    pool_pre_ping=not ES_SQLITE,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
