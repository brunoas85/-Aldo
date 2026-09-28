from datetime import date

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .logic import calcular_dashboard

__all__ = ["get_db", "get_usuario_actual", "get_hoy", "dashboard_o_404"]


def get_usuario_actual(db: Session = Depends(get_db)) -> models.Usuario:
    """MVP de un solo usuario: siempre devuelve (o crea) el usuario id=1."""
    usuario = db.query(models.Usuario).filter_by(id=1).first()
    if usuario is None:
        usuario = models.Usuario(id=1, nombre="Bruno")
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
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
