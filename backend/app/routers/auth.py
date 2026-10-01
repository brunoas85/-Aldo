import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import crear_sesion, hashear_password, verificar_password
from ..deps import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _sesion(usuario: models.Usuario) -> dict:
    return {"token": crear_sesion(usuario.id), "nombre": usuario.nombre, "email": usuario.email}


def _reclamar_usuario_inicial(db: Session, email: str) -> models.Usuario | None:
    """Los datos de antes del login quedaron en el usuario id=1, sin cuenta asociada.
    Se los queda quien se registre con el email de MANGO_EMAIL_USUARIO_INICIAL."""
    email_inicial = os.environ.get("MANGO_EMAIL_USUARIO_INICIAL", "").strip().lower()
    if not email_inicial or email != email_inicial:
        return None
    return db.query(models.Usuario).filter_by(id=1, email=None).first()


@router.post("/registro", response_model=schemas.SesionOut)
def registrarse(payload: schemas.RegistroIn, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter_by(email=payload.email).first()
    if usuario is not None and usuario.password_hash is not None:
        raise HTTPException(status_code=409, detail="Ya hay una cuenta con ese email. Entrá con tu contraseña.")
    # Sin contraseña = cuenta que venía del login con Google: se queda con sus datos.
    usuario = usuario or _reclamar_usuario_inicial(db, payload.email) or models.Usuario()
    usuario.email = payload.email
    usuario.nombre = payload.nombre
    usuario.password_hash = hashear_password(payload.password)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return _sesion(usuario)


@router.post("/login", response_model=schemas.SesionOut)
def entrar(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter_by(email=payload.email).first()
    if usuario is not None and usuario.password_hash is None:
        raise HTTPException(
            status_code=401,
            detail="Tu cuenta era de Google: registrate con este mismo email para ponerle contraseña.",
        )
    if usuario is None or not verificar_password(payload.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    return _sesion(usuario)
