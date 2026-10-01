from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import dashboard_o_404, get_db, get_hoy, get_usuario_actual

router = APIRouter(prefix="/api/gastos", tags=["gastos"])


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
    hoy: date = Depends(get_hoy),
):
    gasto = models.TransaccionDiaria(
        usuario_id=usuario.id,
        fecha=hoy,
        monto=payload.monto,
        descripcion=payload.descripcion,
        categoria=payload.categoria,
    )
    db.add(gasto)
    db.commit()

    return dashboard_o_404(db, usuario, hoy)


@router.put("/{gasto_id}", response_model=schemas.DashboardOut)
def editar_gasto(
    gasto_id: int,
    payload: schemas.GastoIn,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_actual),
    hoy: date = Depends(get_hoy),
):
    gasto = _obtener_gasto_del_usuario(db, gasto_id, usuario)
    gasto.monto = payload.monto
    gasto.descripcion = payload.descripcion
    if "categoria" in payload.model_fields_set:
        gasto.categoria = payload.categoria
    db.commit()

    return dashboard_o_404(db, usuario, hoy)


@router.delete("/{gasto_id}", response_model=schemas.DashboardOut)
def borrar_gasto(
    gasto_id: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_actual),
    hoy: date = Depends(get_hoy),
):
    gasto = _obtener_gasto_del_usuario(db, gasto_id, usuario)
    db.delete(gasto)
    db.commit()

    return dashboard_o_404(db, usuario, hoy)
