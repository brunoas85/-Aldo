from datetime import date

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from . import models
from .auth import leer_sesion
from .database import get_db
from .logic import calcular_dashboard

__all__ = ["get_db", "get_usuario_actual", "get_hoy", "dashboard_o_404"]


def get_usuario_actual(
    authorization: str | None = Header(default=None), db: Session = Depends(get_db)
) -> models.Usuario:
    """Usuario de la sesión (header "Authorization: Bearer <token>"), o 401."""
    esquema, _, token = (authorization or "").partition(" ")
    usuario_id = leer_sesion(token) if esquema.lower() == "bearer" and token else None
    usuario = db.get(models.Usuario, usuario_id) if usuario_id is not None else None
    if usuario is None:
        raise HTTPException(status_code=401, detail="Tenés que iniciar sesión")
    return usuario


def get_hoy() -> date:
    """Fecha de "hoy" para el request. Centralizada acá para poder fijarla en los tests
    y, más adelante, calcularla según la zona horaria del usuario."""
    return date.today()


def dashboard_o_404(db: Session, usuario: models.Usuario, hoy: date) -> dict:
    resultado = calcular_dashboard(db, usuario, hoy)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Todavía no configuraste tu mes")
    return resultado
