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
    Disciplina,
    EstadoContribuicao,
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


app.dependency_overrides[get_session] = session_override
app.router.lifespan_context = no_lifespan


def setup_function() -> None:
    app.dependency_overrides[get_session] = session_override
    app.router.lifespan_context = no_lifespan
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                Curso(nome="Engenharia de Software", sigla="ES"),
                Disciplina(curso_id=1, codigo="CIC-0001", nome="Fundamentos"),
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
        session.commit()
        session.add(
            Contribuicao(
                autor_id=2,
                disciplina_id=1,
                tipo="resumo",
                titulo="Resumo pendente",
                corpo_ou_url="Texto",
            )
        )
        session.commit()


def token(client: TestClient, email: str) -> str:
    return client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "senha-segura"},
    ).json()["access_token"]


def test_usuario_comum_nao_acessa_moderacao() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/moderacao/contribuicoes",
            headers={"Authorization": f"Bearer {token(client, 'estudante@example.com')}"},
        )

    assert response.status_code == 403


def test_moderador_aprova_e_publica_conteudo() -> None:
    with TestClient(app) as client:
        auth = {"Authorization": f"Bearer {token(client, 'moderador@example.com')}"}
        lista = client.get("/api/v1/moderacao/contribuicoes", headers=auth)
        assert lista.status_code == 200
        assert lista.json()[0]["estado"] == "pendente"

        response = client.post(
            "/api/v1/moderacao/contribuicoes/1/decisao",
            headers=auth,
            json={"decisao": "aprovar"},
        )
        assert response.status_code == 200
        assert response.json()["estado"] == "aprovada"

        conteudos = client.get("/api/v1/disciplinas/1/conteudos")
        assert conteudos.status_code == 200
        assert conteudos.json()["itens"][0]["titulo"] == "Resumo pendente"


def test_ajustes_exigem_justificativa_e_preservam_decisao() -> None:
    with TestClient(app) as client:
        auth = {"Authorization": f"Bearer {token(client, 'moderador@example.com')}"}
        sem_justificativa = client.post(
            "/api/v1/moderacao/contribuicoes/1/decisao",
            headers=auth,
            json={"decisao": "ajustes"},
        )
        assert sem_justificativa.status_code == 422

        response = client.post(
            "/api/v1/moderacao/contribuicoes/1/decisao",
            headers=auth,
            json={
                "decisao": "ajustes",
                "justificativa": "Inclua a fonte consultada.",
            },
        )
        assert response.status_code == 200
        assert response.json()["estado"] == "ajustes"
        assert response.json()["justificativa_moderacao"] == "Inclua a fonte consultada."
