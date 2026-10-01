"""Asocia una cuenta a los datos de antes del login (usuario id=1).

Sirve si alguien se registró antes de que MANGO_EMAIL_USUARIO_INICIAL estuviera
bien configurado: el registro le creó un usuario nuevo y vacío. Este script le pasa esa
cuenta (email y contraseña) al usuario id=1 y borra el usuario vacío.

Uso (desde backend/, con el venv activado):

    python -m scripts.asociar_usuario_inicial --email tu@gmail.com   # pide la URL de Neon sin mostrarla

Se niega a hacer nada si el usuario nuevo ya tiene datos cargados, o si el id=1 ya
tiene una cuenta asociada. Todo pasa en una transacción.
"""

import argparse
import getpass
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models
from app.database import normalizar_url


class ErrorAsociacion(Exception):
    pass


def asociar(url: str, email: str) -> None:
    engine = create_engine(normalizar_url(url))
    with Session(engine) as db, db.begin():
        inicial = db.get(models.Usuario, 1)
        if inicial is None:
            raise ErrorAsociacion("No existe el usuario id=1.")
        if inicial.email is not None:
            raise ErrorAsociacion(f"El usuario id=1 ya está asociado a {inicial.email}.")

        nuevo = (
            db.query(models.Usuario)
            .filter(models.Usuario.id != 1, models.Usuario.email.ilike(email.strip()))
            .one_or_none()
        )
        if nuevo is None:
            raise ErrorAsociacion(f"No hay ningún usuario registrado con {email}.")
        if nuevo.configuraciones or nuevo.transacciones:
            raise ErrorAsociacion(
                f"El usuario {nuevo.id} ({nuevo.email}) ya tiene datos cargados; no lo borro."
            )

        email_real, password_hash, nombre = nuevo.email, nuevo.password_hash, nuevo.nombre
        db.delete(nuevo)
        db.flush()  # libera el email (es único) antes de dárselo al id=1
        inicial.email, inicial.password_hash, inicial.nombre = email_real, password_hash, nombre


def main():
    parser = argparse.ArgumentParser(description="Asocia una cuenta a los datos de antes del login.")
    parser.add_argument("--email", required=True, help="email con el que te registraste")
    args = parser.parse_args()

    url = getpass.getpass("URL de la base (postgresql://...): ").strip()
    try:
        asociar(url, args.email)
    except ErrorAsociacion as e:
        print(f"No hice nada: {e}")
        sys.exit(1)
    print("Listo: tus datos de antes quedaron en tu cuenta. Recargá Mango.")


if __name__ == "__main__":
    main()
