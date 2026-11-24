from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from backend.app.api.dependencies import exigir_moderador
from backend.app.api.schemas.moderacao import (
    ContribuicaoModeracao,
    DecisaoRequest,
    FiltroModeracao,
    RecusaExclusao,
)
from backend.app.db import get_session
from backend.app.domain import Usuario
from backend.app.services.moderacao_service import (
    decidir_contribuicao,
    excluir_contribuicao,
    listar_para_moderacao,
    obter_para_moderacao,
    recusar_exclusao,
)

router = APIRouter(prefix="/moderacao", tags=["moderação"])


@router.get(
    "/contribuicoes",
    response_model=list[ContribuicaoModeracao],
)
def listar_contribuicoes(
    session: Session = Depends(get_session),
    _: Usuario = Depends(exigir_moderador),
    filtro: FiltroModeracao = FiltroModeracao.REVISAR,
):
    """Lista para a moderação. filtro: revisar (padrão), exclusao ou todas."""
    return listar_para_moderacao(session, filtro)


@router.get(
    "/contribuicoes/{contribuicao_id}",
    response_model=ContribuicaoModeracao,
)
def detalhar_contribuicao(
    contribuicao_id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(exigir_moderador),
):
    return obter_para_moderacao(session, contribuicao_id)


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


@router.delete(
    "/contribuicoes/{contribuicao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def excluir(
    contribuicao_id: int,
    session: Session = Depends(get_session),
    _: Usuario = Depends(exigir_moderador),
):
    """Exclui de vez a contribuição e o conteúdo publicado a partir dela."""
    excluir_contribuicao(session, contribuicao_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/contribuicoes/{contribuicao_id}/recusar-exclusao",
    response_model=ContribuicaoModeracao,
)
def recusar_pedido_exclusao(
    contribuicao_id: int,
    dados: RecusaExclusao,
    session: Session = Depends(get_session),
    _: Usuario = Depends(exigir_moderador),
):
    """Mantém a contribuição publicada e responde ao autor com a justificativa."""
    return recusar_exclusao(session, contribuicao_id, dados.justificativa)
