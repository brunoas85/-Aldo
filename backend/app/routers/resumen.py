from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_hoy, get_usuario_actual
from ..resumen import calcular_resumen

router = APIRouter(prefix="/api/resumen", tags=["resumen"])


@router.get("", response_model=schemas.ResumenOut)
def obtener_resumen(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_actual),
    hoy: date = Depends(get_hoy),
):
    resumen = calcular_resumen(db, usuario, hoy)
    if resumen is None:
        raise HTTPException(status_code=404, detail="Todavía no configuraste tu mes")
    return resumen
