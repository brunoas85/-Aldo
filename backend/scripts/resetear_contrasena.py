"""Le pone una contraseña nueva a una cuenta (para cuando alguien se la olvida).

Uso (desde backend/, con el venv activado):

    python -m scripts.resetear_contrasena --email alguien@gmail.com   # pide la URL y la contraseña sin mostrarlas

Las sesiones abiertas siguen valiendo hasta que vencen.
"""

import argparse
import getpass
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models
from app.auth import hashear_password
from app.database import normalizar_url

LARGO_MINIMO = 8


class ErrorReseteo(Exception):
    pass


def resetear(url: str, email: str, password: str) -> None:
    if len(password) < LARGO_MINIMO:
        raise ErrorReseteo(f"La contraseña tiene que tener al menos {LARGO_MINIMO} caracteres.")
    engine = create_engine(normalizar_url(url))
    with Session(engine) as db, db.begin():
        usuario = db.query(models.Usuario).filter_by(email=email.strip().lower()).one_or_none()
        if usuario is None:
            raise ErrorReseteo(f"No hay ningún usuario registrado con {email}.")
        usuario.password_hash = hashear_password(password)


def main():
    parser = argparse.ArgumentParser(description="Le pone una contraseña nueva a una cuenta.")
    parser.add_argument("--email", required=True, help="email de la cuenta")
    args = parser.parse_args()

    url = getpass.getpass("URL de la base (postgresql://...): ").strip()
    password = getpass.getpass("Contraseña nueva: ")
    if getpass.getpass("Repetila: ") != password:
        print("No hice nada: las contraseñas no coinciden.")
        sys.exit(1)
    try:
        resetear(url, args.email, password)
    except ErrorReseteo as e:
        print(f"No hice nada: {e}")
        sys.exit(1)
    print(f"Listo: {args.email} ya puede entrar con la contraseña nueva.")


if __name__ == "__main__":
    main()
