from fastapi import FastAPI

from backend.app.api.schema.disciplina import disciplina_router, crud_disciplina_router
from backend.app.api.schema.publicacao_institucional import publicacao_router
from backend.app.api.schema.Contribuicao import routerContribuicao
from backend.app.api.schema.usuario import router_usuario
app = FastAPI()

app.include_router(router=publicacao_router,prefix="/publicacao")
app.include_router(router = disciplina_router,prefix="/cursos")
app.include_router(router = crud_disciplina_router,prefix ="/link_temporario") # para debug
app.include(router = routerContribuicao,prefix = "/api/v1/contribuicoes")
app.include(router = router_usuario)