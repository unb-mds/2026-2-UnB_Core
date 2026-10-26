from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from backend.app.api.errors import NaoEncontrado
from backend.app.api.schemas.academico import (
    ConteudoPublico,
    CursoPublico,
    DisciplinaPublica,
    ListaResposta,
)
from backend.app.db import get_session
from backend.app.domain import Curso, Disciplina, TipoConteudo
from backend.app.services.conteudo_service import (
    listar_conteudos_publicados,
    obter_conteudo_publicado,
    validar_disciplina_do_curso,
)
from backend.app.services.curso_service import (
    listar_cursos_ativos,
    listar_disciplinas_ativas,
)

router = APIRouter(tags=["consulta acadêmica"])


@router.get("/cursos", response_model=ListaResposta[CursoPublico])
def listar_cursos(session: Session = Depends(get_session)):
    return {"itens": listar_cursos_ativos(session)}


@router.get(
    "/cursos/{curso_id}/disciplinas",
    response_model=ListaResposta[DisciplinaPublica],
)
def listar_disciplinas(
    curso_id: int,
    session: Session = Depends(get_session),
):
    if session.get(Curso, curso_id) is None:
        raise NaoEncontrado("O curso não foi encontrado.")
    disciplinas = listar_disciplinas_ativas(session, curso_id)
    return {"itens": disciplinas}


@router.get(
    "/disciplinas/{disciplina_id}/conteudos",
    response_model=ListaResposta[ConteudoPublico],
)
def listar_conteudos(
    disciplina_id: int,
    tipo: TipoConteudo | None = Query(default=None),
    session: Session = Depends(get_session),
):
    if session.get(Disciplina, disciplina_id) is None:
        raise NaoEncontrado("A disciplina não foi encontrada.")
    return {"itens": listar_conteudos_publicados(session, disciplina_id, tipo)}


@router.get("/conteudos/{conteudo_id}", response_model=ConteudoPublico)
def detalhar_conteudo(
    conteudo_id: int,
    session: Session = Depends(get_session),
):
    return obter_conteudo_publicado(session, conteudo_id)
