from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import dashboard_o_404, get_db, get_hoy, get_usuario_actual
from ..logic import calcular_ciclo, obtener_config_actual

router = APIRouter(prefix="/api/config", tags=["config"])


@router.post("", response_model=schemas.DashboardOut)
def guardar_config(
    payload: schemas.ConfigIn,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_actual),
    hoy: date = Depends(get_hoy),
):
    usuario.dia_cobro = payload.dia_cobro

    inicio, _fin = calcular_ciclo(hoy, usuario.dia_cobro)

    config = obtener_config_actual(db, usuario, hoy)
    if config is None:
        config = models.ConfiguracionMensual(
            usuario_id=usuario.id, anio=inicio.year, mes=inicio.month
        )
        db.add(config)

    config.ingresos_mensuales = payload.ingresos_mensuales
    config.meta_ahorro = payload.meta_ahorro
    config.gastos_fijos_detalle = [
        models.GastoFijo(nombre=g.nombre, monto=g.monto, categoria=g.categoria)
        for g in payload.gastos_fijos
    ]
    db.commit()

    return dashboard_o_404(db, usuario, hoy)
