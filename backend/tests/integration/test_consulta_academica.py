from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from backend.app.db import get_session
from backend.app.domain import (
    ConteudoAcademico,
    Curso,
    Disciplina,
    EstadoConteudo,
    TipoConteudo,
    Usuario,
)
from backend.app.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def session_override() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = session_override


@asynccontextmanager
async def no_lifespan(_app):
    yield


app.router.lifespan_context = no_lifespan


def setup_function() -> None:
    app.dependency_overrides[get_session] = session_override
    app.router.lifespan_context = no_lifespan
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        curso = Curso(nome="Engenharia de Software", sigla="ES")
        disciplina = Disciplina(
            curso_id=1,
            codigo="CIC-0001",
            nome="Fundamentos",
        )
        autor = Usuario(
            nome="Estudante",
            email="estudante@example.com",
            senha_hash="hash",
        )
        session.add_all([curso, disciplina, autor])
        session.commit()
        session.add(
            ConteudoAcademico(
                disciplina_id=1,
                tipo=TipoConteudo.RESUMO,
                titulo="Resumo inicial",
                corpo_ou_url="Conteúdo publicado",
                autor_id=1,
                estado=EstadoConteudo.PUBLICADO,
            )
        )
        session.commit()


def test_consulta_publica_filtra_por_tipo() -> None:
    with TestClient(app) as client:
        cursos = client.get("/api/v1/cursos")
        assert cursos.status_code == 200
        assert cursos.json()["itens"][0]["sigla"] == "ES"

        disciplinas = client.get("/api/v1/cursos/1/disciplinas")
        assert disciplinas.status_code == 200
        assert disciplinas.json()["itens"][0]["codigo"] == "CIC-0001"

        conteudos = client.get(
            "/api/v1/disciplinas/1/conteudos?tipo=resumo"
        )
        assert conteudos.status_code == 200
        assert len(conteudos.json()["itens"]) == 1


def test_consulta_sem_resultados_retorna_lista_vazia() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/disciplinas/1/conteudos?tipo=prova"
        )

    assert response.status_code == 200
    assert response.json() == {"itens": []}


def test_conteudo_arquivado_nao_e_exibido() -> None:
    with Session(engine) as session:
        conteudo = session.get(ConteudoAcademico, 1)
        assert conteudo is not None
        conteudo.estado = EstadoConteudo.ARQUIVADO
        session.add(conteudo)
        session.commit()

    with TestClient(app) as client:
        response = client.get("/api/v1/conteudos/1")

    assert response.status_code == 404
