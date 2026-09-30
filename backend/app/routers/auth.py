import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import ErrorAuth, crear_sesion, verificar_token_google
from ..deps import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _buscar_o_crear_usuario(db: Session, datos: dict) -> models.Usuario:
    usuario = db.query(models.Usuario).filter_by(google_sub=datos["sub"]).first()
    if usuario is None:
        usuario = _reclamar_usuario_inicial(db, datos["email"]) or models.Usuario()
        usuario.google_sub = datos["sub"]
        db.add(usuario)
    usuario.email = datos["email"]
    usuario.nombre = datos.get("given_name") or datos.get("name") or usuario.nombre or "vos"
    db.commit()
    db.refresh(usuario)
    return usuario


def _reclamar_usuario_inicial(db: Session, email: str) -> models.Usuario | None:
    """Los datos de antes del login quedaron en el usuario id=1, sin cuenta asociada.
    Se los queda quien entre con el email de MANGO_EMAIL_USUARIO_INICIAL."""
    email_inicial = os.environ.get("MANGO_EMAIL_USUARIO_INICIAL", "").strip().lower()
    if not email_inicial or email.lower() != email_inicial:
        return None
    return db.query(models.Usuario).filter_by(id=1, google_sub=None).first()


@router.post("/google", response_model=schemas.SesionOut)
def login_con_google(payload: schemas.LoginGoogleIn, db: Session = Depends(get_db)):
    try:
        datos = verificar_token_google(payload.credential)
    except ErrorAuth as e:
        raise HTTPException(status_code=401, detail=str(e)) from e

    usuario = _buscar_o_crear_usuario(db, datos)
    return {"token": crear_sesion(usuario.id), "nombre": usuario.nombre, "email": usuario.email}
