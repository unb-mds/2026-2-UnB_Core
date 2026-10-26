from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from backend.tests.test_config import test_engine
from backend.app.moderacao import Decisao, get_decisao, get_usuario
from backend.app.api.schema.Contribuicao import Contribuicao


def user():
    return SimpleNamespace(id=7, nome="Ana", perfil="usuario")


def contribution():
    return Contribuicao(
        disciplina_id=1,
        tipo="artigo",
        origem="UnB",
        conteudo_id=2,
        payload="conteúdo",
        autor_id=7,
    )


def test_get_usuario_permite_moderador():
    session = MagicMock()
    session.get.return_value = SimpleNamespace(
        id=7,
        email="mod@example.com",
        nome="Moderador",
        status="Online",
        ativo=True,
        perfil="moderador",
    )

    assert get_usuario(7, session) == 7


def test_get_usuario_rejeita_usuario_comum():
    session = MagicMock()
    session.get.return_value = SimpleNamespace(
        id=7,
        email="user@example.com",
        nome="Usuário",
        status="Online",
        ativo=True,
        perfil="usuario",
    )

    with pytest.raises(HTTPException) as error:
        get_usuario(7, session)

    assert error.value.status_code == 403


def test_decisao_aprovada_publica_contribuicao():
    session = MagicMock()
    item = contribution()
    item.id = 1

    response = get_decisao(
        Decisao(estado="aprovada", justificativa_moderacao="Aprovado"),
        session,
        item,
        user(),
    )

    assert response.estado == "publicado"
    assert response.justificativa_moderacao == "Aprovado"
    session.commit.assert_called_once()
