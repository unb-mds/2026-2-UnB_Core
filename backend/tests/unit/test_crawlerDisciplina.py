from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from backend.app.crawler.crawlerDisciplina import (
    DisciplinaColetada,
    extrair_disciplinas_html,
    salvar_disciplinas,
)
from backend.app.domain import Curso, CursoDisciplina, Disciplina


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
        disciplina = session.exec(select(Disciplina)).one()
        assert session.exec(
            select(CursoDisciplina).where(
                CursoDisciplina.curso_id == curso.id,
                CursoDisciplina.disciplina_id == disciplina.id,
            )
        ).one()


def test_salvar_disciplinas_do_gama_associa_todos_os_cursos_fcte() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        software = Curso(nome="ENGENHARIA DE SOFTWARE", sigla="FCTE")
        eletronica = Curso(nome="ENGENHARIA ELETRÔNICA", sigla="FCTE")
        session.add_all([software, eletronica])
        session.commit()

        disciplinas = [
            DisciplinaColetada("FGA0003", "COMPILADORES 1", None),
            DisciplinaColetada("FCTE0005", "ALGORITMOS EM GRAFOS", None),
        ]
        assert salvar_disciplinas(session, disciplinas) == 4
        # Rodar de novo não duplica registros.
        assert salvar_disciplinas(session, disciplinas) == 4

        salvas = session.exec(select(Disciplina)).all()
        assert len(salvas) == 2
        for curso in (software, eletronica):
            disciplina_ids = session.exec(
                select(CursoDisciplina.disciplina_id).where(
                    CursoDisciplina.curso_id == curso.id
                )
            ).all()
            codigos = {
                d.codigo for d in salvas if d.id in disciplina_ids
            }
            assert codigos == {"FGA0003", "FCTE0005"}
