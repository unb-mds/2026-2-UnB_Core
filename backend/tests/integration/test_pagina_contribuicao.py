from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.app.db import get_session
from backend.app.domain import (
    ConteudoAcademico,
    Contribuicao,
    Curso,
    CursoDisciplina,
    Disciplina,
    EstadoConteudo,
    TipoConteudo,
    Usuario,
)
from backend.app.main import app
from backend.app.services.auth_service import hash_senha


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
    with Session(engine) as session:
        curso = Curso(nome="ENGENHARIA DE SOFTWARE", sigla="FCTE")
        disciplina = Disciplina(codigo="FGA0003", nome="COMPILADORES 1")
        autora = Usuario(
            nome="Ana Souza",
            email="ana@example.com",
            senha_hash=hash_senha("senha-segura"),
        )
        outra = Usuario(
            nome="Bruno",
            email="bruno@example.com",
            senha_hash=hash_senha("senha-segura"),
        )
        session.add_all([curso, disciplina, autora, outra])
        session.flush()
        session.add(CursoDisciplina(curso_id=curso.id, disciplina_id=disciplina.id))
        session.add(
            ConteudoAcademico(
                disciplina_id=disciplina.id,
                tipo=TipoConteudo.RESUMO,
                titulo="Resumo de análise léxica",
                corpo_ou_url="Tokens, lexemas e autômatos.",
                autor_id=autora.id,
                estado=EstadoConteudo.PUBLICADO,
            )
        )
        session.add(
            Contribuicao(
                autor_id=autora.id,
                disciplina_id=disciplina.id,
                tipo=TipoConteudo.DICA,
                titulo="Dica de parser",
                corpo_ou_url="Comece pela gramática.",
            )
        )
        session.commit()


def autenticar(client: TestClient, email: str) -> dict[str, str]:
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "senha-segura"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_conteudo_publicado_traz_nomes_da_disciplina_e_do_autor() -> None:
    with TestClient(app) as client:
        detalhe = client.get("/api/v1/conteudos/1")
        lista = client.get("/api/v1/disciplinas/1/conteudos")

    assert detalhe.status_code == 200
    corpo = detalhe.json()
    assert corpo["disciplina_codigo"] == "FGA0003"
    assert corpo["disciplina_nome"] == "COMPILADORES 1"
    assert corpo["autor_nome"] == "Ana Souza"
    # Só o nome do autor é público.
    assert "ana@example.com" not in detalhe.text
    assert lista.json()["itens"][0]["autor_nome"] == "Ana Souza"


def test_autor_consulta_a_propria_contribuicao_pelo_id() -> None:
    with TestClient(app) as client:
        resposta = client.get(
            "/api/v1/contribuicoes/minhas/1",
            headers=autenticar(client, "ana@example.com"),
        )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["titulo"] == "Dica de parser"
    assert corpo["estado"] == "pendente"
    assert corpo["disciplina_codigo"] == "FGA0003"
    assert corpo["disciplina_nome"] == "COMPILADORES 1"


def test_contribuicao_de_outra_pessoa_ou_inexistente_nao_e_exibida() -> None:
    with TestClient(app) as client:
        sem_login = client.get("/api/v1/contribuicoes/minhas/1")
        de_outra_pessoa = client.get(
            "/api/v1/contribuicoes/minhas/1",
            headers=autenticar(client, "bruno@example.com"),
        )
        inexistente = client.get(
            "/api/v1/contribuicoes/minhas/999",
            headers=autenticar(client, "ana@example.com"),
        )

    assert sem_login.status_code == 401
    assert de_outra_pessoa.status_code == 422
    assert "Comece pela gramática" not in de_outra_pessoa.text
    assert inexistente.status_code == 404


def test_listagem_e_edicao_das_contribuicoes_trazem_a_disciplina() -> None:
    with TestClient(app) as client:
        headers = autenticar(client, "ana@example.com")
        minhas = client.get("/api/v1/contribuicoes/minhas", headers=headers)
        editada = client.patch(
            "/api/v1/contribuicoes/minhas/1",
            headers=headers,
            json={"titulo": "Dica de parser revisada"},
        )

    assert minhas.json()[0]["disciplina_nome"] == "COMPILADORES 1"
    assert editada.status_code == 200
    assert editada.json()["disciplina_nome"] == "COMPILADORES 1"
