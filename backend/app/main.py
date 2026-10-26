from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.errors import configurar_tratamento_de_erros
from backend.app.api.router import api_router
from backend.app.db import create_db_and_tables

@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


def criar_aplicacao() -> FastAPI:
    aplicacao = FastAPI(
        title="UNB CORE API",
        description="API acadêmica colaborativa da Base de Conhecimento do UNB CORE.",
        version="0.1.0",
        lifespan=lifespan,
    )
    configurar_tratamento_de_erros(aplicacao)
    aplicacao.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    aplicacao.include_router(api_router)
    return aplicacao


app = criar_aplicacao()
