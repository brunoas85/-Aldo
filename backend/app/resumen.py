"""Resumen del ciclo por categoría y consejos de Mango.

Los consejos salen de reglas fijas: se compara cada categoría con el ritmo del ciclo
anterior y con el peso que tiene en el total, y se arma la frase con un consejo
concreto para esa categoría. Todo se calcula acá: no hay servicios externos.
"""

import random
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy.orm import Session

from . import models
from .logic import asegurar_config_actual, calcular_ciclo
from .schemas import CATEGORIAS_GASTO

SIN_CATEGORIA = "Sin categoría"
MINIMO_GASTOS_PARA_ANALIZAR = 3
MAXIMO_CONSEJOS = 4
# Una categoría "se disparó" si su ritmo diario supera en un 20% al del ciclo anterior,
# o si se lleva al menos un cuarto de lo gastado en el ciclo.
SUBA_NOTABLE = 1.2
PESO_NOTABLE = 0.25

TIPS = {
    "Panadería": [
        "Si hacés pan casero el fin de semana, te ahorrás buena parte.",
        "Comprar el pan por kilo y freezarlo sale bastante menos que ir todos los días.",
        "Las facturas de todos los días suman: probá dejarlas para el finde.",
    ],
    "Comida afuera": [
        "Cocinar de más a la noche y llevarte vianda al otro día te ahorra varias salidas.",
        "Fijate qué días tienen promo tus lugares de siempre y concentrá ahí las salidas a comer.",
        "Un pedido menos por semana ya se nota a fin de mes.",
    ],
    "Súper": [
        "Ir con lista y probar las marcas propias del súper suele bajar el ticket bastante.",
        "Comprar lo que no se vence en un mayorista una vez al mes rinde más que ir seguido.",
        "Aprovechá los días de descuento con tu banco o billetera virtual.",
    ],
    "Transporte": [
        "Revisá si te conviene la bici o compartir viajes en los trayectos de siempre.",
        "Juntar trámites en un mismo viaje te ahorra pasajes y nafta.",
        "Si usás apps de viaje, comparar entre dos antes de pedir suele ahorrar unos pesos.",
    ],
    "Salidas": [
        "Una previa en casa antes de salir baja mucho la cuenta.",
        "Buscá planes gratis o con 2x1 para alguna de las salidas del mes.",
        "Ponete un tope para salidas este ciclo y fijate cuánto te queda antes de cada plan.",
    ],
    "Otros": [
        "Revisá qué estás cargando en 'Otros': a veces ahí se esconden gastos que se pueden recortar.",
    ],
    SIN_CATEGORIA: [
        "Si al cargar tocás una categoría (Súper, Panadería...), te puedo decir mejor dónde ajustar.",
    ],
}


def formatear_pesos(monto: float) -> str:
    return "$" + f"{monto:,.0f}".replace(",", ".")


def _gastos_entre(db: Session, usuario: models.Usuario, inicio: date, fin: date):
    return (
        db.query(models.TransaccionDiaria)
        .filter(
            models.TransaccionDiaria.usuario_id == usuario.id,
            models.TransaccionDiaria.fecha >= inicio,
            models.TransaccionDiaria.fecha <= fin,
        )
        .all()
    )


def _por_categoria(gastos) -> dict[str, tuple[float, int]]:
    totales: dict[str, list] = defaultdict(lambda: [0.0, 0])
    for g in gastos:
        cat = g.categoria if g.categoria in CATEGORIAS_GASTO else SIN_CATEGORIA
        totales[cat][0] += g.monto
        totales[cat][1] += 1
    return {cat: (round(total, 2), cantidad) for cat, (total, cantidad) in totales.items()}


