"""Login con Google y sesiones propias.

El frontend obtiene un ID token de Google (botón "Entrar con Google") y lo manda a
/api/auth/google. Acá se verifica la firma contra las claves públicas de Google y, si
está todo bien, se devuelve un token de sesión nuestro (JWT firmado con MANGO_SECRET)
que el frontend manda en cada request como "Authorization: Bearer <token>".
"""

import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

DURACION_SESION = timedelta(days=60)
EMISORES_GOOGLE = ("accounts.google.com", "https://accounts.google.com")
# Tolerancia para relojes desfasados: si el del server atrasa, el token de Google
# parece emitido "en el futuro" y se rechazaría sin este margen.
MARGEN_RELOJ = timedelta(minutes=5)

log = logging.getLogger(__name__)

# Sin MANGO_SECRET (desarrollo local) se usa una clave al azar: las sesiones valen
# hasta que se reinicia el server. En producción Render la genera (render.yaml).
_SECRETO_TEMPORAL = secrets.token_urlsafe(32)
_claves_google = jwt.PyJWKClient("https://www.googleapis.com/oauth2/v3/certs", cache_keys=True)


class ErrorAuth(Exception):
    pass


def _secreto() -> str:
    return os.environ.get("MANGO_SECRET") or _SECRETO_TEMPORAL


def verificar_token_google(credential: str) -> dict:
    """Devuelve los datos de la cuenta (sub, email, given_name...) o lanza ErrorAuth."""
    client_id = os.environ.get("MANGO_GOOGLE_CLIENT_ID")
    if not client_id:
        raise ErrorAuth("El server no tiene configurado MANGO_GOOGLE_CLIENT_ID")
    try:
        clave = _claves_google.get_signing_key_from_jwt(credential)
        datos = jwt.decode(
            credential, clave.key, algorithms=["RS256"], audience=client_id, leeway=MARGEN_RELOJ
        )
    except jwt.PyJWTError as e:
        log.warning("Login de Google rechazado: %s: %s", type(e).__name__, e)
        raise ErrorAuth("El login de Google no es válido") from e
    if datos.get("iss") not in EMISORES_GOOGLE or not datos.get("email_verified"):
        raise ErrorAuth("El login de Google no es válido")
    return datos


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
