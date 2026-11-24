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


def setup_function() -> None:
    app.dependency_overrides[get_session] = session_override
    app.router.lifespan_context = no_lifespan
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                Usuario(nome="Ana Admin", email="admin@example.com", senha_hash=hash_senha("senha-segura"), perfil="administrador"),
                Usuario(nome="Mauro", email="moderador@example.com", senha_hash=hash_senha("senha-segura"), perfil="moderador"),
                Usuario(nome="Bia", email="bia@example.com", senha_hash=hash_senha("senha-esquecida")),
                Usuario(nome="Inativo", email="inativo@example.com", senha_hash=hash_senha("senha-segura"), ativo=False),
            ]
        )
        session.commit()


def autenticar(client: TestClient, email: str, senha: str = "senha-segura") -> dict[str, str]:
    resposta = client.post("/api/v1/auth/login", json={"email": email, "senha": senha})
    assert resposta.status_code == 200, resposta.text
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


def pedir(client: TestClient, email: str, contato: str | None = None):
    return client.post("/api/v1/auth/recuperar-senha", json={"email": email, "contato": contato})


def test_resposta_e_igual_para_email_cadastrado_ou_nao() -> None:
    with TestClient(app) as client:
        cadastrado = pedir(client, "BIA@example.com", "WhatsApp (61) 90000-0000")
        desconhecido = pedir(client, "ninguem@example.com")
        invalido = pedir(client, "nao-e-email")

    assert cadastrado.status_code == desconhecido.status_code == 202
    assert cadastrado.json() == desconhecido.json()
    assert invalido.status_code == 422


def test_administrador_ve_o_pedido_e_o_moderador_nao() -> None:
    with TestClient(app) as client:
        pedir(client, "bia@example.com", "WhatsApp (61) 90000-0000")
        pedir(client, "inativo@example.com")
        admin = autenticar(client, "admin@example.com")
        moderador = autenticar(client, "moderador@example.com")

        pedidos = client.get("/api/v1/usuarios/gestao", headers=admin, params={"recuperacao": "true"})
        para_moderador = client.get("/api/v1/usuarios/gestao", headers=moderador, params={"recuperacao": "true"})

    # Conta desativada não gera pedido.
    assert [item["nome"] for item in pedidos.json()] == ["Bia"]
    assert pedidos.json()[0]["contato_recuperacao"] == "WhatsApp (61) 90000-0000"
    assert pedidos.json()[0]["recuperacao_senha_solicitada_em"] is not None
    # O moderador não filtra por pedidos nem vê o contato.
    assert {item["nome"] for item in para_moderador.json()} == {"Bia", "Inativo"}
    assert all(item["contato_recuperacao"] is None for item in para_moderador.json())


def test_senha_temporaria_atende_o_pedido_e_exige_troca_no_login() -> None:
    with TestClient(app) as client:
        pedir(client, "bia@example.com", "Telegram @bia")
        admin = autenticar(client, "admin@example.com")
        bia_id = client.get("/api/v1/usuarios/gestao", headers=admin, params={"recuperacao": "true"}).json()[0]["id"]

        client.post(f"/api/v1/usuarios/{bia_id}/senha-temporaria", headers=admin, json={"nova_senha": "temporaria-123"})
        restantes = client.get("/api/v1/usuarios/gestao", headers=admin, params={"recuperacao": "true"}).json()

        login_temporario = client.post("/api/v1/auth/login", json={"email": "bia@example.com", "senha": "temporaria-123"})
        token = {"Authorization": f"Bearer {login_temporario.json()['access_token']}"}
        troca = client.patch(
            "/api/v1/auth/me",
            headers=token,
            json={"senha_atual": "temporaria-123", "nova_senha": "minha-senha-nova"},
        )
        login_definitivo = client.post("/api/v1/auth/login", json={"email": "bia@example.com", "senha": "minha-senha-nova"})

    # O pedido sai da lista e o contato é apagado.
    assert restantes == []
    assert login_temporario.status_code == 200
    assert login_temporario.json()["trocar_senha"] is True
    assert troca.status_code == 200
    assert login_definitivo.json()["trocar_senha"] is False


def test_contato_tem_limite_de_tamanho() -> None:
    with TestClient(app) as client:
        resposta = pedir(client, "bia@example.com", "x" * 301)

    assert resposta.status_code == 422
