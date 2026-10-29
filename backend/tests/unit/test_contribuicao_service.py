from unittest.mock import MagicMock

import pytest

from backend.app.api.errors import ErroValidacao, NaoEncontrado
from backend.app.services.contribuicao_service import (
    criar_contribuicao,
    listar_contribuicoes_do_usuario,
)


def test_cria_contribuicao(session, usuario, disciplina):
    session.get.return_value = disciplina
    data = {
        "disciplina_id": 1,
        "conteudo_id": None,
        "tipo": "resumo",
        "titulo": "Resumo",
        "corpo_ou_url": "Texto",
    }

    contribution = criar_contribuicao(session, usuario, data)

    assert contribution.autor_id == usuario.id
    session.commit.assert_called_once()


def test_rejeita_disciplina_inexistente(session, usuario):
    session.get.return_value = None

    with pytest.raises(NaoEncontrado):
        criar_contribuicao(session, usuario, {
            "disciplina_id": 99,
            "tipo": "resumo",
            "titulo": "Resumo",
            "corpo_ou_url": "Texto",
        })


def test_rejeita_conteudo_relacionado_inexistente(session, usuario, disciplina):
    session.get.side_effect = [disciplina, None]

    with pytest.raises(ErroValidacao):
        criar_contribuicao(session, usuario, {
            "disciplina_id": 1,
            "conteudo_id": 99,
            "tipo": "resumo",
            "titulo": "Resumo",
            "corpo_ou_url": "Texto",
        })


def test_lista_contribuicoes_do_usuario(session, usuario):
    expected = [object()]
    session.exec.return_value.all.return_value = expected

    assert listar_contribuicoes_do_usuario(session, usuario) == expected
