from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

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


# Si el navegador no manda su zona (o manda una que no existe), se usa la de Argentina.
ZONA_POR_DEFECTO = ZoneInfo("America/Argentina/Buenos_Aires")


def _ahora_utc() -> datetime:
    return datetime.now(timezone.utc)


def _zona(nombre: str | None) -> ZoneInfo:
    if not nombre or len(nombre) > 64:
        return ZONA_POR_DEFECTO
    try:
        return ZoneInfo(nombre)
    except (ZoneInfoNotFoundError, ValueError):
        return ZONA_POR_DEFECTO


def get_hoy(x_zona_horaria: str | None = Header(default=None)) -> date:
    """Fecha de "hoy" para el usuario, según la zona horaria que manda su navegador en el
    header X-Zona-Horaria (ej. "America/Argentina/Buenos_Aires"). El server corre en UTC:
    sin esto, después de las 21 hs de Argentina ya sería "mañana". Centralizada acá para
    poder fijarla en los tests."""
    return _ahora_utc().astimezone(_zona(x_zona_horaria)).date()


def dashboard_o_404(db: Session, usuario: models.Usuario, hoy: date) -> dict:
    resultado = calcular_dashboard(db, usuario, hoy)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Todavía no configuraste tu mes")
    return resultado
