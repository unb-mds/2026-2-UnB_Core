"""Replace course shift with academic degree."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "curso",
        sa.Column("grau", sa.String(), nullable=False, server_default="Bacharelado"),
    )
    op.drop_column("curso", "turno")


def downgrade() -> None:
    op.add_column(
        "curso",
        sa.Column("turno", sa.String(), nullable=False, server_default="integral"),
    )
    op.drop_column("curso", "grau")
