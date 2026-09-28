from datetime import date

import pytest

from app import models

# Ciclo de referencia: cobro el 1, septiembre 2026 tiene 30 días.
# Pool base = 400.000 - 100.000 (fijos) - 50.000 (ahorro) = 250.000 → 8.333,33 por día.
CONFIG = {
    "ingresos_mensuales": 400_000,
    "dia_cobro": 1,
    "meta_ahorro": 50_000,
    "gastos_fijos": [
        {"nombre": "Alquiler", "monto": 80_000, "categoria": "Alquiler"},
        {"nombre": "Internet", "monto": 20_000, "categoria": "Servicios"},
    ],
}


@pytest.fixture
def configurado(client, fijar_hoy):
    fijar_hoy(date(2026, 9, 1))
    r = client.post("/api/config", json=CONFIG)
    assert r.status_code == 200
    return client


def test_dashboard_sin_config_da_404(client):
    r = client.get("/api/dashboard")
    assert r.status_code == 404


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_config_calcula_presupuesto_diario(configurado):
    d = configurado.get("/api/dashboard").json()
    assert d["presupuesto_diario"] == pytest.approx(250_000 / 30, abs=0.01)
    assert d["dias_restantes"] == 30
    assert d["dias_totales_ciclo"] == 30
    assert d["inicio_ciclo"] == "2026-09-01"
    assert d["fin_ciclo"] == "2026-09-30"
    assert d["estado"] == "bien"
    assert len(d["gastos_fijos"]) == 2


def test_gasto_resta_hoy_y_se_reparte_desde_manana(configurado, fijar_hoy):
    d = configurado.post("/api/gastos", json={"monto": 3_000}).json()
    assert d["gastado_hoy"] == 3_000
    assert d["presupuesto_diario"] == pytest.approx(250_000 / 30 - 3_000, abs=0.01)
    assert d["saldo_disponible_ciclo"] == 247_000

    fijar_hoy(date(2026, 9, 2))
    d = configurado.get("/api/dashboard").json()
    assert d["gastado_hoy"] == 0
    assert d["presupuesto_diario"] == pytest.approx(247_000 / 29, abs=0.01)


def test_gastar_de_mas_pone_estado_critico_sin_bloquear(configurado, fijar_hoy):
    d = configurado.post("/api/gastos", json={"monto": 20_000}).json()
    assert d["presupuesto_diario"] < 0
    assert d["estado"] == "critico"

    # Al día siguiente el excedente ya está repartido en los 29 días que quedan.
    fijar_hoy(date(2026, 9, 2))
    d = configurado.get("/api/dashboard").json()
    assert d["presupuesto_diario"] == pytest.approx(230_000 / 29, abs=0.01)
    assert d["estado"] == "bien"


def test_estado_alerta_debajo_de_la_mitad_del_promedio(configurado):
    # 8.333 - 5.000 = 3.333, menos de la mitad de 8.333.
    d = configurado.post("/api/gastos", json={"monto": 5_000}).json()
    assert d["estado"] == "alerta"


def test_editar_y_borrar_gasto(configurado):
    d = configurado.post("/api/gastos", json={"monto": 3_000, "descripcion": "Café"}).json()
    gasto_id = d["gastos_ciclo"][0]["id"]

    d = configurado.put(f"/api/gastos/{gasto_id}", json={"monto": 1_000, "descripcion": "Café"}).json()
    assert d["gastado_hoy"] == 1_000

    d = configurado.delete(f"/api/gastos/{gasto_id}").json()
    assert d["gastado_hoy"] == 0
    assert d["gastos_ciclo"] == []

    assert configurado.delete(f"/api/gastos/{gasto_id}").status_code == 404


def test_ingreso_extra_suma_al_presupuesto(configurado):
    d = configurado.post("/api/ingresos", json={"monto": 30_000, "descripcion": "Changa"}).json()
    assert d["ingresos_variables_ciclo"] == 30_000
    assert d["presupuesto_diario"] == pytest.approx(280_000 / 30, abs=0.01)

    ingreso_id = d["ingresos_variables"][0]["id"]
    d = configurado.delete(f"/api/ingresos/{ingreso_id}").json()
    assert d["presupuesto_diario"] == pytest.approx(250_000 / 30, abs=0.01)


def test_ingreso_sin_config_da_404(client):
    assert client.post("/api/ingresos", json={"monto": 1_000}).status_code == 404


def test_guardar_config_dos_veces_actualiza_sin_duplicar(configurado, db):
    nueva = {**CONFIG, "ingresos_mensuales": 500_000, "gastos_fijos": [CONFIG["gastos_fijos"][0]]}
    d = configurado.post("/api/config", json=nueva).json()
    assert d["ingresos_mensuales"] == 500_000
    assert len(d["gastos_fijos"]) == 1
    assert db.query(models.ConfiguracionMensual).count() == 1
    assert db.query(models.GastoFijo).count() == 1  # los gastos fijos viejos se borran


def test_ciclo_nuevo_hereda_la_config_anterior(configurado, fijar_hoy, db):
    configurado.post("/api/gastos", json={"monto": 3_000})

    fijar_hoy(date(2026, 10, 2))
    r = configurado.get("/api/dashboard")
    assert r.status_code == 200
    d = r.json()
    assert d["inicio_ciclo"] == "2026-10-01"
    assert d["ingresos_mensuales"] == 400_000
    assert d["meta_ahorro"] == 50_000
    assert [g["nombre"] for g in d["gastos_fijos"]] == ["Alquiler", "Internet"]
    assert d["gastos_ciclo"] == []  # los gastos de septiembre no cuentan
    assert d["dias_restantes"] == 30  # del 2 al 31 de octubre
    assert d["presupuesto_diario"] == pytest.approx(250_000 / 30, abs=0.01)

    # Pedir el dashboard otra vez no crea otra config.
    configurado.get("/api/dashboard")
    assert db.query(models.ConfiguracionMensual).count() == 2


def test_ciclo_nuevo_permite_cargar_ingreso_directo(configurado, fijar_hoy):
    fijar_hoy(date(2026, 10, 2))
    r = configurado.post("/api/ingresos", json={"monto": 10_000})
    assert r.status_code == 200
    assert r.json()["ingresos_variables_ciclo"] == 10_000


@pytest.mark.parametrize("monto", [0, -500])
@pytest.mark.parametrize("ruta", ["/api/gastos", "/api/ingresos"])
def test_montos_no_positivos_dan_422(configurado, ruta, monto):
    assert configurado.post(ruta, json={"monto": monto}).status_code == 422


@pytest.mark.parametrize(
    "cambio",
    [
        {"ingresos_mensuales": 0},
        {"dia_cobro": 0},
        {"dia_cobro": 32},
        {"meta_ahorro": -1},
        {"gastos_fijos": [{"nombre": "", "monto": 100}]},
        {"gastos_fijos": [{"nombre": "Luz", "monto": 0}]},
    ],
)
def test_config_invalida_da_422(client, cambio):
    assert client.post("/api/config", json={**CONFIG, **cambio}).status_code == 422
