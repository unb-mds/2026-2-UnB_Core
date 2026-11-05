"""Create the initial application schema.

Revision ID: 0001
Revises:
Create Date: 2026-11-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


tipo_conteudo = postgresql.ENUM(
    "RESUMO",
    "DICA",
    "DIFICULDADE",
    "PROVA",
    "IMPLEMENTACAO",
    "LINK",
    name="tipoconteudo",
    schema="public",
    create_type=False,
)
estado_conteudo = postgresql.ENUM(
    "PUBLICADO",
    "ARQUIVADO",
    name="estadoconteudo",
    schema="public",
    create_type=False,
)
estado_contribuicao = postgresql.ENUM(
    "PENDENTE",
    "AJUSTES",
    "REJEITADA",
    "APROVADA",
    "ARQUIVADA",
    name="estadocontribuicao",
    schema="public",
    create_type=False,
)
perfil_usuario = postgresql.ENUM(
    "USUARIO",
    "MODERADOR",
    "ADMINISTRADOR",
    name="perfilusuario",
    schema="public",
    create_type=False,
)


def upgrade() -> None:
    """Create all tables required by the application."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for enum in (
            ("tipoconteudo", tipo_conteudo.enums),
            ("estadoconteudo", estado_conteudo.enums),
            ("estadocontribuicao", estado_contribuicao.enums),
            ("perfilusuario", perfil_usuario.enums),
        ):
            values = ", ".join(
                f"'{value}'" for value in enum[1]
            )
            op.execute(
                sa.text(
                    f"DO $$ BEGIN "
                    f"CREATE TYPE public.{enum[0]} AS ENUM ({values}); "
                    f"EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
                )
            )

    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("senha_hash", sa.String(), nullable=False),
        sa.Column(
            "perfil",
            perfil_usuario,
            nullable=False,
            server_default="USUARIO",
        ),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_usuario_email", "usuario", ["email"], unique=True)

    op.create_table(
        "curso",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("sigla", sa.String(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "disciplina",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("curso_id", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("periodo", sa.String(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["curso_id"], ["curso.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_disciplina_curso_id", "disciplina", ["curso_id"])

    op.create_table(
        "conteudoacademico",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("disciplina_id", sa.Integer(), nullable=False),
        sa.Column("tipo", tipo_conteudo, nullable=False),
        sa.Column("titulo", sa.String(), nullable=False),
        sa.Column("corpo_ou_url", sa.String(), nullable=False),
        sa.Column("autor_id", sa.Integer(), nullable=False),
        sa.Column("origem", sa.String(), nullable=True),
        sa.Column("estado", estado_conteudo, nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["autor_id"], ["usuario.id"]),
        sa.ForeignKeyConstraint(["disciplina_id"], ["disciplina.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_conteudoacademico_disciplina_id",
        "conteudoacademico",
        ["disciplina_id"],
    )

    op.create_table(
        "contribuicao",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("autor_id", sa.Integer(), nullable=False),
        sa.Column("conteudo_id", sa.Integer(), nullable=True),
        sa.Column("disciplina_id", sa.Integer(), nullable=False),
        sa.Column("tipo", tipo_conteudo, nullable=False),
        sa.Column("titulo", sa.String(), nullable=False),
        sa.Column("corpo_ou_url", sa.String(), nullable=False),
        sa.Column("origem", sa.String(), nullable=True),
        sa.Column("estado", estado_contribuicao, nullable=False),
        sa.Column("justificativa_moderacao", sa.String(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["autor_id"], ["usuario.id"]),
        sa.ForeignKeyConstraint(["conteudo_id"], ["conteudoacademico.id"]),
        sa.ForeignKeyConstraint(["disciplina_id"], ["disciplina.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contribuicao_autor_id", "contribuicao", ["autor_id"])


def downgrade() -> None:
    """Drop all application tables and enum types."""
    op.drop_index("ix_contribuicao_autor_id", table_name="contribuicao")
    op.drop_table("contribuicao")
    op.drop_index(
        "ix_conteudoacademico_disciplina_id",
        table_name="conteudoacademico",
    )
    op.drop_table("conteudoacademico")
    op.drop_index("ix_disciplina_curso_id", table_name="disciplina")
    op.drop_table("disciplina")
    op.drop_table("curso")
    op.drop_index("ix_usuario_email", table_name="usuario")
    op.drop_table("usuario")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for enum_name in (
            "perfilusuario",
            "estadocontribuicao",
            "estadoconteudo",
            "tipoconteudo",
        ):
            op.execute(sa.text(f"DROP TYPE IF EXISTS public.{enum_name}"))
