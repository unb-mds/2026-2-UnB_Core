from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.app.db import get_session
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


def cadastrar_e_autenticar(
    client: TestClient,
    email: str = "estudante@example.com",
) -> dict[str, str]:
    client.post(
        "/api/v1/auth/cadastro",
        json={"nome": "Estudante", "email": email, "senha": "senha-segura"},
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "senha-segura"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_usuario_altera_nome_sem_senha_atual() -> None:
    with TestClient(app) as client:
        headers = cadastrar_e_autenticar(client)

        resposta = client.patch(
            "/api/v1/auth/me",
            json={"nome": "  Novo Nome  "},
            headers=headers,
        )

        assert resposta.status_code == 200
        assert resposta.json()["nome"] == "Novo Nome"
        assert client.get("/api/v1/auth/me", headers=headers).json()["nome"] == "Novo Nome"


def test_usuario_altera_email_e_senha_com_senha_atual() -> None:
    with TestClient(app) as client:
        headers = cadastrar_e_autenticar(client)

        resposta = client.patch(
            "/api/v1/auth/me",
            json={
                "email": "Novo@Example.com",
                "senha_atual": "senha-segura",
                "nova_senha": "outra-senha-segura",
            },
            headers=headers,
        )

        assert resposta.status_code == 200
        assert resposta.json()["email"] == "novo@example.com"
        # O token continua válido, porque identifica o usuário pelo id.
        assert client.get("/api/v1/auth/me", headers=headers).status_code == 200
        login_antigo = client.post(
            "/api/v1/auth/login",
            json={"email": "novo@example.com", "senha": "senha-segura"},
        )
        login_novo = client.post(
            "/api/v1/auth/login",
            json={"email": "novo@example.com", "senha": "outra-senha-segura"},
        )
        assert login_antigo.status_code == 422
        assert login_novo.status_code == 200


def test_troca_de_email_ou_senha_exige_senha_atual_correta() -> None:
    with TestClient(app) as client:
        headers = cadastrar_e_autenticar(client)

        sem_senha = client.patch(
            "/api/v1/auth/me",
            json={"nova_senha": "outra-senha-segura"},
            headers=headers,
        )
        senha_errada = client.patch(
            "/api/v1/auth/me",
            json={"email": "novo@example.com", "senha_atual": "errada"},
            headers=headers,
        )

        assert sem_senha.status_code == 422
        assert senha_errada.status_code == 422
        assert client.get("/api/v1/auth/me", headers=headers).json()["email"] == (
            "estudante@example.com"
        )


def test_usuario_nao_usa_email_de_outra_conta() -> None:
    with TestClient(app) as client:
        cadastrar_e_autenticar(client, "outra@example.com")
        headers = cadastrar_e_autenticar(client)

        resposta = client.patch(
            "/api/v1/auth/me",
            json={"email": "outra@example.com", "senha_atual": "senha-segura"},
            headers=headers,
        )

        assert resposta.status_code == 422
        assert "e-mail" in resposta.text


def test_atualizar_perfil_exige_login_e_algum_dado() -> None:
    with TestClient(app) as client:
        assert client.patch("/api/v1/auth/me", json={"nome": "X"}).status_code == 401

        headers = cadastrar_e_autenticar(client)
        vazio = client.patch("/api/v1/auth/me", json={}, headers=headers)

        assert vazio.status_code == 422
