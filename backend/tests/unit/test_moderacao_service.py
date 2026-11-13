from unittest.mock import MagicMock

import pytest

from backend.app.api.errors import ErroValidacao, NaoEncontrado
from backend.app.api.schemas.moderacao import DecisaoModeracao
from backend.app.domain import (
    ConteudoAcademico,
    EstadoContribuicao,
    EstadoConteudo,
    TipoConteudo,
)
from backend.app.services.moderacao_service import (
    decidir_contribuicao,
    listar_para_moderacao,
    publicar_conteudo,
)


def test_lista_contribuicoes_pendentes(session):
    expected = [object()]
    session.exec.return_value.all.return_value = expected

    assert listar_para_moderacao(session) == expected


@pytest.mark.parametrize(
    ("decision", "state"),
    [
        (DecisaoModeracao.AJUSTES, EstadoContribuicao.AJUSTES),
        (DecisaoModeracao.REJEITAR, EstadoContribuicao.REJEITADA),
        (DecisaoModeracao.ARQUIVAR, EstadoContribuicao.ARQUIVADA),
    ],
)
def test_decide_contribuicao_pendente(session, contribuicao, decision, state):
    session.get.return_value = contribuicao

    result = decidir_contribuicao(session, 1, decision, "motivo")

    assert result.estado == state
    assert result.justificativa_moderacao == "motivo"


def test_aprovacao_cria_novo_conteudo(session, contribuicao):
    contribuicao.conteudo_id = None
    session.get.return_value = contribuicao

    result = decidir_contribuicao(
        session,
        1,
        DecisaoModeracao.APROVAR,
        None,
    )

    assert result.estado == EstadoContribuicao.APROVADA
    assert session.add.call_count == 2


def test_rejeita_contribuicao_inexistente(session):
    session.get.return_value = None

    with pytest.raises(NaoEncontrado):
        decidir_contribuicao(
            session,
            1,
            DecisaoModeracao.APROVAR,
            None,
        )


def test_rejeita_transicao_invalida(session, contribuicao):
    contribuicao.estado = EstadoContribuicao.AJUSTES
    session.get.return_value = contribuicao

    with pytest.raises(ErroValidacao):
        decidir_contribuicao(
            session,
            1,
            DecisaoModeracao.APROVAR,
            None,
        )


def test_ajuste_exige_justificativa(session, contribuicao):
    session.get.return_value = contribuicao

    with pytest.raises(ErroValidacao):
        decidir_contribuicao(
            session,
            1,
            DecisaoModeracao.AJUSTES,
            " ",
        )


def test_publica_conteudo_existente(session, contribuicao):
    content = ConteudoAcademico(
        id=4,
        disciplina_id=1,
        tipo=TipoConteudo.DICA,
        titulo="Antigo",
        corpo_ou_url="antigo",
        autor_id=1,
        estado=EstadoConteudo.ARQUIVADO,
    )
    contribuicao.conteudo_id = 4
    session.get.return_value = content

    result = publicar_conteudo(session, contribuicao)

    assert result.estado == EstadoConteudo.PUBLICADO
    assert result.titulo == contribuicao.titulo


def test_publicacao_rejeita_conteudo_relacionado_inexistente(session, contribuicao):
    contribuicao.conteudo_id = 4
    session.get.return_value = None

    with pytest.raises(NaoEncontrado):
        publicar_conteudo(session, contribuicao)
