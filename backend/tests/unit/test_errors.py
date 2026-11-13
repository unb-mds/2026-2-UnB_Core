import asyncio
from unittest.mock import MagicMock

import pytest
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.api.errors import (
    CodigoErro,
    ErroValidacao,
    FonteIndisponivel,
    NaoAutenticado,
    _codigo_para_status,
    _criar_resposta,
    _mensagem_padrao,
    tratar_erro_api,
    tratar_erro_interno,
    tratar_erro_validacao,
    tratar_http_exception,
    configurar_tratamento_de_erros,
)


def test_cria_resposta_de_erro():
    response = _criar_resposta(
        codigo=CodigoErro.VALIDACAO,
        mensagem="inválido",
        status_code=422,
        identificador="abc",
    )

    assert response.status_code == 422
    assert response.headers["X-Error-ID"] == "abc"


@pytest.mark.parametrize(
    ("http_status", "code"),
    [
        (401, CodigoErro.NAO_AUTENTICADO),
        (403, CodigoErro.PERMISSAO_NEGADA),
        (404, CodigoErro.NAO_ENCONTRADO),
        (503, CodigoErro.FONTE_INDISPONIVEL),
        (422, CodigoErro.VALIDACAO),
        (500, CodigoErro.ERRO_INTERNO),
    ],
)
def test_mapeia_status_para_codigo_de_erro(http_status, code):
    assert _codigo_para_status(http_status) == code


def test_mensagens_padrao_exist():
    for code in CodigoErro:
        assert _mensagem_padrao(code)


def test_tratador_de_erro_api():
    response = asyncio.run(tratar_erro_api(
        MagicMock(),
        ErroValidacao("inválido"),
    ))

    assert response.status_code == 422


def test_erro_de_fonte_indisponivel():
    error = FonteIndisponivel()

    assert error.status_code == 503


def test_configura_todos_os_tratadores_de_erro():
    app = MagicMock()

    configurar_tratamento_de_erros(app)

    assert app.add_exception_handler.call_count == 4


def test_tratador_de_erro_de_validacao():
    response = asyncio.run(tratar_erro_validacao(
        MagicMock(),
        RequestValidationError([]),
    ))

    assert response.status_code == 422


def test_tratador_de_erro_http():
    response = asyncio.run(tratar_http_exception(
        MagicMock(),
        StarletteHTTPException(status_code=404, detail="não encontrado"),
    ))

    assert response.status_code == 404


def test_tratador_http_usa_mensagem_generica_para_erro_do_servidor():
    response = asyncio.run(tratar_http_exception(
        MagicMock(),
        StarletteHTTPException(status_code=500, detail="segredo"),
    ))

    assert response.status_code == 500


def test_tratador_de_erro_interno():
    response = asyncio.run(
        tratar_erro_interno(MagicMock(), RuntimeError("erro"))
    )

    assert response.status_code == 500
