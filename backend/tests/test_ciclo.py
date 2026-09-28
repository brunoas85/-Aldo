from datetime import date

import pytest

from app.logic import calcular_ciclo


@pytest.mark.parametrize(
    ("hoy", "dia_cobro", "esperado"),
    [
        # Cobro el 1: el ciclo es el mes calendario.
        (date(2026, 9, 28), 1, (date(2026, 9, 1), date(2026, 9, 30))),
        (date(2026, 9, 1), 1, (date(2026, 9, 1), date(2026, 9, 30))),
        # Cobro a mitad de mes, antes y después del día de cobro.
        (date(2026, 9, 28), 25, (date(2026, 9, 25), date(2026, 10, 24))),
        (date(2026, 9, 10), 25, (date(2026, 8, 25), date(2026, 9, 24))),
        (date(2026, 9, 24), 25, (date(2026, 8, 25), date(2026, 9, 24))),
        # Cambio de año, para los dos lados.
        (date(2026, 12, 20), 15, (date(2026, 12, 15), date(2027, 1, 14))),
        (date(2027, 1, 10), 15, (date(2026, 12, 15), date(2027, 1, 14))),
        # Cobro el 31: en meses cortos se cobra el último día.
        (date(2026, 2, 15), 31, (date(2026, 1, 31), date(2026, 2, 27))),
        (date(2026, 2, 28), 31, (date(2026, 2, 28), date(2026, 3, 30))),
        (date(2028, 2, 29), 31, (date(2028, 2, 29), date(2028, 3, 30))),  # bisiesto
        (date(2026, 4, 30), 31, (date(2026, 4, 30), date(2026, 5, 30))),
    ],
)
def test_calcular_ciclo(hoy, dia_cobro, esperado):
    assert calcular_ciclo(hoy, dia_cobro) == esperado


@pytest.mark.parametrize(("dia_cobro", "equivalente"), [(0, 1), (-3, 1), (40, 31)])
def test_calcular_ciclo_acota_dia_invalido(dia_cobro, equivalente):
    hoy = date(2026, 9, 15)
    assert calcular_ciclo(hoy, dia_cobro) == calcular_ciclo(hoy, equivalente)


def test_hoy_siempre_cae_dentro_del_ciclo():
    """Barrido de dos años con todos los días de cobro: hoy siempre está en [inicio, fin]
    y el ciclo dura entre 28 y 31 días."""
    hoy = date(2026, 1, 1)
    while hoy < date(2028, 1, 1):
        for dia_cobro in range(1, 32):
            inicio, fin = calcular_ciclo(hoy, dia_cobro)
            assert inicio <= hoy <= fin
            assert 28 <= (fin - inicio).days + 1 <= 31
        hoy = date.fromordinal(hoy.toordinal() + 1)
