from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

from backend.app.api.routers.academico import router as academico_router
from backend.app.api.routers.auth import router as auth_router
from backend.app.api.routers.contribuicoes import router as contribuicoes_router
from backend.app.api.routers.moderacao import router as moderacao_router

api_router.include_router(academico_router)
api_router.include_router(auth_router)
api_router.include_router(contribuicoes_router)
api_router.include_router(moderacao_router)
