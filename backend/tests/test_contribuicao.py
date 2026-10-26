from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from backend.tests.test_config import test_engine
from backend.app.api.schema.Contribuicao import (
    Contribuicao,
    ContribuicaoCreate,
    ContribuicaoUpdate,
    criar_contribuicao,
    delete_contribuicao,
    editar_contribuicao,
    listar_minhas_contribuicoes,
)
from backend.app.api.schema.SubmissaoBase import Submissao


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


def test_criar_contribuicao_define_autor():
    session = MagicMock()
    data = ContribuicaoCreate(
        disciplina_id=1,
        tipo="artigo",
        origem="UnB",
        conteudo_id=2,
        payload="conteúdo",
        autor_id=99,
    )

    response = criar_contribuicao(data, session, user())

    assert response.autor_id == 7
    session.commit.assert_called_once()


def test_listar_minhas_contribuicoes_retorna_lista():
    session = MagicMock()
    execution = MagicMock()
    execution.all.return_value = []
    session.exec.return_value = execution

    assert listar_minhas_contribuicoes(session, user()) == []


def test_excluir_contribuicao_de_outro_usuario():
    session = MagicMock()
    item = contribution()
    item.id = 1
    item.autor_id = 99
    session.get.return_value = item

    with pytest.raises(HTTPException) as error:
        delete_contribuicao(1, user(), session)

    assert error.value.status_code == 403


def test_editar_contribuicao_atualiza_payload():
    session = MagicMock()
    item = contribution()
    item.id = 1
    session.get.return_value = item

    response = editar_contribuicao(
        1,
        ContribuicaoUpdate(payload="novo conteúdo"),
        session,
        user(),
    )

    assert response.payload == "novo conteúdo"
    assert response.estado == "pendente"
    session.commit.assert_called_once()


def test_contribuicao_rejeita_estado_invalido():
    with pytest.raises(ValueError, match="status"):
        Submissao.validate_estado("invalido")
