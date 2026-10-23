import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from backend.tests.test_config import session, test_engine
from backend.app.api.schema import usuario as usuario_module


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(usuario_module.router_usuario)

    def override_get_session():
        from sqlmodel import Session

        with Session(test_engine) as database_session:
            yield database_session

    app.dependency_overrides[usuario_module.get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client


def user_payload(
    email="ana@example.com",
    nome="Ana",
    status="Online",
    senha="senha-segura",
):
    return {
        "email": email,
        "nome": nome,
        "status": status,
        "senha": senha,
    }


def create_user(session, **kwargs):
    data = user_payload(**kwargs)
    plain_password = data.pop("senha")
    user = usuario_module.Usuario(
        **data,
        senha=usuario_module.hash_senha(plain_password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def auth_headers(user):
    token = usuario_module.criar_access_token(user.id, user.perfil)
    return {"Authorization": f"Bearer {token}"}


def test_cadastro_cria_usuario_sem_expor_senha(client, session):
    response = client.post("/usuario/cadastro", json=user_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "ana@example.com"
    assert body["perfil"] == "usuario"
    assert "senha" not in body

    created = session.get(usuario_module.Usuario, body["id"])
    assert created is not None
    assert created.senha != "senha-segura"
    assert usuario_module.verificar_senha("senha-segura", created.senha)


def test_cadastro_rejeita_email_duplicado(client, session):
    create_user(session)

    response = client.post("/usuario/cadastro", json=user_payload())

    assert response.status_code == 409
    assert response.json()["detail"] == "Ja existe usuario com esse e-mail cadastrado"


def test_cadastro_rejeita_status_invalido(client):
    response = client.post(
        "/usuario/cadastro",
        json=user_payload(status="Disponível"),
    )

    assert response.status_code == 422


def test_hash_senha_trunca_senhas_maiores_que_72_bytes():
    senha = "a" * 73

    hashed_password = usuario_module.hash_senha(senha)

    assert usuario_module.verificar_senha("a" * 72, hashed_password)
    assert usuario_module.verificar_senha(senha, hashed_password)


def test_perfil_invalido_e_rejeitado():
    with pytest.raises(ValueError, match="Perfil de usuario não valido"):
        usuario_module.Usuario.validate_perfil("superusuario")


def test_login_retorna_token_e_usuario(client, session):
    user = create_user(session)

    response = client.post(
        "/usuario/login",
        data={"username": user.email, "password": "senha-segura"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["usuario"]["id"] == user.id
    assert body["usuario"]["email"] == user.email


def test_login_rejeita_senha_incorreta(client, session):
    user = create_user(session)

    response = client.post(
        "/usuario/login",
        data={"username": user.email, "password": "senha-incorreta"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "E-mail ou senha incorretos"


def test_login_rejeita_usuario_inexistente(client):
    response = client.post(
        "/usuario/login",
        data={"username": "inexistente@example.com", "password": "qualquer"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha incorretos"


def test_me_retorna_usuario_autenticado(client, session):
    user = create_user(session)

    response = client.get("/usuario/me", headers=auth_headers(user))

    assert response.status_code == 200
    assert response.json()["id"] == user.id
    assert response.json()["email"] == user.email


def test_me_rejeita_requisicao_sem_token(client):
    response = client.get("/usuario/me")

    assert response.status_code == 401


def test_me_rejeita_usuario_inativo(client, session):
    user = create_user(session)
    user.ativo = False
    session.add(user)
    session.commit()

    response = client.get("/usuario/me", headers=auth_headers(user))

    assert response.status_code == 401
    assert response.json()["detail"] == "Usuário inválido ou inativo"


def test_remover_exclui_usuario_autenticado(client, session):
    user = create_user(session)
    user_id = user.id

    response = client.delete("/usuario/remover", headers=auth_headers(user))

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    session.expire_all()
    assert session.get(usuario_module.Usuario, user_id) is None


def test_verificar_admin_moderador_permite_administrador(session):
    user = create_user(session, email="admin@example.com")
    user.perfil = "administrador"

    assert usuario_module.verificar_admin_moderador(user, session) is user


def test_verificar_admin_moderador_permite_moderador(session):
    user = create_user(
        session,
        email="moderador@example.com",
    )
    user.perfil = "moderador"

    assert usuario_module.verificar_admin_moderador(user, session) is user


def test_verificar_admin_moderador_rejeita_usuario_comum(session):
    user = create_user(session)

    with pytest.raises(HTTPException) as error:
        usuario_module.verificar_admin_moderador(user, session)

    assert error.value.status_code == 403
    assert error.value.detail == "Ana não tem permição para acessar essa pagina"
