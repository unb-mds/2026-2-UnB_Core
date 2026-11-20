from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from backend.app.db import get_session
from backend.app.domain import (
    ConteudoAcademico,
    Contribuicao,
    Curso,
    CursoDisciplina,
    Disciplina,
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
        session.add_all(
            [
                curso,
                disciplina,
                Usuario(
                    nome="Moderador",
                    email="moderador@example.com",
                    senha_hash=hash_senha("senha-segura"),
                    perfil="moderador",
                ),
                Usuario(
                    nome="Estudante",
                    email="estudante@example.com",
                    senha_hash=hash_senha("senha-segura"),
                ),
            ]
        )
        session.flush()
        session.add(CursoDisciplina(curso_id=curso.id, disciplina_id=disciplina.id))
        session.commit()


def autenticar(client: TestClient, email: str) -> dict[str, str]:
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "senha-segura"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def aprovar(client: TestClient, moderador: dict[str, str], contribuicao_id: int) -> None:
    resposta = client.post(
        f"/api/v1/moderacao/contribuicoes/{contribuicao_id}/decisao",
        headers=moderador,
        json={"decisao": "aprovar"},
    )
    assert resposta.status_code == 200


def conteudos_publicados(client: TestClient) -> list[dict]:
    return client.get("/api/v1/disciplinas/1/conteudos").json()["itens"]


def test_editar_contribuicao_aprovada_atualiza_o_mesmo_conteudo() -> None:
    with TestClient(app) as client:
        estudante = autenticar(client, "estudante@example.com")
        moderador = autenticar(client, "moderador@example.com")

        criada = client.post(
            "/api/v1/contribuicoes",
            headers=estudante,
            json={
                "disciplina_id": 1,
                "tipo": "resumo",
                "titulo": "Resumo v1",
                "corpo_ou_url": "Primeira versão",
            },
        ).json()
        aprovar(client, moderador, criada["id"])

        publicados = conteudos_publicados(client)
        assert [conteudo["titulo"] for conteudo in publicados] == ["Resumo v1"]
        conteudo_id = publicados[0]["id"]

        minhas = client.get("/api/v1/contribuicoes/minhas", headers=estudante).json()
        assert minhas[0]["conteudo_id"] == conteudo_id

        editada = client.patch(
            f"/api/v1/contribuicoes/minhas/{criada['id']}",
            headers=estudante,
            json={"titulo": "Resumo v2", "corpo_ou_url": "Segunda versão"},
        )
        assert editada.json()["estado"] == "pendente"
        # Enquanto a edição está pendente, a versão aprovada continua visível.
        assert [conteudo["titulo"] for conteudo in conteudos_publicados(client)] == ["Resumo v1"]

        aprovar(client, moderador, criada["id"])

        publicados = conteudos_publicados(client)
        assert len(publicados) == 1
        assert publicados[0]["id"] == conteudo_id
        assert publicados[0]["titulo"] == "Resumo v2"
        assert publicados[0]["corpo_ou_url"] == "Segunda versão"

    with Session(engine) as session:
        assert len(session.exec(select(ConteudoAcademico)).all()) == 1
        assert len(session.exec(select(Contribuicao)).all()) == 1
