from fastapi import FastAPI

from backend.app.api.schema.disciplina import disciplina_router, crud_disciplina_router
from backend.app.api.schema.publicacao_institucional import publicacao_router
app = FastAPI()

app.include_router(router=publicacao_router,prefix="/publicacao")
app.include_router(router = disciplina_router,prefix="/cursos")
app.include_router(router = crud_disciplina_router,prefix ="/link_temporario") # para debug