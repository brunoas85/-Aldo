"""Una sola ConfiguracionMensual por usuario y ciclo

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-28
"""
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "uq_config_usuario_ciclo",
        "configuraciones_mensuales",
        ["usuario_id", "anio", "mes"],
        unique=True,
    )


def downgrade():
    op.drop_index("uq_config_usuario_ciclo", table_name="configuraciones_mensuales")
