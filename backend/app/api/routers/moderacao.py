from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.app.api.dependencies import exigir_moderador
from backend.app.api.schemas.moderacao import (
    ContribuicaoModeracao,
    DecisaoRequest,
)
from backend.app.db import get_session
from backend.app.domain import Usuario
from backend.app.services.moderacao_service import (
    decidir_contribuicao,
    listar_para_moderacao,
)

router = APIRouter(prefix="/moderacao", tags=["moderação"])


@router.get(
    "/contribuicoes",
    response_model=list[ContribuicaoModeracao],
)
def listar_contribuicoes(
    session: Session = Depends(get_session),
    _: Usuario = Depends(exigir_moderador),
):
    return listar_para_moderacao(session)


@router.post(
    "/contribuicoes/{contribuicao_id}/decisao",
    response_model=ContribuicaoModeracao,
)
def decidir(
    contribuicao_id: int,
    dados: DecisaoRequest,
    session: Session = Depends(get_session),
    _: Usuario = Depends(exigir_moderador),
):
    return decidir_contribuicao(
        session,
        contribuicao_id,
        dados.decisao,
        dados.justificativa,
    )
