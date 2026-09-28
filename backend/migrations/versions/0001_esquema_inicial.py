"""Esquema inicial (el que generaba create_all antes de usar Alembic)

Revision ID: 0001
Revises:
Create Date: 2026-09-28
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String()),
        sa.Column("dia_cobro", sa.Integer(), nullable=False),
    )
    op.create_index("ix_usuarios_id", "usuarios", ["id"])

    op.create_table(
        "configuraciones_mensuales",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("ingresos_mensuales", sa.Float(), nullable=False),
        sa.Column("meta_ahorro", sa.Float(), nullable=False),
    )
    op.create_index("ix_configuraciones_mensuales_id", "configuraciones_mensuales", ["id"])

    op.create_table(
        "gastos_fijos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("configuracion_id", sa.Integer(), sa.ForeignKey("configuraciones_mensuales.id"), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("monto", sa.Float(), nullable=False),
        sa.Column("categoria", sa.String()),
    )
    op.create_index("ix_gastos_fijos_id", "gastos_fijos", ["id"])

    op.create_table(
        "ingresos_variables",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("configuracion_id", sa.Integer(), sa.ForeignKey("configuraciones_mensuales.id"), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("monto", sa.Float(), nullable=False),
        sa.Column("descripcion", sa.String()),
    )
    op.create_index("ix_ingresos_variables_id", "ingresos_variables", ["id"])
    op.create_index("ix_ingresos_variables_fecha", "ingresos_variables", ["fecha"])

    op.create_table(
        "transacciones_diarias",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("monto", sa.Float(), nullable=False),
        sa.Column("descripcion", sa.String()),
    )
    op.create_index("ix_transacciones_diarias_id", "transacciones_diarias", ["id"])
    op.create_index("ix_transacciones_diarias_fecha", "transacciones_diarias", ["fecha"])


def downgrade():
    op.drop_table("transacciones_diarias")
    op.drop_table("ingresos_variables")
    op.drop_table("gastos_fijos")
    op.drop_table("configuraciones_mensuales")
    op.drop_table("usuarios")
