from datetime import date

import pytest

from app.resumen import formatear_pesos

CONFIG = {
    "ingresos_mensuales": 500_000,
    "dia_cobro": 1,
    "meta_ahorro": 50_000,
    "gastos_fijos": [{"nombre": "Alquiler", "monto": 200_000}],
}


def _gastar(client, fijar_hoy, dia, monto, categoria=None, mes=9):
    fijar_hoy(date(2026, mes, dia))
    body = {"monto": monto} | ({"categoria": categoria} if categoria else {})
    r = client.post("/api/gastos", json=body)
    assert r.status_code == 200, r.text
    return r.json()


@pytest.fixture
def con_gastos(client, fijar_hoy):
    fijar_hoy(date(2026, 8, 1))
    client.post("/api/config", json=CONFIG)
    _gastar(client, fijar_hoy, 3, 4_000, "Panadería", mes=8)
    _gastar(client, fijar_hoy, 2, 3_000, "Panadería")
    _gastar(client, fijar_hoy, 5, 5_000, "Panadería")
    _gastar(client, fijar_hoy, 6, 20_000, "Súper")
    _gastar(client, fijar_hoy, 7, 1_000)
    fijar_hoy(date(2026, 9, 10))
    return client


def test_gasto_guarda_categoria_y_el_put_la_conserva(client, fijar_hoy):
    fijar_hoy(date(2026, 9, 1))
    client.post("/api/config", json=CONFIG)
    gasto = _gastar(client, fijar_hoy, 1, 2_500, "Panadería")["gastos_ciclo"][0]
    assert gasto["categoria"] == "Panadería"

    d = client.put(f"/api/gastos/{gasto['id']}", json={"monto": 3_000}).json()
    assert d["gastos_ciclo"][0]["categoria"] == "Panadería"
    d = client.put(f"/api/gastos/{gasto['id']}", json={"monto": 3_000, "categoria": "Súper"}).json()
    assert d["gastos_ciclo"][0]["categoria"] == "Súper"
    d = client.put(f"/api/gastos/{gasto['id']}", json={"monto": 3_000, "categoria": None}).json()
    assert d["gastos_ciclo"][0]["categoria"] is None


def test_categoria_invalida_da_422(client, fijar_hoy):
    fijar_hoy(date(2026, 9, 1))
    client.post("/api/config", json=CONFIG)
    assert client.post("/api/gastos", json={"monto": 100, "categoria": "Casino"}).status_code == 422


def test_resumen_por_categoria_contra_el_ciclo_anterior(con_gastos):
    r = con_gastos.get("/api/resumen").json()

    assert r["total_gastado"] == 29_000
    assert r["total_ciclo_anterior"] == 4_000
    assert r["dias_transcurridos"] == 10
    assert [(c["categoria"], c["total"], c["cantidad"], c["total_ciclo_anterior"]) for c in r["categorias"]] == [
        ("Súper", 20_000, 1, 0),
        ("Panadería", 8_000, 2, 4_000),
        ("Sin categoría", 1_000, 1, 0),
    ]
    assert r["aviso"] is None


def test_analisis_marca_lo_que_se_disparo_y_lo_que_mas_pesa(con_gastos):
    analisis = con_gastos.get("/api/resumen").json()["analisis"]

    assert analisis["resumen"].startswith("Llevás $29.000 gastados en 10 días del ciclo, unos $2.900 por día.")
    assert "súper: $20.000, el 69% del total" in analisis["resumen"]
    # Panadería: $800/día contra $4.000 en 31 días (~$129/día) del ciclo anterior.
    panaderia = next(c for c in analisis["consejos"] if "panadería" in c)
    assert panaderia.startswith("Llevás $8.000 en panadería (2 compras): por día, un 520% más que el ciclo pasado.")
    assert any(c.startswith("Súper se lleva el 69%") for c in analisis["consejos"])
    assert len(analisis["consejos"]) <= 4


def test_avisa_cuando_una_categoria_viene_mejor(client, fijar_hoy):
    fijar_hoy(date(2026, 8, 1))
    client.post("/api/config", json=CONFIG)
    _gastar(client, fijar_hoy, 3, 60_000, "Salidas", mes=8)
    for dia in (1, 2, 3):
        _gastar(client, fijar_hoy, dia, 1_000, "Salidas")
    consejos = client.get("/api/resumen").json()["analisis"]["consejos"]
    assert "Bien ahí con salidas: venís gastando menos que el ciclo pasado." in consejos


def test_muchos_gastos_sin_categoria_sugiere_categorizar(client, fijar_hoy):
    fijar_hoy(date(2026, 9, 1))
    client.post("/api/config", json=CONFIG)
    for _ in range(3):
        _gastar(client, fijar_hoy, 1, 1_000)
    consejos = client.get("/api/resumen").json()["analisis"]["consejos"]
    assert consejos[0].startswith("El 100% de lo que gastaste está sin categoría.")


def test_sin_suficientes_gastos_no_hay_analisis(client, fijar_hoy):
    fijar_hoy(date(2026, 9, 1))
    client.post("/api/config", json=CONFIG)
    _gastar(client, fijar_hoy, 1, 500, "Súper")
    r = client.get("/api/resumen").json()
    assert r["analisis"] is None and "algunos gastos más" in r["aviso"]


def test_formato_de_pesos():
    assert formatear_pesos(18_000) == "$18.000"
    assert formatear_pesos(1_234_567.8) == "$1.234.568"


def test_resumen_sin_config_da_404(client):
    assert client.get("/api/resumen").status_code == 404
