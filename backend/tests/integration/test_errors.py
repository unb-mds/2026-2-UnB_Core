from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from backend.app.api.errors import (
    ErroValidacao,
    FonteIndisponivel,
    NaoAutenticado,
    NaoEncontrado,
    PermissaoNegada,
)
from backend.app.db import get_session
from backend.app.main import app
from backend.tests.integration.test_auth_contribuicoes import (
    engine,
    session_override,
)


@asynccontextmanager
async def no_lifespan(_app):
    yield


app.dependency_overrides[get_session] = session_override
app.router.lifespan_context = no_lifespan


@app.get("/__test__/erro/nao-autenticado")
def erro_nao_autenticado():
    raise NaoAutenticado()


@app.get("/__test__/erro/permissao-negada")
def erro_permissao_negada():
    raise PermissaoNegada()


@app.get("/__test__/erro/nao-encontrado")
def erro_nao_encontrado():
    raise NaoEncontrado()


@app.get("/__test__/erro/fonte-indisponivel")
def erro_fonte_indisponivel():
    raise FonteIndisponivel()


@app.get("/__test__/erro/validacao")
def erro_validacao():
    raise ErroValidacao("Dados inválidos.")


@app.get("/__test__/erro/interno")
def erro_interno():
    raise RuntimeError("erro interno de teste")


@app.get("/__test__/erro/http/{status_code}")
def erro_http(status_code: int):
    from starlette.exceptions import HTTPException

    raise HTTPException(status_code=status_code, detail="")


def setup_function() -> None:
    app.dependency_overrides[get_session] = session_override
    app.router.lifespan_context = no_lifespan
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def obter_erro(client, path: str):
    response = client.get(path)

    assert response.headers["X-Error-ID"]
    assert "erro" in response.json()
    return response.json()["erro"]


def test_trata_erros_de_autenticacao_e_permissao():
    with TestClient(app, raise_server_exceptions=False) as client:
        nao_autenticado = obter_erro(
            client,
            "/__test__/erro/nao-autenticado",
        )
        permissao_negada = obter_erro(
            client,
            "/__test__/erro/permissao-negada",
        )

    assert nao_autenticado["codigo"] == "NAO_AUTENTICADO"
    assert permissao_negada["codigo"] == "PERMISSAO_NEGADA"


def test_trata_erro_de_recurso_inexistente():
    with TestClient(app, raise_server_exceptions=False) as client:
        erro = obter_erro(client, "/__test__/erro/nao-encontrado")

    assert erro["codigo"] == "NAO_ENCONTRADO"


def test_trata_erro_de_fonte_indisponivel():
    with TestClient(app, raise_server_exceptions=False) as client:
        erro = obter_erro(client, "/__test__/erro/fonte-indisponivel")

    assert erro["codigo"] == "FONTE_INDISPONIVEL"


def test_trata_erro_de_validacao():
    with TestClient(app, raise_server_exceptions=False) as client:
        erro = obter_erro(client, "/__test__/erro/validacao")

    assert erro["codigo"] == "VALIDACAO"
    assert erro["mensagem"] == "Dados inválidos."


def test_trata_validacao_de_requisicao():
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/api/v1/auth/cadastro",
            json={"email": "invalido"},
        )

    assert response.status_code == 422
    assert response.json()["erro"]["codigo"] == "VALIDACAO"


def test_trata_status_http_e_mensagens_padrao():
    with TestClient(app, raise_server_exceptions=False) as client:
        respostas = {
            status_code: obter_erro(
                client,
                f"/__test__/erro/http/{status_code}",
            )
            for status_code in (400, 401, 403, 404, 502, 503, 504, 500)
        }

    assert respostas[400]["codigo"] == "VALIDACAO"
    assert respostas[401]["codigo"] == "NAO_AUTENTICADO"
    assert respostas[403]["codigo"] == "PERMISSAO_NEGADA"
    assert respostas[404]["codigo"] == "NAO_ENCONTRADO"
    assert respostas[502]["codigo"] == "FONTE_INDISPONIVEL"
    assert respostas[503]["codigo"] == "FONTE_INDISPONIVEL"
    assert respostas[504]["codigo"] == "FONTE_INDISPONIVEL"
    assert respostas[500]["codigo"] == "ERRO_INTERNO"


def test_trata_erro_interno_sem_expor_detalhes():
    with TestClient(app, raise_server_exceptions=False) as client:
        erro = obter_erro(client, "/__test__/erro/interno")

    assert erro["codigo"] == "ERRO_INTERNO"
    assert "erro interno de teste" not in erro["mensagem"]
