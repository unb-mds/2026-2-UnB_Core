from fastapi import FastAPI

from backend.app.api.errors import configurar_tratamento_de_erros


def criar_aplicacao() -> FastAPI:
    aplicacao = FastAPI(
        title="UNB CORE API",
        description=(
            "API da Base de Conhecimento colaborativa e Editais"
            "Central de Editais e Avisos da UnB."
        ),
        version="0.1.0",
    )

    configurar_tratamento_de_erros(aplicacao)

    return aplicacao


app = criar_aplicacao()