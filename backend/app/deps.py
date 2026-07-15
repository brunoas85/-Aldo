from fastapi import Depends
from sqlalchemy.orm import Session

from . import models
from .database import get_db

__all__ = ["get_db", "get_usuario_actual"]


def get_usuario_actual(db: Session = Depends(get_db)) -> models.Usuario:
    """MVP de un solo usuario: siempre devuelve (o crea) el usuario id=1."""
    usuario = db.query(models.Usuario).filter_by(id=1).first()
    if usuario is None:
        usuario = models.Usuario(id=1, nombre="Bruno")
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
    return usuario
