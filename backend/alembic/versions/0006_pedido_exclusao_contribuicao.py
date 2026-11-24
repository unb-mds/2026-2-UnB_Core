"""Add the author's deletion request to contributions.

Two nullable columns, so existing rows are not affected:
- exclusao_solicitada_em: when the author asked to delete a published contribution;
- motivo_exclusao: the reason given by the author.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006"
down_revision: Union[str, Sequence[str], None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "contribuicao",
        sa.Column("exclusao_solicitada_em", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "contribuicao",
        sa.Column("motivo_exclusao", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("contribuicao", "motivo_exclusao")
    op.drop_column("contribuicao", "exclusao_solicitada_em")
