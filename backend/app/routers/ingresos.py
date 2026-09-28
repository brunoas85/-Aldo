from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_usuario_actual
from ..logic import asegurar_config_actual, calcular_dashboard

router = APIRouter(prefix="/api/ingresos", tags=["ingresos"])


def _dashboard_o_404(db: Session, usuario: models.Usuario) -> dict:
    resultado = calcular_dashboard(db, usuario)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Todavía no configuraste tu mes")
    return resultado


def _obtener_ingreso_del_usuario(db: Session, ingreso_id: int, usuario: models.Usuario) -> models.IngresoVariable:
    ingreso = (
        db.query(models.IngresoVariable)
        .join(models.ConfiguracionMensual)
        .filter(
            models.IngresoVariable.id == ingreso_id,
            models.ConfiguracionMensual.usuario_id == usuario.id,
        )
        .first()
    )
    if ingreso is None:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
    return ingreso


@router.post("", response_model=schemas.DashboardOut)
def registrar_ingreso(
    payload: schemas.IngresoIn,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_actual),
):
    hoy = date.today()
    config = asegurar_config_actual(db, usuario, hoy)
    if config is None:
        raise HTTPException(status_code=404, detail="Todavía no configuraste tu mes")

    ingreso = models.IngresoVariable(
        configuracion_id=config.id,
        fecha=hoy,
        monto=payload.monto,
        descripcion=payload.descripcion,
    )
    db.add(ingreso)
    db.commit()

    return _dashboard_o_404(db, usuario)


@router.put("/{ingreso_id}", response_model=schemas.DashboardOut)
def editar_ingreso(
    ingreso_id: int,
    payload: schemas.IngresoIn,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_actual),
):
    ingreso = _obtener_ingreso_del_usuario(db, ingreso_id, usuario)
    ingreso.monto = payload.monto
    ingreso.descripcion = payload.descripcion
    db.commit()

    return _dashboard_o_404(db, usuario)


@router.delete("/{ingreso_id}", response_model=schemas.DashboardOut)
def borrar_ingreso(
    ingreso_id: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_actual),
):
    ingreso = _obtener_ingreso_del_usuario(db, ingreso_id, usuario)
    db.delete(ingreso)
    db.commit()

    return _dashboard_o_404(db, usuario)
