from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.app.services.curso_service import (
    listar_cursos_ativos,
    listar_disciplinas_ativas,
)
from backend.app.domain import Curso


def test_lista_cursos_ativos(session):
    expected = [object()]
    session.exec.return_value.all.return_value = expected

    assert listar_cursos_ativos(session) == expected


def test_lista_disciplinas_ativas(session):
    expected = [object()]
    session.exec.return_value.all.return_value = expected

    assert listar_disciplinas_ativas(session, 10) == expected


def test_lista_cursos_ativos_retorna_cursos_de_todas_as_unidades():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Curso(nome="CIÊNCIA DA COMPUTAÇÃO", sigla="CIC"))
        session.add(Curso(nome="ENGENHARIA DE SOFTWARE", sigla="FCTE"))
        session.commit()

        cursos = listar_cursos_ativos(session)

    assert [curso.nome for curso in cursos] == [
        "CIÊNCIA DA COMPUTAÇÃO",
        "ENGENHARIA DE SOFTWARE",
    ]
