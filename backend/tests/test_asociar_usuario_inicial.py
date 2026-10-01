from datetime import date

import pytest
from sqlalchemy import text

from app import models
from app.database import SQLALCHEMY_DATABASE_URL, engine
from scripts.asociar_usuario_inicial import ErrorAsociacion, asociar


@pytest.fixture
def datos_de_antes_y_cuenta_vacia(client_anonimo, entrar):
    """Usuario id=1 con datos y sin cuenta, más un usuario nuevo vacío creado por el registro."""
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO usuarios (id, nombre, dia_cobro) VALUES (1, 'vos', 1)"))
        conn.execute(
            text("INSERT INTO transacciones_diarias (usuario_id, fecha, monto) VALUES (1, :f, 500)"),
            {"f": date(2026, 9, 1)},
        )
    entrar(email="bruno@example.com", nombre="Bruno")


def test_pasa_la_cuenta_al_usuario_inicial_y_borra_el_vacio(datos_de_antes_y_cuenta_vacia, db):
    asociar(SQLALCHEMY_DATABASE_URL, "Bruno@Example.com")

    usuarios = db.query(models.Usuario).all()
    assert [(u.id, u.email, u.nombre) for u in usuarios] == [(1, "bruno@example.com", "Bruno")]
    assert len(usuarios[0].transacciones) == 1


def test_despues_de_asociar_se_entra_con_la_misma_contrasena(datos_de_antes_y_cuenta_vacia, client_anonimo):
    asociar(SQLALCHEMY_DATABASE_URL, "bruno@example.com")
    r = client_anonimo.post("/api/auth/login", json={"email": "bruno@example.com", "password": "clave-segura"})
    assert r.status_code == 200


def test_no_borra_si_la_cuenta_nueva_ya_tiene_datos(datos_de_antes_y_cuenta_vacia, client_anonimo, entrar):
    login = {"email": "bruno@example.com", "password": "clave-segura"}
    token = client_anonimo.post("/api/auth/login", json=login).json()["token"]
    client_anonimo.post(
        "/api/config",
        json={"ingresos_mensuales": 1000, "dia_cobro": 1, "meta_ahorro": 0, "gastos_fijos": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    with pytest.raises(ErrorAsociacion, match="ya tiene datos"):
        asociar(SQLALCHEMY_DATABASE_URL, "bruno@example.com")


def test_no_hace_nada_si_el_inicial_ya_esta_asociado(datos_de_antes_y_cuenta_vacia):
    asociar(SQLALCHEMY_DATABASE_URL, "bruno@example.com")
    with pytest.raises(ErrorAsociacion, match="ya está asociado"):
        asociar(SQLALCHEMY_DATABASE_URL, "bruno@example.com")
