from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import dashboard_o_404, get_db, get_hoy, get_usuario_actual

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=schemas.DashboardOut)
def obtener_dashboard(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_usuario_actual),
    hoy: date = Depends(get_hoy),
):
    return dashboard_o_404(db, usuario, hoy)
