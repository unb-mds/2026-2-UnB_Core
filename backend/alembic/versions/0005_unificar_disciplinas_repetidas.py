"""Fix the course-discipline link table and merge duplicated disciplines.

1. The 0004 migration created "curso_disciplina", but the CursoDisciplina
   model had no __tablename__, so SQLModel used "cursodisciplina" and
   create_all() created that empty table at startup. Links written there
   (e.g. by the crawler on a fresh database) are moved to "curso_disciplina"
   and the wrong table is dropped.
2. Before 0004 each course had its own copy of a discipline (e.g. FGA0003
   existed once per Gama course). The 0004 migration kept those copies, each
   linked to a single course, so content published in one course did not
   show up in the others. One row per code is kept and every course link,
   content and contribution is moved to it.
"""

from collections import defaultdict
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005"
down_revision: Union[str, Sequence[str], None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Tabelas declaradas aqui, e não importadas dos models, para a migration
# continuar válida mesmo que os models mudem depois.
disciplina = sa.table(
    "disciplina",
    sa.column("id", sa.Integer),
    sa.column("codigo", sa.String),
    sa.column("ativo", sa.Boolean),
)
curso_disciplina = sa.table(
    "curso_disciplina",
    sa.column("curso_id", sa.Integer),
    sa.column("disciplina_id", sa.Integer),
)
conteudo_academico = sa.table(
    "conteudoacademico",
    sa.column("disciplina_id", sa.Integer),
)
contribuicao = sa.table(
    "contribuicao",
    sa.column("disciplina_id", sa.Integer),
)


TABELA_ERRADA = "cursodisciplina"


def consolidar_tabela_de_vinculos(conexao: sa.engine.Connection) -> int:
    """Move os vínculos da tabela "cursodisciplina" para "curso_disciplina".

    Retorna quantos vínculos foram copiados. Não faz nada se a tabela errada
    não existir.
    """
    if not sa.inspect(conexao).has_table(TABELA_ERRADA):
        return 0

    tabela_errada = sa.table(
        TABELA_ERRADA,
        sa.column("curso_id", sa.Integer),
        sa.column("disciplina_id", sa.Integer),
    )
    existentes = set(
        conexao.execute(
            sa.select(curso_disciplina.c.curso_id, curso_disciplina.c.disciplina_id)
        ).tuples()
    )
    novos = [
        {"curso_id": curso_id, "disciplina_id": disciplina_id}
        for curso_id, disciplina_id in conexao.execute(
            sa.select(tabela_errada.c.curso_id, tabela_errada.c.disciplina_id)
        ).tuples()
        if (curso_id, disciplina_id) not in existentes
    ]
    if novos:
        conexao.execute(curso_disciplina.insert(), novos)
    conexao.execute(sa.text(f"DROP TABLE {TABELA_ERRADA}"))
    return len(novos)


def unificar_disciplinas_repetidas(conexao: sa.engine.Connection) -> int:
    """Mantém uma disciplina por código e retorna quantas cópias foram removidas.

    A disciplina mantida é a ativa de menor id (ou a de menor id, se nenhuma
    estiver ativa). Os vínculos com cursos, conteúdos e contribuições das
    cópias passam para ela antes de as cópias serem apagadas.
    """
    grupos: dict[str, list[tuple[int, bool]]] = defaultdict(list)
    linhas = conexao.execute(
        sa.select(disciplina.c.id, disciplina.c.codigo, disciplina.c.ativo)
        .order_by(disciplina.c.id)
    ).all()
    for id_disciplina, codigo, ativo in linhas:
        grupos[codigo].append((id_disciplina, bool(ativo)))

    removidas_total = 0
    for copias in grupos.values():
        if len(copias) < 2:
            continue
        ativas = [id_disciplina for id_disciplina, ativo in copias if ativo]
        mantida = ativas[0] if ativas else copias[0][0]
        removidas = [id_disciplina for id_disciplina, _ in copias if id_disciplina != mantida]

        cursos_da_mantida = set(
            conexao.execute(
                sa.select(curso_disciplina.c.curso_id).where(
                    curso_disciplina.c.disciplina_id == mantida
                )
            ).scalars()
        )
        cursos_das_copias = set(
            conexao.execute(
                sa.select(curso_disciplina.c.curso_id).where(
                    curso_disciplina.c.disciplina_id.in_(removidas)
                )
            ).scalars()
        )
        novos_cursos = sorted(cursos_das_copias - cursos_da_mantida)
        if novos_cursos:
            conexao.execute(
                curso_disciplina.insert(),
                [
                    {"curso_id": curso_id, "disciplina_id": mantida}
                    for curso_id in novos_cursos
                ],
            )
        conexao.execute(
            curso_disciplina.delete().where(
                curso_disciplina.c.disciplina_id.in_(removidas)
            )
        )
        for tabela in (conteudo_academico, contribuicao):
            conexao.execute(
                tabela.update()
                .where(tabela.c.disciplina_id.in_(removidas))
                .values(disciplina_id=mantida)
            )
        conexao.execute(disciplina.delete().where(disciplina.c.id.in_(removidas)))
        removidas_total += len(removidas)
    return removidas_total


def upgrade() -> None:
    conexao = op.get_bind()
    consolidar_tabela_de_vinculos(conexao)
    unificar_disciplinas_repetidas(conexao)


def downgrade() -> None:
    # A junção não pode ser desfeita: não há como saber qual cópia pertencia
    # a qual curso. A tabela "cursodisciplina" também não é recriada, porque
    # era um erro. O downgrade da 0004 continua funcionando, porque escolhe
    # um curso para cada disciplina.
    pass
