import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Por defecto la base vive en backend/aldo.db, sin importar desde dónde se levante el server.
# Los tests (y un futuro Postgres) la cambian con la variable de entorno ALDO_DATABASE_URL.
BACKEND_DIR = Path(__file__).resolve().parent.parent
SQLALCHEMY_DATABASE_URL = os.environ.get("ALDO_DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'aldo.db'}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
