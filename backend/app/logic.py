import calendar
import random
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models

NOMBRES_DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

MENSAJES_MANGO = [
    "Vas bien, seguí así.",
    "Los gastos chiquitos suman: fijate cuánto te llevaron esta semana las compras de menos de $2.000.",
    "Anotar cada gasto ya es la mitad del trabajo. La otra mitad la hago yo.",
    "Si esta semana te sobró un poco, es un buen momento para sumarlo a tu meta de ahorro.",
    "Revisá tus suscripciones cada tanto: es fácil pagar por algo que ya no usás.",
    "Comparar precios antes de una compra grande te puede ahorrar más que un mes de café.",
    "Un gasto fijo que baja es un presupuesto diario que sube. Vale la pena renegociar de vez en cuando.",
    "No hace falta ser perfecto con la plata, solo tener una idea de por dónde se va.",
]


def _fecha_cobro(anio: int, mes: int, dia_cobro: int) -> date:
    _, dias_mes = calendar.monthrange(anio, mes)
    return date(anio, mes, min(dia_cobro, dias_mes))


def calcular_ciclo(hoy: date, dia_cobro: int) -> tuple[date, date]:
    """Devuelve (inicio, fin) del ciclo de facturación que contiene a `hoy`,
    arrancando cada mes en `dia_cobro` (con clamp para meses cortos)."""
    dia_cobro = max(1, min(dia_cobro, 31))
    inicio_este_mes = _fecha_cobro(hoy.year, hoy.month, dia_cobro)

    if hoy >= inicio_este_mes:
        inicio = inicio_este_mes
        mes_sig = hoy.month % 12 + 1
        anio_sig = hoy.year + (1 if hoy.month == 12 else 0)
        fin = _fecha_cobro(anio_sig, mes_sig, dia_cobro) - timedelta(days=1)
    else:
        mes_ant = 12 if hoy.month == 1 else hoy.month - 1
        anio_ant = hoy.year - 1 if hoy.month == 1 else hoy.year
        inicio = _fecha_cobro(anio_ant, mes_ant, dia_cobro)
        fin = inicio_este_mes - timedelta(days=1)

    return inicio, fin


def obtener_config_actual(db: Session, usuario: models.Usuario, hoy: date | None = None):
    hoy = hoy or date.today()
    inicio, _fin = calcular_ciclo(hoy, usuario.dia_cobro)
    return (
        db.query(models.ConfiguracionMensual)
        .filter_by(usuario_id=usuario.id, anio=inicio.year, mes=inicio.month)
        .first()
    )


