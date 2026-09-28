import logging
from collections.abc import Mapping
from enum import StrEnum
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class CodigoErro(StrEnum):
    VALIDACAO = "VALIDACAO"
    NAO_ENCONTRADO = "NAO_ENCONTRADO"
    NAO_AUTENTICADO = "NAO_AUTENTICADO"
    PERMISSAO_NEGADA = "PERMISSAO_NEGADA"
    FONTE_INDISPONIVEL = "FONTE_INDISPONIVEL"
    ERRO_INTERNO = "ERRO_INTERNO"


class DetalheErro(BaseModel):
    codigo: CodigoErro
    mensagem: str
    id: str


class RespostaErro(BaseModel):
    erro: DetalheErro


class ErroAPI(Exception):
    def __init__(
        self,
        *,
        codigo: CodigoErro,
        mensagem: str,
        status_code: int,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.mensagem = mensagem
        self.status_code = status_code
        self.headers = dict(headers or {})


class ErroValidacao(ErroAPI):
    def __init__(self, mensagem: str) -> None:
        super().__init__(
            codigo=CodigoErro.VALIDACAO,
            mensagem=mensagem,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class NaoEncontrado(ErroAPI):
    def __init__(self, mensagem: str = "O recurso solicitado não foi encontrado.") -> None:
        super().__init__(
            codigo=CodigoErro.NAO_ENCONTRADO,
            mensagem=mensagem,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class NaoAutenticado(ErroAPI):
    def __init__(
        self,
        mensagem: str = "É necessário entrar em uma conta para realizar esta ação.",
    ) -> None:
        super().__init__(
            codigo=CodigoErro.NAO_AUTENTICADO,
            mensagem=mensagem,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissaoNegada(ErroAPI):
    def __init__(
        self,
        mensagem: str = "Você não possui permissão para executar esta ação.",
    ) -> None:
        super().__init__(
            codigo=CodigoErro.PERMISSAO_NEGADA,
            mensagem=mensagem,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class FonteIndisponivel(ErroAPI):
    def __init__(
        self,
        mensagem: str = (
            "A fonte oficial está temporariamente indisponível. "
            "Tente novamente mais tarde."
        ),
    ) -> None:
        super().__init__(
            codigo=CodigoErro.FONTE_INDISPONIVEL,
            mensagem=mensagem,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def _criar_resposta(
    *,
    codigo: CodigoErro,
    mensagem: str,
    status_code: int,
    identificador: str | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    identificador = identificador or str(uuid4())
    response_headers = dict(headers or {})
    response_headers["X-Error-ID"] = identificador

    conteudo = RespostaErro(
        erro=DetalheErro(
            codigo=codigo,
            mensagem=mensagem,
            id=identificador,
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=conteudo.model_dump(mode="json"),
        headers=response_headers,
    )


def _codigo_para_status(status_code: int) -> CodigoErro:
    if status_code == status.HTTP_401_UNAUTHORIZED:
        return CodigoErro.NAO_AUTENTICADO

    if status_code == status.HTTP_403_FORBIDDEN:
        return CodigoErro.PERMISSAO_NEGADA

    if status_code == status.HTTP_404_NOT_FOUND:
        return CodigoErro.NAO_ENCONTRADO

    if status_code in {
        status.HTTP_502_BAD_GATEWAY,
        status.HTTP_503_SERVICE_UNAVAILABLE,
        status.HTTP_504_GATEWAY_TIMEOUT,
    }:
        return CodigoErro.FONTE_INDISPONIVEL

    if 400 <= status_code < 500:
        return CodigoErro.VALIDACAO

    return CodigoErro.ERRO_INTERNO


def _mensagem_padrao(codigo: CodigoErro) -> str:
    mensagens = {
        CodigoErro.VALIDACAO: (
            "Os dados informados são inválidos. "
            "Revise os campos e tente novamente."
        ),
        CodigoErro.NAO_ENCONTRADO: (
            "O recurso solicitado não foi encontrado. "
            "Verifique o identificador informado."
        ),
        CodigoErro.NAO_AUTENTICADO: (
            "É necessário entrar em uma conta para realizar esta ação."
        ),
        CodigoErro.PERMISSAO_NEGADA: (
            "Você não possui permissão para executar esta ação."
        ),
        CodigoErro.FONTE_INDISPONIVEL: (
            "A fonte oficial está temporariamente indisponível. "
            "Tente novamente mais tarde."
        ),
        CodigoErro.ERRO_INTERNO: (
            "Não foi possível concluir a solicitação. "
            "Tente novamente mais tarde."
        ),
    }
    return mensagens[codigo]


async def tratar_erro_api(_: Request, exc: ErroAPI) -> JSONResponse:
    return _criar_resposta(
        codigo=exc.codigo,
        mensagem=exc.mensagem,
        status_code=exc.status_code,
        headers=exc.headers,
    )


async def tratar_erro_validacao(
    _: Request,
    __: RequestValidationError,
) -> JSONResponse:
    # Não devolve o corpo recebido ou os valores rejeitados, evitando expor senhas.
    return _criar_resposta(
        codigo=CodigoErro.VALIDACAO,
        mensagem=(
            "Os dados informados são inválidos. "
            "Revise os campos obrigatórios e os formatos utilizados."
        ),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def tratar_http_exception(
    _: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    codigo = _codigo_para_status(exc.status_code)

    mensagem = (
        exc.detail
        if isinstance(exc.detail, str)
        and exc.detail.strip()
        and exc.status_code < 500
        else _mensagem_padrao(codigo)
    )

    return _criar_resposta(
        codigo=codigo,
        mensagem=mensagem,
        status_code=exc.status_code,
        headers=exc.headers,
    )


async def tratar_erro_interno(_: Request, exc: Exception) -> JSONResponse:
    identificador = str(uuid4())

    # Registra apenas o tipo e o identificador. A mensagem da exceção pode
    # conter dados sensíveis originados da requisição.
    logger.error(
        "Erro interno não tratado. id=%s tipo=%s",
        identificador,
        type(exc).__name__,
    )

    return _criar_resposta(
        codigo=CodigoErro.ERRO_INTERNO,
        mensagem=_mensagem_padrao(CodigoErro.ERRO_INTERNO),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        identificador=identificador,
    )


def configurar_tratamento_de_erros(app: FastAPI) -> None:
    app.add_exception_handler(ErroAPI, tratar_erro_api)
    app.add_exception_handler(RequestValidationError, tratar_erro_validacao)
    app.add_exception_handler(StarletteHTTPException, tratar_http_exception)
    app.add_exception_handler(Exception, tratar_erro_interno)