"""Login con Google: cada usuario queda identificado por su cuenta de Google

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-30
"""
import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    # Nullable: el usuario que ya existía (id=1) no tiene cuenta asociada hasta su primer login.
    op.add_column("usuarios", sa.Column("google_sub", sa.String(), nullable=True))
    op.add_column("usuarios", sa.Column("email", sa.String(), nullable=True))
    op.create_index("uq_usuarios_google_sub", "usuarios", ["google_sub"], unique=True)


def downgrade():
    op.drop_index("uq_usuarios_google_sub", table_name="usuarios")
    with op.batch_alter_table("usuarios") as batch:
        batch.drop_column("email")
        batch.drop_column("google_sub")
