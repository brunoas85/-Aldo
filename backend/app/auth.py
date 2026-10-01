"""Login con email y contraseña, y sesiones propias.

La contraseña se guarda hasheada con scrypt (librería estándar, salt al azar por usuario).
Al registrarse o entrar se devuelve un token de sesión (JWT firmado con MANGO_SECRET)
que el frontend manda en cada request como "Authorization: Bearer <token>".
"""

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

DURACION_SESION = timedelta(days=60)

# Parámetros de scrypt: ~16 MB de memoria y unas decenas de ms por intento.
_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2**14, 8, 1

# Sin MANGO_SECRET (desarrollo local) se usa una clave al azar: las sesiones valen
# hasta que se reinicia el server. En producción Render la genera (render.yaml).
_SECRETO_TEMPORAL = secrets.token_urlsafe(32)


def _secreto() -> str:
    return os.environ.get("MANGO_SECRET") or _SECRETO_TEMPORAL


def _b64(datos: bytes) -> str:
    return base64.b64encode(datos).decode()


def hashear_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    hash_ = hashlib.scrypt(password.encode(), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P)
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${_b64(salt)}${_b64(hash_)}"


def verificar_password(password: str, guardado: str | None) -> bool:
    try:
        algoritmo, n, r, p, salt, hash_ = (guardado or "").split("$")
        if algoritmo != "scrypt":
            return False
        calculado = hashlib.scrypt(
            password.encode(), salt=base64.b64decode(salt), n=int(n), r=int(r), p=int(p)
        )
    except ValueError:
        return False
    return hmac.compare_digest(calculado, base64.b64decode(hash_))


def crear_sesion(usuario_id: int) -> str:
    ahora = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": str(usuario_id), "iat": ahora, "exp": ahora + DURACION_SESION},
        _secreto(),
        algorithm="HS256",
    )


def leer_sesion(token: str) -> int | None:
    """Id del usuario de la sesión, o None si el token no sirve o venció."""
    try:
        return int(jwt.decode(token, _secreto(), algorithms=["HS256"])["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
