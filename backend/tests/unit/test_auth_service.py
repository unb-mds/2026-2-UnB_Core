from unittest.mock import MagicMock

import pytest

from backend.app.api.errors import ErroValidacao
from backend.app.domain import PerfilUsuario, Usuario
from backend.app.services import auth_service


def test_gera_e_verifica_senha():
    password_hash = auth_service.hash_senha("senha-segura")

    assert auth_service.verificar_senha("senha-segura", password_hash)
    assert not auth_service.verificar_senha("outra-senha", password_hash)


def test_cadastra_usuario_com_dados_normalizados():
    session = MagicMock()
    session.exec.return_value.first.return_value = None

    user = auth_service.cadastrar_usuario(
        session,
        nome="  Ana  ",
        email="ANA@EXAMPLE.COM",
        senha="senha-segura",
    )

    assert user.nome == "Ana"
    assert user.email == "ana@example.com"
    assert user.perfil == PerfilUsuario.USUARIO
    session.commit.assert_called_once()


def test_cadastro_rejeita_email_duplicado():
    session = MagicMock()
    session.exec.return_value.first.return_value = Usuario(
        id=1,
        nome="Ana",
        email="ana@example.com",
        senha_hash="hash",
    )

    with pytest.raises(ErroValidacao):
        auth_service.cadastrar_usuario(
            session,
            nome="Ana",
            email="ana@example.com",
            senha="senha-segura",
        )


def test_autentica_usuario_valido(usuario):
    session = MagicMock()
    usuario.senha_hash = auth_service.hash_senha("senha-segura")
    session.exec.return_value.first.return_value = usuario

    assert auth_service.autenticar_usuario(
        session,
        email="ANA@EXAMPLE.COM",
        senha="senha-segura",
    ) is usuario


@pytest.mark.parametrize("inactive", [True, False])
def test_rejeita_credenciais_invalidas(usuario, inactive):
    session = MagicMock()
    usuario.ativo = not inactive
    usuario.senha_hash = auth_service.hash_senha("senha-segura")
    session.exec.return_value.first.return_value = (
        None if inactive else usuario
    )

    with pytest.raises(ErroValidacao):
        auth_service.autenticar_usuario(
            session,
            email="ana@example.com",
            senha="senha-incorreta",
        )


def test_cria_sessao_para_usuario_persistido(usuario):
    token = auth_service.criar_sessao(usuario)

    assert token


def test_rejeita_sessao_para_usuario_nao_persistido():
    with pytest.raises(ErroValidacao):
        auth_service.criar_sessao(Usuario(
            nome="Ana",
            email="ana@example.com",
            senha_hash="hash",
        ))


def test_rota_auth_delega_para_servico_de_cadastro(monkeypatch):
    from backend.app.api.routers import auth
    from backend.app.api.schemas.auth import CadastroRequest

    expected = object()
    monkeypatch.setattr(auth, "cadastrar_usuario", lambda *_args, **_kwargs: expected)

    result = auth.cadastro(
        CadastroRequest(
            nome="Ana",
            email="ana@example.com",
            senha="senha-segura",
        ),
        MagicMock(),
    )

    assert result is expected
