from unittest.mock import MagicMock

import pytest

from backend.app.api.errors import ErroValidacao, NaoEncontrado
from backend.app.domain import (
    Contribuicao,
    Disciplina,
    Usuario,
)
from backend.app.services.contribuicao_service import (
    criar_contribuicao,
    listar_contribuicoes_do_usuario,
    obter_contribuicao_do_usuario,
)


def test_criar_contribuicao_rejeita_disciplina_inativa() -> None:
    session = MagicMock()
    session.get.return_value = Disciplina(
        id=1,
        curso_id=1,
        codigo="CIC-1",
        nome="Computação",
        ativo=False,
    )

    with pytest.raises(NaoEncontrado):
        criar_contribuicao(
            session,
            Usuario(id=1, nome="Ana", email="ana@example.com", senha_hash="hash"),
            {"disciplina_id": 1, "tipo": "resumo"},
        )


def test_criar_contribuicao_rejeita_conteudo_inexistente() -> None:
    session = MagicMock()
    session.get.side_effect = [
        Disciplina(
            id=1,
            curso_id=1,
            codigo="CIC-1",
            nome="Computação",
        ),
        None,
    ]

    with pytest.raises(ErroValidacao):
        criar_contribuicao(
            session,
            Usuario(id=1, nome="Ana", email="ana@example.com", senha_hash="hash"),
            {
                "disciplina_id": 1,
                "conteudo_id": 4,
                "tipo": "resumo",
                "titulo": "Resumo",
                "corpo_ou_url": "Conteúdo",
            },
        )


def test_criar_e_listar_contribuicoes() -> None:
    session = MagicMock()
    disciplina = Disciplina(
        id=1,
        curso_id=1,
        codigo="CIC-1",
        nome="Computação",
    )
    session.get.return_value = disciplina
    contribuicao = criar_contribuicao(
        session,
        Usuario(id=1, nome="Ana", email="ana@example.com", senha_hash="hash"),
        {
            "disciplina_id": 1,
            "tipo": "resumo",
            "titulo": "Resumo",
            "corpo_ou_url": "Conteúdo",
        },
    )
    session.exec.return_value.all.return_value = [contribuicao]

    assert listar_contribuicoes_do_usuario(
        session,
        Usuario(id=1, nome="Ana", email="ana@example.com", senha_hash="hash"),
    ) == [contribuicao]
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(contribuicao)


def test_obter_contribuicao_do_usuario_retorna_contribuicao() -> None:
    session = MagicMock()
    usuario = MagicMock(id=1)
    contribuicao = Contribuicao(
        id=3,
        autor_id=1,
        disciplina_id=1,
        tipo="resumo",
        titulo="Resumo",
        corpo_ou_url="Conteúdo",
    )
    session.exec.return_value.first.return_value = contribuicao

    resultado = obter_contribuicao_do_usuario(session, usuario, 3)

    assert resultado is contribuicao


def test_obter_contribuicao_do_usuario_lanca_404_se_nao_encontrada() -> None:
    session = MagicMock()
    session.exec.return_value.first.return_value = None

    with pytest.raises(NaoEncontrado):
        obter_contribuicao_do_usuario(session, MagicMock(id=1), 3)


def test_obter_contribuicao_do_usuario_rejeita_outro_autor() -> None:
    session = MagicMock()
    session.exec.return_value.first.return_value = Contribuicao(
        id=3,
        autor_id=2,
        disciplina_id=1,
        tipo="resumo",
        titulo="Resumo",
        corpo_ou_url="Conteúdo",
    )

    with pytest.raises(ErroValidacao):
        obter_contribuicao_do_usuario(session, MagicMock(id=1), 3)
