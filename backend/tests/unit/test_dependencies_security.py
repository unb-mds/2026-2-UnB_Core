from unittest.mock import MagicMock

import pytest

from backend.app.api.dependencies import (
    exigir_perfil,
    obter_usuario_atual,
)
from backend.app.api.errors import NaoAutenticado, PermissaoNegada
from backend.app.api.security import criar_access_token, obter_usuario_token
from backend.app.domain import PerfilUsuario


def test_ciclo_completo_do_token():
    token = criar_access_token(7, PerfilUsuario.USUARIO.value)
    payload = obter_usuario_token(token)

    assert payload["sub"] == "7"
    assert payload["perfil"] == "usuario"


def test_rejeita_token_invalido():
    with pytest.raises(Exception) as error:
        obter_usuario_token("invalid")

    assert error.value.status_code == 401


def test_rejeita_token_sem_subject(monkeypatch):
    monkeypatch.setattr(
        "backend.app.api.security.jwt.decode",
        lambda *_args, **_kwargs: {"perfil": "usuario"},
    )

    with pytest.raises(Exception) as error:
        obter_usuario_token("valid-format-token")

    assert error.value.status_code == 401


def test_dependencia_retorna_usuario_ativo(session, usuario):
    session.get.return_value = usuario

    assert obter_usuario_atual({"sub": "1"}, session) is usuario


def test_dependencia_rejeita_sub_ausente(session):
    with pytest.raises(NaoAutenticado):
        obter_usuario_atual({}, session)


def test_dependencia_rejeita_usuario_inativo(session, usuario):
    usuario.ativo = False
    session.get.return_value = usuario

    with pytest.raises(NaoAutenticado):
        obter_usuario_atual({"sub": "1"}, session)


def test_dependencia_de_perfil_permite_perfil_exigido(moderador):
    dependency = exigir_perfil(PerfilUsuario.MODERADOR)

    assert dependency(moderador) is moderador


def test_dependencia_de_perfil_rejeita_perfil_incorreto(usuario):
    dependency = exigir_perfil(PerfilUsuario.ADMINISTRADOR)

    with pytest.raises(PermissaoNegada):
        dependency(usuario)
