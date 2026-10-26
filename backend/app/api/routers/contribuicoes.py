from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from backend.app.api.dependencies import obter_usuario_atual
from backend.app.api.schemas.contribuicao import (
    ContribuicaoCriacao,
    ContribuicaoPublica,
)
from backend.app.db import get_session
from backend.app.domain import Usuario
from backend.app.services.contribuicao_service import (
    criar_contribuicao,
    listar_contribuicoes_do_usuario,
)

router = APIRouter(prefix="/contribuicoes", tags=["contribuições"])


@router.post(
    "",
    response_model=ContribuicaoPublica,
    status_code=status.HTTP_201_CREATED,
)
def criar(
    dados: ContribuicaoCriacao,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    return criar_contribuicao(session, usuario, dados.model_dump())


@router.get("/minhas", response_model=list[ContribuicaoPublica])
def minhas(
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    return listar_contribuicoes_do_usuario(session, usuario)
