import os
import tempfile
from datetime import date
from pathlib import Path

import pytest

# Tiene que definirse antes de importar la app: nunca tocar backend/mango.db desde los tests.
_TMP_DIR = tempfile.mkdtemp(prefix="mango-tests-")
os.environ["MANGO_DATABASE_URL"] = f"sqlite:///{Path(_TMP_DIR) / 'test.db'}"

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import BACKEND_DIR, SessionLocal  # noqa: E402
from app.deps import get_hoy  # noqa: E402
from app.routers import auth as auth_router  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture
def alembic_cfg():
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    return cfg


@pytest.fixture
def client_anonimo(alembic_cfg):
    """Cliente sin sesión, con la base recién migrada (el lifespan corre las migraciones).
    Al terminar baja todas las migraciones, así cada test arranca de cero."""
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    command.downgrade(alembic_cfg, "base")


@pytest.fixture
def entrar(client_anonimo, monkeypatch):
    """Simula el login con Google (sin hablar con Google) y devuelve la respuesta:
    entrar(sub="otro", email="otra@example.com", nombre="Ana")."""

    def _entrar(sub="google-bruno", email="bruno@example.com", nombre="Bruno"):
        datos = {"sub": sub, "email": email, "given_name": nombre, "email_verified": True}
        monkeypatch.setattr(auth_router, "verificar_token_google", lambda _credential: datos)
        return client_anonimo.post("/api/auth/google", json={"credential": "token-de-google"})

    return _entrar


@pytest.fixture
def client(client_anonimo, entrar):
    """Cliente con la sesión de un usuario ya iniciada."""
    token = entrar().json()["token"]
    client_anonimo.headers["Authorization"] = f"Bearer {token}"
    return client_anonimo


@pytest.fixture
def fijar_hoy():
    """Fija la fecha que ve la API: fijar_hoy(date(2026, 9, 1))."""

    def _fijar(fecha: date):
        app.dependency_overrides[get_hoy] = lambda: fecha

    return _fijar


@pytest.fixture
def db():
    sesion = SessionLocal()
    try:
        yield sesion
    finally:
        sesion.close()
