import asyncio
from contextlib import asynccontextmanager
import logging
import os

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select

from backend.app.api.errors import configurar_tratamento_de_erros
from backend.app.api.router import api_router
from backend.app.crawler.crawlerCurriculo import coletar_e_sincronizar_curriculos
from backend.app.crawler.crawlerDisciplina import coletar_e_salvar_disciplinas
from backend.app.crawler.crawlercursos import coletar_e_salvar_cursos
from backend.app.db import create_db_and_tables, engine
from backend.app.domain import Curso, Disciplina
from backend.app.services.usuario_service import garantir_usuario_admin


logger = logging.getLogger(__name__)


def _garantir_admin_configurado() -> None:
    configuracoes = {
        "ADMIN_NAME": os.getenv("ADMIN_NAME") or None,
        "ADMIN_EMAIL": os.getenv("ADMIN_EMAIL") or None,
        "ADMIN_PASSWORD": os.getenv("ADMIN_PASSWORD") or None,
    }
    presentes = [valor is not None for valor in configuracoes.values()]
    if not any(presentes):
        return
    if not all(presentes):
        raise RuntimeError(
            "ADMIN_NAME, ADMIN_EMAIL e ADMIN_PASSWORD devem ser "
            "configurados juntos."
        )
    if len(configuracoes["ADMIN_PASSWORD"]) < 8:
        raise RuntimeError("ADMIN_PASSWORD deve ter pelo menos 8 caracteres.")

    with Session(engine) as session:
        garantir_usuario_admin(
            session,
            nome=configuracoes["ADMIN_NAME"],
            email=configuracoes["ADMIN_EMAIL"],
            senha=configuracoes["ADMIN_PASSWORD"],
        )
    logger.info("Conta administrativa configurada para %s.", configuracoes["ADMIN_EMAIL"])


async def _carregar_dados_iniciais() -> None:
    try:
        with Session(engine) as session:
            curso_existente = session.exec(select(Curso.id).limit(1)).first()
            if curso_existente is None:
                quantidade = await coletar_e_salvar_cursos(session)
                logger.info(
                    "Carga inicial de cursos concluida: %s cursos.",
                    quantidade,
                )

            disciplina_existente = session.exec(
                select(Disciplina.id).limit(1)
            ).first()
            if disciplina_existente is None:
                quantidade = await coletar_e_salvar_disciplinas(session)
                logger.info(
                    "Carga inicial de disciplinas concluida: %s disciplinas.",
                    quantidade,
                )
                quantidade = await coletar_e_sincronizar_curriculos(session)
                logger.info(
                    "Estruturas curriculares do Gama aplicadas: %s disciplinas.",
                    quantidade,
                )
    except (httpx.HTTPError, SQLAlchemyError, RuntimeError):
        logger.exception("Falha na carga inicial dos dados academicos.")


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    _garantir_admin_configurado()
    tarefa_carga = asyncio.create_task(_carregar_dados_iniciais())
    try:
        yield
    finally:
        if not tarefa_carga.done():
            tarefa_carga.cancel()
        try:
            await tarefa_carga
        except asyncio.CancelledError:
            logger.info("Carga inicial interrompida durante o encerramento.")


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
