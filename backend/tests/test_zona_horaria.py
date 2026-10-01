from datetime import date, datetime, timezone

import pytest

from app import deps

CONFIG = {"ingresos_mensuales": 300_000, "dia_cobro": 1, "meta_ahorro": 0, "gastos_fijos": []}


@pytest.fixture
def son_las(monkeypatch):
    """Fija la hora UTC del server: son_las(datetime(2026, 10, 2, 1, 30))."""

    def _fijar(momento: datetime):
        monkeypatch.setattr(deps, "_ahora_utc", lambda: momento.replace(tzinfo=timezone.utc))

    return _fijar


@pytest.mark.parametrize(
    "zona,esperado",
    [
        # 01:30 UTC del 2 de octubre son las 22:30 del 1 en Argentina.
        ("America/Argentina/Buenos_Aires", date(2026, 10, 1)),
        ("Europe/Madrid", date(2026, 10, 2)),
        (None, date(2026, 10, 1)),
        ("Zona/Inventada", date(2026, 10, 1)),
        ("../../etc/passwd", date(2026, 10, 1)),
        ("", date(2026, 10, 1)),
    ],
)
def test_hoy_segun_la_zona_del_usuario(son_las, zona, esperado):
    son_las(datetime(2026, 10, 2, 1, 30))
    assert deps.get_hoy(zona) == esperado


def test_un_gasto_a_la_noche_cuenta_para_ese_dia(client, son_las):
    son_las(datetime(2026, 10, 1, 12, 0))
    client.post("/api/config", json=CONFIG)
    son_las(datetime(2026, 10, 2, 1, 30))  # 22:30 del 1 en Argentina

    d = client.post("/api/gastos", json={"monto": 1_000}, headers={"X-Zona-Horaria": "America/Argentina/Buenos_Aires"})

    assert d.json()["gastos_ciclo"][0]["fecha"] == "2026-10-01"
    assert d.json()["gastado_hoy"] == 1_000
