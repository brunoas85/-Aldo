from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_usuario_actual
from ..logic import calcular_dashboard

router = APIRouter(prefix="/api/gastos", tags=["gastos"])


def _dashboard_o_404(db: Session, usuario: models.Usuario) -> dict:
    resultado = calcular_dashboard(db, usuario)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Todavía no configuraste tu mes")
    return resultado


def _obtener_gasto_del_usuario(db: Session, gasto_id: int, usuario: models.Usuario) -> models.TransaccionDiaria:
    gasto = (
        db.query(models.TransaccionDiaria)
        .filter(models.TransaccionDiaria.id == gasto_id, models.TransaccionDiaria.usuario_id == usuario.id)
        .first()
    )
    if gasto is None:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return gasto


@router.post("", response_model=schemas.DashboardOut)
def registrar_gasto(
    payload: schemas.GastoIn,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_actual),
):
    hoy = date.today()
    gasto = models.TransaccionDiaria(
        usuario_id=usuario.id,
        fecha=hoy,
        monto=payload.monto,
        descripcion=payload.descripcion,
    )
    db.add(gasto)
    db.commit()

    return _dashboard_o_404(db, usuario)


@router.put("/{gasto_id}", response_model=schemas.DashboardOut)
def editar_gasto(
    gasto_id: int,
    payload: schemas.GastoIn,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_actual),
):
    gasto = _obtener_gasto_del_usuario(db, gasto_id, usuario)
    gasto.monto = payload.monto
    gasto.descripcion = payload.descripcion
    db.commit()

    return _dashboard_o_404(db, usuario)


@router.delete("/{gasto_id}", response_model=schemas.DashboardOut)
def borrar_gasto(
    gasto_id: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_actual),
):
    gasto = _obtener_gasto_del_usuario(db, gasto_id, usuario)
    db.delete(gasto)
    db.commit()

    return _dashboard_o_404(db, usuario)