def generar_analisis(
    hoy: date,
    categorias: list[dict],
    total: float,
    total_anterior: float,
    dias_transcurridos: int,
    dias_anterior: int,
) -> dict:
    """Resumen de dos o tres oraciones y hasta MAXIMO_CONSEJOS consejos, en el tono de Mango."""
    ritmo = total / dias_transcurridos
    mayor = max(categorias, key=lambda c: c["total"])
    resumen = [
        f"Llevás {formatear_pesos(total)} gastados en {dias_transcurridos} "
        f"{'día' if dias_transcurridos == 1 else 'días'} del ciclo, unos {formatear_pesos(ritmo)} por día.",
        f"Lo que más se lleva es {mayor['categoria'].lower()}: {formatear_pesos(mayor['total'])}, "
        f"el {mayor['total'] / total:.0%} del total.",
    ]
    if total_anterior > 0:
        variacion = ritmo / (total_anterior / dias_anterior) - 1
        if abs(variacion) < 0.1:
            resumen.append("Venís a un ritmo parecido al del ciclo anterior.")
        else:
            direccion = "más" if variacion > 0 else "menos"
            resumen.append(f"Por día, venís gastando un {abs(variacion):.0%} {direccion} que el ciclo anterior.")

    # Cada consejo con un puntaje: lo que más se disparó o más pesa va primero.
    candidatos: list[tuple[float, str]] = []
    for c in categorias:
        if c["total"] <= 0:
            continue
        cat, peso = c["categoria"], c["total"] / total
        ritmo_ant = c["total_ciclo_anterior"] / dias_anterior
        suba = (c["total"] / dias_transcurridos) / ritmo_ant if ritmo_ant > 0 else None
        tip = random.Random(f"{hoy.isoformat()}-{cat}").choice(TIPS[cat])
        compras = f"{c['cantidad']} {'compra' if c['cantidad'] == 1 else 'compras'}"
        nombre = cat if cat == SIN_CATEGORIA else cat.lower()

        if cat == SIN_CATEGORIA:
            if peso >= PESO_NOTABLE:
                candidatos.append((peso, f"El {peso:.0%} de lo que gastaste está sin categoría. {tip}"))
        elif suba is not None and suba >= SUBA_NOTABLE:
            candidatos.append(
                (
                    suba + peso,
                    f"Llevás {formatear_pesos(c['total'])} en {nombre} ({compras}): por día, "
                    f"un {suba - 1:.0%} más que el ciclo pasado. {tip}",
                )
            )
        elif peso >= PESO_NOTABLE:
            candidatos.append(
                (peso, f"{cat} se lleva el {peso:.0%} de lo que gastaste ({formatear_pesos(c['total'])}). {tip}")
            )

    for c in categorias:
        ritmo_ant = c["total_ciclo_anterior"] / dias_anterior
        if c["categoria"] != SIN_CATEGORIA and ritmo_ant > 0 and c["total"] / dias_transcurridos < ritmo_ant * 0.8:
            candidatos.append(
                (0, f"Bien ahí con {c['categoria'].lower()}: venís gastando menos que el ciclo pasado.")
            )

    consejos = [texto for _, texto in sorted(candidatos, key=lambda x: -x[0])][:MAXIMO_CONSEJOS]
    if not consejos:
        consejos = ["Venís parejo en todas las categorías. Seguí así."]
    return {"resumen": " ".join(resumen), "consejos": consejos}


def calcular_resumen(db: Session, usuario: models.Usuario, hoy: date) -> dict | None:
    config = asegurar_config_actual(db, usuario, hoy)
    if config is None:
        return None

    inicio, fin = calcular_ciclo(hoy, usuario.dia_cobro)
    inicio_ant, fin_ant = calcular_ciclo(inicio - timedelta(days=1), usuario.dia_cobro)
    dias_transcurridos = (hoy - inicio).days + 1

    gastos = _gastos_entre(db, usuario, inicio, fin)
    actual = _por_categoria(gastos)
    anterior = _por_categoria(_gastos_entre(db, usuario, inicio_ant, fin_ant))

    categorias = sorted(
        (
            {
                "categoria": cat,
                "total": actual.get(cat, (0, 0))[0],
                "cantidad": actual.get(cat, (0, 0))[1],
                "total_ciclo_anterior": anterior.get(cat, (0, 0))[0],
            }
            for cat in actual.keys() | anterior.keys()
        ),
        key=lambda c: (-c["total"], -c["total_ciclo_anterior"]),
    )
    total_gastado = round(sum(t for t, _ in actual.values()), 2)
    total_anterior = round(sum(t for t, _ in anterior.values()), 2)

    resumen = {
        "inicio_ciclo": inicio,
        "fin_ciclo": fin,
        "dias_transcurridos": dias_transcurridos,
        "dias_totales_ciclo": (fin - inicio).days + 1,
        "total_gastado": total_gastado,
        "total_ciclo_anterior": total_anterior,
        "categorias": categorias,
        "analisis": None,
        "aviso": None,
    }
    if len(gastos) < MINIMO_GASTOS_PARA_ANALIZAR:
        resumen["aviso"] = "Cargá algunos gastos más este ciclo y te armo el análisis."
    else:
        resumen["analisis"] = generar_analisis(
            hoy, categorias, total_gastado, total_anterior, dias_transcurridos, (fin_ant - inicio_ant).days + 1
        )
    return resumen
