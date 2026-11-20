"""Move discipline course ownership to a many-to-many association."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "curso_disciplina",
        sa.Column("curso_id", sa.Integer(), nullable=False),
        sa.Column("disciplina_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["curso_id"], ["curso.id"]),
        sa.ForeignKeyConstraint(["disciplina_id"], ["disciplina.id"]),
        sa.PrimaryKeyConstraint("curso_id", "disciplina_id"),
    )
    op.create_index(
        "ix_curso_disciplina_curso_id",
        "curso_disciplina",
        ["curso_id"],
    )
    op.create_index(
        "ix_curso_disciplina_disciplina_id",
        "curso_disciplina",
        ["disciplina_id"],
    )
    op.execute(
        sa.text(
            "INSERT INTO curso_disciplina (curso_id, disciplina_id) "
            "SELECT curso_id, id FROM disciplina"
        )
    )
    op.drop_index("ix_disciplina_curso_id", table_name="disciplina")
    op.drop_column("disciplina", "curso_id")


def downgrade() -> None:
    op.add_column(
        "disciplina",
        sa.Column("curso_id", sa.Integer(), nullable=True),
    )
    op.execute(
        sa.text(
            "UPDATE disciplina SET curso_id = ("
            "SELECT curso_id FROM curso_disciplina "
            "WHERE curso_disciplina.disciplina_id = disciplina.id "
            "LIMIT 1)"
        )
    )
    op.alter_column("disciplina", "curso_id", nullable=False)
    op.create_index(
        "ix_disciplina_curso_id",
        "disciplina",
        ["curso_id"],
    )
    op.drop_index(
        "ix_curso_disciplina_disciplina_id",
        table_name="curso_disciplina",
    )
    op.drop_index("ix_curso_disciplina_curso_id", table_name="curso_disciplina")
    op.drop_table("curso_disciplina")
