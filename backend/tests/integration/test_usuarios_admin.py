from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.app.db import get_session
from backend.app.domain import Usuario
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
                Usuario(
                    nome="Administrador",
                    email="admin@example.com",
                    senha_hash=hash_senha("senha-segura"),
                    perfil="administrador",
                ),
                Usuario(
                    nome="Estudante",
                    email="estudante@example.com",
                    senha_hash=hash_senha("senha-segura"),
                ),
            ]
        )
        session.commit()


def login_token(client: TestClient, email: str) -> str:
    return client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "senha-segura"},
    ).json()["access_token"]


def test_somente_administrador_acessa_usuarios() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/usuarios",
            headers={
                "Authorization": f"Bearer {login_token(client, 'estudante@example.com')}"
            },
        )
    assert response.status_code == 403


def test_administrador_cria_e_atualiza_moderador() -> None:
    with TestClient(app) as client:
        auth = {
            "Authorization": f"Bearer {login_token(client, 'admin@example.com')}"
        }
        created = client.post(
            "/api/v1/usuarios",
            headers=auth,
            json={
                "nome": "Moderador",
                "email": "moderador@example.com",
                "senha": "senha-segura",
                "perfil": "moderador",
            },
        )
        assert created.status_code == 201
        usuario_id = created.json()["id"]
        assert "senha" not in created.text

        updated = client.patch(
            f"/api/v1/usuarios/{usuario_id}",
            headers=auth,
            json={"ativo": False},
        )
        assert updated.status_code == 200
        assert updated.json()["ativo"] is False