def asegurar_config_actual(db: Session, usuario: models.Usuario, hoy: date | None = None):
    """Devuelve la config del ciclo actual. Si arrancó un ciclo nuevo y todavía no hay
    config, hereda la del último ciclo configurado (ingresos, meta y gastos fijos) para
    no obligar al usuario a cargar todo de nuevo. Devuelve None si nunca configuró nada."""
    hoy = hoy or date.today()
    config = obtener_config_actual(db, usuario, hoy)
    if config is not None:
        return config

    anterior = (
        db.query(models.ConfiguracionMensual)
        .filter_by(usuario_id=usuario.id)
        .order_by(models.ConfiguracionMensual.anio.desc(), models.ConfiguracionMensual.mes.desc())
        .first()
    )
    if anterior is None:
        return None

    inicio, _fin = calcular_ciclo(hoy, usuario.dia_cobro)
    config = models.ConfiguracionMensual(
        usuario_id=usuario.id,
        anio=inicio.year,
        mes=inicio.month,
        ingresos_mensuales=anterior.ingresos_mensuales,
        meta_ahorro=anterior.meta_ahorro,
        gastos_fijos_detalle=[
            models.GastoFijo(nombre=g.nombre, monto=g.monto, categoria=g.categoria)
            for g in anterior.gastos_fijos_detalle
        ],
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def generar_sugerencias(
    hoy: date,
    dias_transcurridos: int,
    dias_restantes: int,
    gastado_en_ciclo: float,
    pool_disponible: float,
    gastos_fijos_detalle: list[models.GastoFijo],
    ingresos_mensuales: float,
    gastos_ciclo: list[models.TransaccionDiaria],
) -> list[str]:
    sugerencias: list[str] = []

    ritmo_diario = gastado_en_ciclo / dias_transcurridos if dias_transcurridos else 0
    if ritmo_diario > 0:
        dias_que_alcanzan = pool_disponible / ritmo_diario
        dias_antes = dias_restantes - dias_que_alcanzan
        if dias_que_alcanzan < dias_restantes and dias_antes >= 1:
            fecha_quiebre = hoy + timedelta(days=max(int(dias_que_alcanzan), 0))
            sugerencias.append(
                f"Si seguís gastando a este ritmo, se te acaba la plata el "
                f"{fecha_quiebre.strftime('%d/%m')}, unos {dias_antes:.0f} días antes de que termine el ciclo."
            )

    if len(gastos_ciclo) >= 5:
        por_dia = defaultdict(list)
        for g in gastos_ciclo:
            por_dia[g.fecha.weekday()].append(g.monto)
        promedios = {dia: sum(montos) / len(montos) for dia, montos in por_dia.items()}
        promedio_general = sum(g.monto for g in gastos_ciclo) / len(gastos_ciclo)
        dia_max = max(promedios, key=promedios.get)
        if promedios[dia_max] > promedio_general * 1.3:
            sugerencias.append(
                f"Los {NOMBRES_DIAS[dia_max]} solés gastar más que en el resto de la semana "
                f"(promedio ${promedios[dia_max]:.0f})."
            )

    if gastos_fijos_detalle and ingresos_mensuales > 0:
        mayor = max(gastos_fijos_detalle, key=lambda g: g.monto)
        pct = mayor.monto / ingresos_mensuales * 100
        if pct >= 30:
            sugerencias.append(
                f"'{mayor.nombre}' se lleva el {pct:.0f}% de tus ingresos. Si podés renegociarlo "
                f"o buscar una alternativa más barata, es donde más impacto vas a tener."
            )

    if len(sugerencias) < 3:
        mensaje_del_dia = random.Random(hoy.isoformat()).choice(MENSAJES_MANGO)
        sugerencias.append(mensaje_del_dia)

    return sugerencias[:3]


def calcular_dashboard(db: Session, usuario: models.Usuario, hoy: date | None = None) -> dict | None:
    hoy = hoy or date.today()
    config = asegurar_config_actual(db, usuario, hoy)
    if config is None:
        return None

    inicio, fin = calcular_ciclo(hoy, usuario.dia_cobro)
    dias_totales_ciclo = (fin - inicio).days + 1
    dias_restantes = (fin - hoy).days + 1
    dias_transcurridos = (hoy - inicio).days + 1

    gastos_fijos_total = sum(g.monto for g in config.gastos_fijos_detalle)
    ingresos_variables_ciclo = sum(i.monto for i in config.ingresos_variables)

    gastos_ciclo = (
        db.query(models.TransaccionDiaria)
        .filter(
            models.TransaccionDiaria.usuario_id == usuario.id,
            models.TransaccionDiaria.fecha >= inicio,
            models.TransaccionDiaria.fecha <= fin,
        )
        .order_by(models.TransaccionDiaria.fecha.desc(), models.TransaccionDiaria.id.desc())
        .all()
    )
    gastado_en_ciclo = sum(g.monto for g in gastos_ciclo)
    gastado_hoy = sum(g.monto for g in gastos_ciclo if g.fecha == hoy)

    pool_disponible = (
        config.ingresos_mensuales
        + ingresos_variables_ciclo
        - gastos_fijos_total
        - config.meta_ahorro
        - gastado_en_ciclo
    )

    # El presupuesto diario es lo que te toca gastar HOY: la parte del pool que te
    # tocaba antes de gastar nada hoy, menos lo que ya gastaste hoy. Puede ir negativo
    # si te pasaste — el resto de días recién se ajusta a partir de mañana.
    pool_al_inicio_de_hoy = pool_disponible + gastado_hoy
    presupuesto_diario = pool_al_inicio_de_hoy / dias_restantes - gastado_hoy

    promedio_base = (
        config.ingresos_mensuales + ingresos_variables_ciclo - gastos_fijos_total - config.meta_ahorro
    ) / dias_totales_ciclo

    if presupuesto_diario < 0:
        estado = "critico"
    elif presupuesto_diario < promedio_base * 0.5:
        estado = "alerta"
    else:
        estado = "bien"

    sugerencias = generar_sugerencias(
        hoy,
        dias_transcurridos,
        dias_restantes,
        gastado_en_ciclo,
        pool_disponible,
        config.gastos_fijos_detalle,
        config.ingresos_mensuales,
        gastos_ciclo,
    )

    return {
        "nombre": usuario.nombre,
        "presupuesto_diario": round(presupuesto_diario, 2),
        "dias_restantes": dias_restantes,
        "dias_totales_ciclo": dias_totales_ciclo,
        "inicio_ciclo": inicio,
        "fin_ciclo": fin,
        "estado": estado,
        "gastado_hoy": round(gastado_hoy, 2),
        "dia_cobro": usuario.dia_cobro,
        "ingresos_mensuales": config.ingresos_mensuales,
        "meta_ahorro": config.meta_ahorro,
        "gastos_fijos": config.gastos_fijos_detalle,
        "ingresos_variables_ciclo": round(ingresos_variables_ciclo, 2),
        "ingresos_variables": config.ingresos_variables,
        "gastos_ciclo": gastos_ciclo,
        "saldo_disponible_ciclo": round(pool_disponible, 2),
        "sugerencias": sugerencias,
    }
