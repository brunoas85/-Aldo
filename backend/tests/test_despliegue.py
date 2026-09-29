import pytest

from app.database import normalizar_url


@pytest.fixture
def con_clave(monkeypatch):
    monkeypatch.setenv("ALDO_API_KEY", "secreta")


def test_sin_clave_configurada_la_api_queda_abierta(client):
    assert client.get("/api/dashboard").status_code == 404


def test_con_clave_configurada_rechaza_requests_sin_clave(client, con_clave):
    r = client.get("/api/dashboard")
    assert r.status_code == 401
    assert client.post("/api/gastos", json={"monto": 100}).status_code == 401


def test_con_clave_configurada_rechaza_clave_incorrecta(client, con_clave):
    assert client.get("/api/dashboard", headers={"X-Aldo-Clave": "otra"}).status_code == 401


def test_con_clave_correcta_pasa(client, con_clave):
    # 404 porque no hay config: la clave ya pasó.
    assert client.get("/api/dashboard", headers={"X-Aldo-Clave": "secreta"}).status_code == 404


def test_health_no_pide_clave(client, con_clave):
    assert client.get("/api/health").status_code == 200


@pytest.mark.parametrize(
    "entrada, esperada",
    [
        ("postgresql://u:p@h.neon.tech/db?sslmode=require", "postgresql+psycopg://u:p@h.neon.tech/db?sslmode=require"),
        ("postgres://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql+psycopg://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("sqlite:///aldo.db", "sqlite:///aldo.db"),
    ],
)
def test_normalizar_url(entrada, esperada):
    assert normalizar_url(entrada) == esperada
