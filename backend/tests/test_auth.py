from datetime import date

import jwt
import pytest
from sqlalchemy import text

from app import auth, models
from app.database import engine

CONFIG = {"ingresos_mensuales": 300_000, "dia_cobro": 1, "meta_ahorro": 0, "gastos_fijos": []}


def _headers(respuesta_login):
    return {"Authorization": f"Bearer {respuesta_login.json()['token']}"}


def test_sin_sesion_da_401(client_anonimo):
    assert client_anonimo.get("/api/dashboard").status_code == 401
    assert client_anonimo.post("/api/gastos", json={"monto": 100}).status_code == 401


@pytest.mark.parametrize("header", ["Bearer basura", "basura", "Basic abc"])
def test_token_invalido_da_401(client_anonimo, header):
    assert client_anonimo.get("/api/dashboard", headers={"Authorization": header}).status_code == 401


def test_token_vencido_da_401(client_anonimo, entrar):
    usuario_id = int(jwt.decode(entrar().json()["token"], options={"verify_signature": False})["sub"])
    vencido = jwt.encode({"sub": str(usuario_id), "exp": 0}, auth._secreto(), algorithm="HS256")
    assert client_anonimo.get("/api/dashboard", headers={"Authorization": f"Bearer {vencido}"}).status_code == 401


def test_login_de_google_invalido_da_401(client_anonimo, monkeypatch):
    monkeypatch.delenv("MANGO_GOOGLE_CLIENT_ID", raising=False)
    r = client_anonimo.post("/api/auth/google", json={"credential": "cualquier-cosa"})
    assert r.status_code == 401


def test_primer_login_crea_usuario_con_nombre_de_google(entrar, client_anonimo, fijar_hoy):
    r = entrar(nombre="Ana", email="ana@example.com")
    assert r.status_code == 200
    assert r.json()["nombre"] == "Ana"
    # Usuario nuevo: todavía no configuró nada.
    assert client_anonimo.get("/api/dashboard", headers=_headers(r)).status_code == 404

    fijar_hoy(date(2026, 9, 1))
    d = client_anonimo.post("/api/config", json=CONFIG, headers=_headers(r)).json()
    assert d["nombre"] == "Ana"


def test_volver_a_entrar_usa_el_mismo_usuario(entrar, db):
    entrar()
    entrar(nombre="Bruno Cambiado")
    usuarios = db.query(models.Usuario).all()
    assert len(usuarios) == 1
    assert usuarios[0].nombre == "Bruno Cambiado"


def test_cada_usuario_ve_solo_sus_datos(entrar, client_anonimo, fijar_hoy):
    fijar_hoy(date(2026, 9, 1))
    bruno = _headers(entrar())
    ana = _headers(entrar(sub="google-ana", email="ana@example.com", nombre="Ana"))

    client_anonimo.post("/api/config", json=CONFIG, headers=bruno)
    client_anonimo.post("/api/config", json=CONFIG, headers=ana)
    gasto = client_anonimo.post("/api/gastos", json={"monto": 5_000}, headers=bruno).json()["gastos_ciclo"][0]

    assert client_anonimo.get("/api/dashboard", headers=ana).json()["gastos_ciclo"] == []
    # Ana no puede editar ni borrar el gasto de Bruno.
    assert client_anonimo.put(f"/api/gastos/{gasto['id']}", json={"monto": 1}, headers=ana).status_code == 404
    assert client_anonimo.delete(f"/api/gastos/{gasto['id']}", headers=ana).status_code == 404
    assert len(client_anonimo.get("/api/dashboard", headers=bruno).json()["gastos_ciclo"]) == 1


def _crear_usuario_de_antes_del_login():
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO usuarios (id, nombre, dia_cobro) VALUES (1, 'Bruno', 1)"))


def test_email_inicial_se_queda_con_los_datos_de_antes(client_anonimo, entrar, monkeypatch, db):
    _crear_usuario_de_antes_del_login()
    monkeypatch.setenv("MANGO_EMAIL_USUARIO_INICIAL", "Bruno@Example.com")

    entrar(email="bruno@example.com")

    usuario = db.get(models.Usuario, 1)
    assert usuario.google_sub == "google-bruno"
    assert db.query(models.Usuario).count() == 1


def test_otro_email_no_se_queda_con_los_datos_de_antes(client_anonimo, entrar, monkeypatch, db):
    _crear_usuario_de_antes_del_login()
    monkeypatch.setenv("MANGO_EMAIL_USUARIO_INICIAL", "bruno@example.com")

    entrar(sub="google-intruso", email="intruso@example.com")

    assert db.get(models.Usuario, 1).google_sub is None
    assert db.query(models.Usuario).count() == 2
