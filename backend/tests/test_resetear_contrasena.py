import pytest

from app.database import SQLALCHEMY_DATABASE_URL
from scripts.resetear_contrasena import ErrorReseteo, resetear


def _login(client, password):
    return client.post("/api/auth/login", json={"email": "bruno@example.com", "password": password})


def test_resetea_la_contrasena(client_anonimo, entrar):
    entrar(password="clave-vieja")
    resetear(SQLALCHEMY_DATABASE_URL, " Bruno@Example.com ", "clave-nueva")
    assert _login(client_anonimo, "clave-vieja").status_code == 401
    assert _login(client_anonimo, "clave-nueva").status_code == 200


def test_email_inexistente(client_anonimo):
    with pytest.raises(ErrorReseteo, match="No hay ningún usuario"):
        resetear(SQLALCHEMY_DATABASE_URL, "nadie@example.com", "clave-nueva")


def test_contrasena_corta(client_anonimo, entrar):
    entrar()
    with pytest.raises(ErrorReseteo, match="al menos 8"):
        resetear(SQLALCHEMY_DATABASE_URL, "bruno@example.com", "corta")
