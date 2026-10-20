from fastapi import FastAPI
from contextlib import asynccontextmanager  

from backend.app.api.errors import configurar_tratamento_de_erros
from backend.app.api.schema import (
    publicacao_router,
    disciplina_router,
    crud_disciplina_router,
    routerContribuicao,
    router_usuario,
)
from backend.app.api.search import routerBusca as search_router
#from backend.app.api.administracao import router_administracao
from backend.app.db import create_db_and_tables

@asynccontextmanager
async def lifespan(app : FastAPI):
    create_db_and_tables()
    yield


def criar_aplicacao() -> FastAPI:
    aplicacao = FastAPI(
        title="UNB CORE API",
        description=(
            "API da Base de Conhecimento colaborativa e Editais"
            "Central de Editais e Avisos da UnB."
        ),
        version="0.1.0",
        lifespan=lifespan
    )

    configurar_tratamento_de_erros(aplicacao)

    return aplicacao


app = criar_aplicacao()

app.include_router(router=publicacao_router,prefix="/publicacao",tags = ["publicacao"])
app.include_router(router = disciplina_router,prefix="/cursos",tags = ["cursos"])
app.include_router(router = crud_disciplina_router,prefix ="/link_temporario",tags = ["CRUD disciplina"]) # para debug
app.include_router(router = routerContribuicao,prefix = "/api/v1/contribuicoes",tags = ["Contribuicao"])
app.include_router(router = router_usuario,tags = ["Usuario"])
app.include_router(router=search_router, tags = ["busca"])
# app.include_router(router=router_administracao)

