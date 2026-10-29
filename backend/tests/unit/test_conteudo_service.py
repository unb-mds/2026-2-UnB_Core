from unittest.mock import MagicMock

import pytest

from backend.app.api.errors import NaoEncontrado
from backend.app.domain import EstadoConteudo, TipoConteudo
from backend.app.services.conteudo_service import (
    listar_conteudos_publicados,
    obter_conteudo_publicado,
    validar_disciplina_do_curso,
)


def test_lista_conteudo_publicado(session):
    expected = [object()]
    session.exec.return_value.all.return_value = expected

    assert listar_conteudos_publicados(session, 1) == expected


def test_lista_conteudo_publicado_filtrado_por_tipo(session):
    expected = [object()]
    session.exec.return_value.all.return_value = expected

    assert listar_conteudos_publicados(
        session,
        1,
        TipoConteudo.DICA,
    ) == expected


def test_obtem_conteudo_publicado(session):
    content = MagicMock(estado=EstadoConteudo.PUBLICADO)
    session.get.return_value = content

    assert obter_conteudo_publicado(session, 1) is content


@pytest.mark.parametrize("content", [None, MagicMock(estado=EstadoConteudo.ARQUIVADO)])
def test_rejeita_conteudo_inexistente_ou_arquivado(session, content):
    session.get.return_value = content

    with pytest.raises(NaoEncontrado):
        obter_conteudo_publicado(session, 1)


def test_valida_disciplina_ativa_do_curso(session, disciplina):
    session.get.return_value = disciplina

    assert validar_disciplina_do_curso(session, 1, 10) is disciplina


def test_rejeita_disciplina_invalida_do_curso(session, disciplina):
    disciplina.ativo = False
    session.get.return_value = disciplina

    with pytest.raises(NaoEncontrado):
        validar_disciplina_do_curso(session, 1, 10)
