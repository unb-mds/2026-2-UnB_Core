from backend.app.crawler.crawlerDisciplina import (
    DisciplinaColetada,
    coletar_disciplinas,
    coletar_e_salvar_disciplinas,
    extrair_disciplinas_html,
    salvar_disciplinas,
)
from backend.app.crawler.crawlercursos import (
    CursoColetado,
    coletar_cursos,
    coletar_e_salvar_cursos,
    extrair_cursos_html,
    salvar_cursos,
)

__all__ = [
    "DisciplinaColetada",
    "coletar_disciplinas",
    "coletar_e_salvar_disciplinas",
    "extrair_disciplinas_html",
    "salvar_disciplinas",
    "CursoColetado",
    "coletar_cursos",
    "coletar_e_salvar_cursos",
    "extrair_cursos_html",
    "salvar_cursos",
]
