from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.app.db import get_session
from backend.app.domain import Curso, Disciplina
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


app.dependency_overrides[get_session] = session_override
app.router.lifespan_context = no_lifespan


def setup_function() -> None:
    app.dependency_overrides[get_session] = session_override
    app.router.lifespan_context = no_lifespan
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Curso(nome="Engenharia de Software", sigla="ES"))
        session.add(
            Disciplina(
                curso_id=1,
                codigo="CIC-0001",
                nome="Fundamentos",
            )
        )
        session.commit()


def test_cadastro_login_e_me() -> None:
    with TestClient(app) as client:
        cadastro = client.post(
            "/api/v1/auth/cadastro",
            json={
                "nome": "Estudante",
                "email": "estudante@example.com",
                "senha": "senha-segura",
            },
        )
        assert cadastro.status_code == 201
        assert "senha" not in cadastro.text

        login = client.post(
            "/api/v1/auth/login",
            json={
                "email": "estudante@example.com",
                "senha": "senha-segura",
            },
        )
        assert login.status_code == 200
        token = login.json()["access_token"]

        me = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me.status_code == 200
        assert me.json()["email"] == "estudante@example.com"


def test_contribuicao_exige_login_e_fica_pendente() -> None:
    with TestClient(app) as client:
        payload = {
            "disciplina_id": 1,
            "tipo": "resumo",
            "titulo": "Resumo",
            "corpo_ou_url": "Conteúdo para revisão",
        }
        assert client.post("/api/v1/contribuicoes", json=payload).status_code == 401

        login = client.post(
            "/api/v1/auth/cadastro",
            json={
                "nome": "Colaborador",
                "email": "colaborador@example.com",
                "senha": "senha-segura",
            },
        )
        assert login.status_code == 201
        token = client.post(
            "/api/v1/auth/login",
            json={
                "email": "colaborador@example.com",
                "senha": "senha-segura",
            },
        ).json()["access_token"]

        response = client.post(
            "/api/v1/contribuicoes",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["estado"] == "pendente"

        minhas = client.get(
            "/api/v1/contribuicoes/minhas",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert minhas.status_code == 200
        assert len(minhas.json()) == 1
