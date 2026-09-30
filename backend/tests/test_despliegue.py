import pytest

from app.database import normalizar_url


def test_health_no_pide_sesion(client_anonimo):
    assert client_anonimo.get("/api/health").status_code == 200


@pytest.mark.parametrize(
    "entrada, esperada",
    [
        ("postgresql://u:p@h.neon.tech/db?sslmode=require", "postgresql+psycopg://u:p@h.neon.tech/db?sslmode=require"),
        ("postgres://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql+psycopg://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("sqlite:///mango.db", "sqlite:///mango.db"),
    ],
)
def test_normalizar_url(entrada, esperada):
    assert normalizar_url(entrada) == esperada
