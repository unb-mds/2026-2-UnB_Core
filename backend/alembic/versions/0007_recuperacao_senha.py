"""Add password recovery fields to users.

- recuperacao_senha_solicitada_em: when the user asked for a new password on the login page;
- contato_recuperacao: optional contact the user gave for receiving the temporary password;
- trocar_senha: the user signed in with a temporary password and must set a new one.

Only adds columns; existing users get trocar_senha = false.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007"
down_revision: Union[str, Sequence[str], None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuario",
        sa.Column("recuperacao_senha_solicitada_em", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "usuario",
        sa.Column("contato_recuperacao", sa.String(), nullable=True),
    )
    op.add_column(
        "usuario",
        sa.Column("trocar_senha", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("usuario", "trocar_senha")
    op.drop_column("usuario", "contato_recuperacao")
    op.drop_column("usuario", "recuperacao_senha_solicitada_em")
