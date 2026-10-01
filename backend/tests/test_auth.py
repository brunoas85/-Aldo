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


def test_registro_y_login(entrar, client_anonimo):
    r = entrar(email="  Ana@Example.com ", nombre=" Ana ")
    assert r.status_code == 200
    assert r.json()["email"] == "ana@example.com"
    assert r.json()["nombre"] == "Ana"

    r = client_anonimo.post("/api/auth/login", json={"email": "ANA@example.com", "password": "clave-segura"})
    assert r.status_code == 200
    assert client_anonimo.get("/api/dashboard", headers=_headers(r)).status_code == 404


@pytest.mark.parametrize(
    "email,password",
    [("bruno@example.com", "clave-mala"), ("nadie@example.com", "clave-segura")],
)
def test_login_con_datos_incorrectos_da_401(entrar, client_anonimo, email, password):
    entrar()
    r = client_anonimo.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 401
    assert r.json()["detail"] == "Email o contraseña incorrectos"


def test_no_se_puede_registrar_dos_veces_el_mismo_email(entrar, db):
    entrar()
    r = entrar(email="BRUNO@example.com", password="otra-clave-larga")
    assert r.status_code == 409
    assert db.query(models.Usuario).count() == 1


@pytest.mark.parametrize(
    "datos",
    [
        {"email": "sin-arroba", "nombre": "Ana", "password": "clave-segura"},
        {"email": "ana@example.com", "nombre": "Ana", "password": "corta"},
        {"email": "ana@example.com", "nombre": "   ", "password": "clave-segura"},
    ],
)
def test_registro_con_datos_invalidos_da_422(client_anonimo, datos):
    assert client_anonimo.post("/api/auth/registro", json=datos).status_code == 422


def test_la_contrasena_no_se_guarda_en_texto_plano(entrar, db):
    entrar(password="clave-segura")
    guardado = db.query(models.Usuario).one().password_hash
    assert "clave-segura" not in guardado
    assert auth.verificar_password("clave-segura", guardado)
    assert not auth.verificar_password("clave-segurA", guardado)


def test_primer_registro_crea_usuario_vacio(entrar, client_anonimo, fijar_hoy):
    r = entrar(nombre="Ana", email="ana@example.com")
    # Usuario nuevo: todavía no configuró nada.
    assert client_anonimo.get("/api/dashboard", headers=_headers(r)).status_code == 404

    fijar_hoy(date(2026, 9, 1))
    d = client_anonimo.post("/api/config", json=CONFIG, headers=_headers(r)).json()
    assert d["nombre"] == "Ana"


def test_cada_usuario_ve_solo_sus_datos(entrar, client_anonimo, fijar_hoy):
    fijar_hoy(date(2026, 9, 1))
    bruno = _headers(entrar())
    ana = _headers(entrar(email="ana@example.com", nombre="Ana"))

    client_anonimo.post("/api/config", json=CONFIG, headers=bruno)
    client_anonimo.post("/api/config", json=CONFIG, headers=ana)
    gasto = client_anonimo.post("/api/gastos", json={"monto": 5_000}, headers=bruno).json()["gastos_ciclo"][0]

    assert client_anonimo.get("/api/dashboard", headers=ana).json()["gastos_ciclo"] == []
    # Ana no puede editar ni borrar el gasto de Bruno.
    assert client_anonimo.put(f"/api/gastos/{gasto['id']}", json={"monto": 1}, headers=ana).status_code == 404
    assert client_anonimo.delete(f"/api/gastos/{gasto['id']}", headers=ana).status_code == 404
    assert len(client_anonimo.get("/api/dashboard", headers=bruno).json()["gastos_ciclo"]) == 1


def _crear_usuario(id_, email=None):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO usuarios (id, nombre, dia_cobro, email) VALUES (:id, 'Viejo', 1, :email)"),
            {"id": id_, "email": email},
        )
        conn.execute(
            text("INSERT INTO transacciones_diarias (usuario_id, fecha, monto) VALUES (:id, :f, 500)"),
            {"id": id_, "f": date(2026, 9, 1)},
        )


def test_cuenta_que_venia_de_google_se_recupera_registrandose(client_anonimo, entrar, db):
    _crear_usuario(7, email="bruno@example.com")
    r = client_anonimo.post("/api/auth/login", json={"email": "bruno@example.com", "password": "lo-que-sea"})
    assert r.status_code == 401
    assert "registrate" in r.json()["detail"]

    assert entrar(email="Bruno@example.com", nombre="Bruno").status_code == 200

    usuario = db.query(models.Usuario).one()
    assert (usuario.id, usuario.nombre, len(usuario.transacciones)) == (7, "Bruno", 1)
    r = client_anonimo.post("/api/auth/login", json={"email": "bruno@example.com", "password": "clave-segura"})
    assert r.status_code == 200


def test_email_inicial_se_queda_con_los_datos_de_antes(client_anonimo, entrar, monkeypatch, db):
    _crear_usuario(1)
    monkeypatch.setenv("MANGO_EMAIL_USUARIO_INICIAL", "Bruno@Example.com")

    entrar(email="bruno@example.com")

    usuario = db.query(models.Usuario).one()
    assert (usuario.id, usuario.email) == (1, "bruno@example.com")


def test_otro_email_no_se_queda_con_los_datos_de_antes(client_anonimo, entrar, monkeypatch, db):
    _crear_usuario(1)
    monkeypatch.setenv("MANGO_EMAIL_USUARIO_INICIAL", "bruno@example.com")

    entrar(email="intruso@example.com")

    assert db.get(models.Usuario, 1).email is None
    assert db.query(models.Usuario).count() == 2
