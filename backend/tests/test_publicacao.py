from datetime import datetime
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
from backend.app.api.schema.usuario import get_current_user, verificar_admin
from backend.app.services.publicacao_service import (
    _contains,
    detalhar_publicacao,
    listar_publicacoes,
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
    with pytest.raises(HTTPException) as missing_url:
        verificar_fonte_oficial(None)
    assert missing_url.value.status_code == 422

    with pytest.raises(HTTPException) as invalid_url:
        verificar_fonte_oficial("/")
    assert invalid_url.value.status_code == 422

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

    response = get_publicacao(1, session)

    assert response.publicacao_id == 1


def test_buscar_publicacao_inexistente():
    session = MagicMock()
    session.get.return_value = None

    with pytest.raises(HTTPException) as error:
        get_publicacao(99, session)

    assert error.value.status_code == 404


def test_listar_publicacoes():
    session = MagicMock()
    execution = MagicMock()
    execution.all.return_value = []
    session.exec.return_value = execution

    assert get_lista_publicacao(session) == {"itens": []}


def test_criar_publicacao():
    session = MagicMock()
    admin = MagicMock()

    response = post_publicacao(publication_payload(), session, admin)

    assert response.titulo == "Edital"
    session.add.assert_called_once()
    session.commit.assert_called_once()


def current_user(perfil):
    return get_current_user(
        email="admin@unb.br",
        nome="Administrador",
        status="Online",
        ativo=True,
        id=1,
        perfil=perfil,
    )


def test_verificar_admin_permite_administrador():
    usuario = current_user("administrador")

    assert verificar_admin(usuario) is usuario


def test_verificar_admin_rejeita_usuario_nao_autorizado():
    usuario = current_user("usuario")

    with pytest.raises(HTTPException) as error:
        verificar_admin(usuario)

    assert error.value.status_code == 403


def publication_model(publicacao_id=1, **overrides):
    values = {
        "publicacao_id": publicacao_id,
        "titulo": "Edital",
        "resumo": "Resumo",
        "categoria": "ensino",
        "unidade_responsavel": "UnB",
        "url_oficial": "https://unb.br/edital",
    }
    values.update(overrides)
    return PublicacaoInstitucional(**values)


def mocked_listing_session():
    session = MagicMock()
    execution = MagicMock()
    execution.all.return_value = []
    session.exec.return_value = execution
    return session


def test_contains_escapa_caracteres_especiais():
    assert _contains(r"edital\_%") == r"%edital\\\_\%%"


def test_listar_publicacoes_rejeita_prazo_invalido():
    with pytest.raises(HTTPException) as error:
        listar_publicacoes(mocked_listing_session(), prazo_fim="invalido")

    assert error.value.status_code == 422
    assert error.value.detail["codigo"] == "VALIDACAO"


def test_listar_publicacoes_aplica_filtros():
    session = mocked_listing_session()

    result = listar_publicacoes(
        session,
        termo=" edital ",
        categoria="ensino",
        unidade=" UnB ",
        curso_id=7,
        estado="ativa",
    )

    assert result == []
    session.exec.assert_called_once()


@pytest.mark.parametrize("prazo_fim", ["Sem informação", "ativa", "inativa"])
def test_listar_publicacoes_aplica_filtro_de_prazo(prazo_fim):
    session = mocked_listing_session()

    assert listar_publicacoes(
        session,
        prazo_fim=prazo_fim,
        agora=datetime(2026, 1, 1),
    ) == []
    session.exec.assert_called_once()


def test_listar_publicacoes_ignora_filtros_vazios():
    session = mocked_listing_session()

    assert listar_publicacoes(
        session,
        termo=" ",
        categoria=" ",
        unidade=" ",
        estado=" ",
    ) == []
    session.exec.assert_called_once()


def test_detalhar_publicacao_existente():
    session = MagicMock()
    session.get.return_value = publication_model()

    result = detalhar_publicacao(1, session)

    assert result.publicacao_id == 1


def test_detalhar_publicacao_inexistente():
    session = MagicMock()
    session.get.return_value = None

    with pytest.raises(HTTPException) as error:
        detalhar_publicacao(99, session)

    assert error.value.status_code == 404
    assert error.value.detail["codigo"] == "NAO_ENCONTRADO"
