"""Categoría opcional en los gastos del día (Súper, Panadería...) para el resumen del ciclo

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-01
"""
import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("transacciones_diarias", sa.Column("categoria", sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table("transacciones_diarias") as batch:
        batch.drop_column("categoria")
