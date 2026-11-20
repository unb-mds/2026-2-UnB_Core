from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from backend.app.api.errors import NaoEncontrado
from backend.app.api.schemas.academico import (
    ConteudoPublico,
    CursoPublico,
    DisciplinaPublica,
    ListaResposta,
)
from backend.app.db import get_session
from backend.app.domain import Curso, CursoDisciplina, Disciplina, TipoConteudo
from backend.app.services.conteudo_service import (
    listar_conteudos_publicados,
    obter_conteudo_publicado,
    validar_disciplina_do_curso,
)
from backend.app.services.curso_service import (
    buscar_disciplinas,
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
    return {
        "itens": [
            _disciplina_com_cursos(session, disciplina)
            for disciplina in disciplinas
        ]
    }


@router.get("/disciplinas", response_model=ListaResposta[DisciplinaPublica])
def buscar(
    busca: str = Query(min_length=2, max_length=100),
    limite: int = Query(default=20, ge=1, le=50),
    session: Session = Depends(get_session),
):
    """Busca disciplinas pelo código ou nome, sem precisar escolher o curso."""
    disciplinas = buscar_disciplinas(session, busca, limite)
    return {
        "itens": [
            _disciplina_com_cursos(session, disciplina)
            for disciplina in disciplinas
        ]
    }


def _disciplina_com_cursos(session: Session, disciplina: Disciplina) -> dict:
    curso_ids = session.exec(
        select(CursoDisciplina.curso_id).where(
            CursoDisciplina.disciplina_id == disciplina.id
        )
    ).all()
    return {
        "id": disciplina.id,
        "curso_id": list(curso_ids),
        "codigo": disciplina.codigo,
        "nome": disciplina.nome,
        "periodo": disciplina.periodo,
    }


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
