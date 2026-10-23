import asyncio
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from backend.tests.test_config import test_engine
from backend.app.api.schema.publicacao_institucional import (
    PublicacaoInstitucional,
    PublicacaoInstitucionalCreate,
    PublicacaoInstitucionalGet,
    PublicacaoInstitucionalBase,
    verificar_fonte_oficial,
    get_lista_publicacao,
    get_publicacao,
    post_publicacao,
)


def publication_payload():
    return PublicacaoInstitucionalCreate(
        fonte_id=1,
        titulo="Edital",
        resumo="Resumo do edital",
        categoria="ensino",
        unidade_responsavel="UnB",
        url_oficial="https://unb.br/edital",
    )


def test_verificar_fonte_oficial():
    assert verificar_fonte_oficial(None) == "sem fonte"
    assert verificar_fonte_oficial("/") == "sem fonte"
    assert verificar_fonte_oficial("https://unb.br") == "https://unb.br"


def test_estado_da_publicacao_usa_ativa_com_valor_nulo():
    assert PublicacaoInstitucionalBase.validar_estado(None) == "ativa"


def test_estado_da_publicacao_invalido():
    with pytest.raises(ValueError, match="estado deve ser um dos seguintes"):
        PublicacaoInstitucionalBase.validar_estado("inexistente")


def test_propriedade_id_da_publicacao():
    publication = PublicacaoInstitucional(publicacao_id=10, **publication_payload().model_dump())

    assert publication.id == 10
    publication.id = 11
    assert publication.publicacao_id == 11


def test_propriedade_id_da_publicacao_get():
    publication = PublicacaoInstitucionalGet(
        publicacao_id=10,
        fonte_id=1,
        titulo="Edital",
        resumo="Resumo",
        categoria="ensino",
        unidade_responsavel="UnB",
    )

    assert publication.id == 10


def test_buscar_publicacao_existente():
    publication = PublicacaoInstitucional(
        publicacao_id=1,
        fonte_id=1,
        titulo="Edital",
        resumo="Resumo",
        categoria="ensino",
        unidade_responsavel="UnB",
        url_oficial="https://unb.br/edital",
    )
    session = MagicMock()
    session.get.return_value = publication

    response = asyncio.run(get_publicacao(1, session))

    assert response.publicacao_id == 1


def test_buscar_publicacao_inexistente():
    session = MagicMock()
    session.get.return_value = None

    with pytest.raises(HTTPException) as error:
        asyncio.run(get_publicacao(99, session))

    assert error.value.status_code == 404


def test_listar_publicacoes():
    session = MagicMock()
    execution = MagicMock()
    execution.all.return_value = []
    session.exec.return_value = execution

    assert asyncio.run(get_lista_publicacao(session)) == []


def test_criar_publicacao():
    session = MagicMock()

    response = asyncio.run(post_publicacao(publication_payload(), session))

    assert response.titulo == "Edital"
    session.add.assert_called_once()
    session.commit.assert_called_once()
