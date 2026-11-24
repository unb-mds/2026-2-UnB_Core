from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.app.api.routers import academico
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


def setup_function() -> None:
    app.dependency_overrides[get_session] = session_override
    app.router.lifespan_context = no_lifespan
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                Usuario(
                    nome="Admin",
                    email="admin@example.com",
                    senha_hash=hash_senha("senha-segura"),
                    perfil="administrador",
                ),
                # E-mail com domínio reservado (.local), que o EmailStr recusa.
                Usuario(
                    nome="Conta antiga",
                    email="antiga@unbcore.local",
                    senha_hash="hash",
                    ativo=False,
                ),
            ]
        )
        session.commit()


def test_lista_de_usuarios_nao_quebra_com_email_fora_do_padrao() -> None:
    with TestClient(app) as client:
        token = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "senha": "senha-segura"},
        ).json()["access_token"]
        resposta = client.get("/api/v1/usuarios", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 200
    assert {usuario["email"] for usuario in resposta.json()} == {"admin@example.com", "antiga@unbcore.local"}


def test_erro_inesperado_chega_ao_front_com_cors_e_mensagem_padrao(monkeypatch) -> None:
    def falhar(*_args, **_kwargs):
        raise RuntimeError("falha inesperada")

    monkeypatch.setattr(academico, "listar_cursos_ativos", falhar)

    with TestClient(app) as client:
        resposta = client.get("/api/v1/cursos", headers={"Origin": "http://localhost:5173"})

    assert resposta.status_code == 500
    assert resposta.json()["erro"]["codigo"] == "ERRO_INTERNO"
    # Com o cabeçalho de CORS, o navegador entrega a resposta ao front, que mostra a
    # mensagem de erro em vez de "Não foi possível conectar à API".
    assert resposta.headers["access-control-allow-origin"] == "http://localhost:5173"
    # Os detalhes da exceção não vazam para o cliente.
    assert "falha inesperada" not in resposta.text
