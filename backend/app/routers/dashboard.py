from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_usuario_actual
from ..logic import calcular_dashboard

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=schemas.DashboardOut)
def obtener_dashboard(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_actual),
):
    resultado = calcular_dashboard(db, usuario)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Todavía no configuraste tu mes")
    return resultado
