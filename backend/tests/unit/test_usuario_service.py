from unittest.mock import MagicMock

import pytest

from backend.app.api.errors import ErroValidacao, NaoEncontrado
from backend.app.domain import PerfilUsuario, Usuario
from backend.app.services.usuario_service import (
    atualizar_usuario,
    criar_usuario_admin,
    listar_usuarios,
)


def test_lista_usuarios(session):
    users = [Usuario(
        id=1,
        nome="Ana",
        email="ana@example.com",
        senha_hash="hash",
    )]
    session.exec.return_value.all.return_value = users

    assert listar_usuarios(session) == users


def test_cria_usuario_administrador(session):
    session.exec.return_value.first.return_value = None

    user = criar_usuario_admin(
        session,
        nome=" Admin ",
        email="ADMIN@EXAMPLE.COM",
        senha="senha-segura",
        perfil=PerfilUsuario.ADMINISTRADOR,
    )

    assert user.nome == "Admin"
    assert user.email == "admin@example.com"
    assert user.perfil == PerfilUsuario.ADMINISTRADOR


def test_criacao_de_administrador_rejeita_duplicado(session):
    session.exec.return_value.first.return_value = object()

    with pytest.raises(ErroValidacao):
        criar_usuario_admin(
            session,
            nome="Admin",
            email="admin@example.com",
            senha="senha-segura",
            perfil=PerfilUsuario.ADMINISTRADOR,
        )


def test_atualiza_perfil_e_estado_ativo(session, usuario):
    session.get.return_value = usuario

    updated = atualizar_usuario(
        session,
        usuario.id,
        perfil=PerfilUsuario.MODERADOR,
        ativo=False,
    )

    assert updated.perfil == PerfilUsuario.MODERADOR
    assert updated.ativo is False
    session.commit.assert_called_once()


def test_atualizacao_rejeita_usuario_inexistente(session):
    session.get.return_value = None

    with pytest.raises(NaoEncontrado):
        atualizar_usuario(session, 99, perfil=None, ativo=True)


def test_atualizacao_rejeita_alteracao_vazia(session, usuario):
    session.get.return_value = usuario

    with pytest.raises(ErroValidacao):
        atualizar_usuario(session, usuario.id, perfil=None, ativo=None)
