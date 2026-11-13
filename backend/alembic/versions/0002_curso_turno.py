"""Replace course activity flag with its offered shift."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "curso",
        sa.Column("turno", sa.String(), nullable=False, server_default="integral"),
    )
    op.drop_column("curso", "ativo")


def downgrade() -> None:
    op.add_column(
        "curso",
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.drop_column("curso", "turno")
