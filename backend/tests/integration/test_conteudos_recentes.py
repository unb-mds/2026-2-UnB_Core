from collections.abc import Generator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.app.db import get_session
from backend.app.domain import (
    ConteudoAcademico,
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


@asynccontextmanager
async def no_lifespan(_app):
    yield


def setup_function() -> None:
    app.dependency_overrides[get_session] = session_override
    app.router.lifespan_context = no_lifespan
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    agora = datetime(2026, 11, 20, 12, tzinfo=timezone.utc)
    with Session(engine) as session:
        compiladores = Disciplina(codigo="FGA0003", nome="COMPILADORES 1")
        calculo = Disciplina(codigo="MAT0025", nome="CÁLCULO 1")
        autora = Usuario(nome="Ana Souza", email="ana@example.com", senha_hash="hash")
        session.add_all([compiladores, calculo, autora])
        session.flush()
        for horas, titulo, disciplina, estado in [
            (3, "Mais antigo", compiladores, EstadoConteudo.PUBLICADO),
            (2, "Arquivado", calculo, EstadoConteudo.ARQUIVADO),
            (1, "Do meio", calculo, EstadoConteudo.PUBLICADO),
            (0, "Mais novo", compiladores, EstadoConteudo.PUBLICADO),
        ]:
            momento = agora - timedelta(hours=horas)
            session.add(
                ConteudoAcademico(
                    disciplina_id=disciplina.id,
                    tipo=TipoConteudo.RESUMO,
                    titulo=titulo,
                    corpo_ou_url="texto",
                    autor_id=autora.id,
                    estado=estado,
                    criado_em=momento,
                    atualizado_em=momento,
                )
            )
        session.commit()


def test_lista_os_publicados_mais_recentes_de_todas_as_disciplinas() -> None:
    with TestClient(app) as client:
        resposta = client.get("/api/v1/conteudos")

    assert resposta.status_code == 200
    itens = resposta.json()["itens"]
    assert [item["titulo"] for item in itens] == ["Mais novo", "Do meio", "Mais antigo"]
    assert itens[1]["disciplina_nome"] == "CÁLCULO 1"
    assert itens[0]["autor_nome"] == "Ana Souza"


def test_respeita_e_valida_o_limite() -> None:
    with TestClient(app) as client:
        um = client.get("/api/v1/conteudos", params={"limite": 1})
        zero = client.get("/api/v1/conteudos", params={"limite": 0})
        alto = client.get("/api/v1/conteudos", params={"limite": 100})

    assert [item["titulo"] for item in um.json()["itens"]] == ["Mais novo"]
    assert zero.status_code == 422
    assert alto.status_code == 422


def test_detalhe_por_id_continua_funcionando() -> None:
    with TestClient(app) as client:
        resposta = client.get("/api/v1/conteudos/1")

    assert resposta.status_code == 200
    assert resposta.json()["titulo"] == "Mais antigo"
