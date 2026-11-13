from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from backend.app.crawler.crawlerDisciplina import (
    DisciplinaColetada,
    extrair_disciplinas_html,
    salvar_disciplinas,
)
from backend.app.domain import Curso, Disciplina


def test_extrair_disciplinas_html_deduplica_turmas() -> None:
    html = """
    <table class="listagem">
      <tr><th>Código</th><th>Ano-Período</th></tr>
      <tr class="agrupador"><td colspan="8">
        <span class="tituloDisciplina">CIC0002 - FUNDAMENTOS TEÓRICOS</span>
      </td></tr>
      <tr><td class="turma">01</td><td class="anoPeriodo">2026.2</td></tr>
      <tr class="agrupador"><td colspan="8">
        <span class="tituloDisciplina">CIC0002 - FUNDAMENTOS TEÓRICOS</span>
      </td></tr>
      <tr><td class="turma">02</td><td class="anoPeriodo">2026.2</td></tr>
    </table>
    """

    assert extrair_disciplinas_html(html) == [
        DisciplinaColetada(
            codigo="CIC0002",
            nome="FUNDAMENTOS TEÓRICOS",
            periodo="2026.2",
        )
    ]


def test_salvar_disciplinas_associa_curso_pelo_prefixo() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        curso = Curso(nome="Computação", sigla="CIC")
        session.add(curso)
        session.commit()
        session.refresh(curso)

        assert salvar_disciplinas(
            session,
            [
                DisciplinaColetada(
                    "CIC0002",
                    "Fundamentos",
                    "2026.2",
                )
            ],
        ) == 1
        assert session.exec(select(Disciplina)).one().curso_id == curso.id
