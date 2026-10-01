"""Login con email y contraseña en vez de Google

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-01
"""
import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    # Los usuarios que venían de Google conservan su email (y sus datos), pero quedan
    # sin contraseña hasta que se registran de nuevo con ese mismo email.
    op.execute("UPDATE usuarios SET email = lower(trim(email)) WHERE email IS NOT NULL")
    op.drop_index("uq_usuarios_google_sub", table_name="usuarios")
    with op.batch_alter_table("usuarios") as batch:
        batch.drop_column("google_sub")
        batch.add_column(sa.Column("password_hash", sa.String(), nullable=True))
    op.create_index("uq_usuarios_email", "usuarios", ["email"], unique=True)


def downgrade():
    op.drop_index("uq_usuarios_email", table_name="usuarios")
    with op.batch_alter_table("usuarios") as batch:
        batch.drop_column("password_hash")
        batch.add_column(sa.Column("google_sub", sa.String(), nullable=True))
    op.create_index("uq_usuarios_google_sub", "usuarios", ["google_sub"], unique=True)
