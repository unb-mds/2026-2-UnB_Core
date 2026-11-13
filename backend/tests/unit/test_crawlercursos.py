from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool

from backend.app.crawler.crawlercursos import (
    CursoColetado,
    extrair_cursos_html,
    salvar_cursos,
)
from backend.app.domain import Curso, GrauCurso


def test_extrair_cursos_html_usa_departamento_como_sigla() -> None:
    html = """
    <table>
      <tr><th>Nome</th></tr>
      <tr><td colspan="7">ADM - DEPTO ADMINISTRAÇÃO</td></tr>
      <tr><td>ADMINISTRAÇÃO</td><td>Bacharelado</td><td>NOTURNO</td>
          <td>BRASÍLIA</td><td>Presencial</td><td>Bacharelado</td>
          <td>Coordenação</td></tr>
      <tr><td>ADMINISTRAÇÃO</td><td>Bacharelado</td><td>DIURNO</td>
          <td>BRASÍLIA</td><td>Presencial</td><td>Bacharelado</td>
          <td>Coordenação</td></tr>
    </table>
    """

    assert extrair_cursos_html(html) == [
        CursoColetado(
            nome="ADMINISTRAÇÃO",
            sigla="ADM",
            grau=GrauCurso.BACHARELADO,
        ),
    ]


def test_salvar_cursos_e_idempotente() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    cursos = [
        CursoColetado(
            nome="ADMINISTRAÇÃO",
            sigla="ADM",
            grau=GrauCurso.BACHARELADO,
        )
    ]

    with Session(engine) as session:
        assert salvar_cursos(session, cursos) == 1
        assert salvar_cursos(session, cursos) == 1
        assert len(session.exec(select(Curso)).all()) == 1
