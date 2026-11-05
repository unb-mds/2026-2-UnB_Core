from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from backend.app.api.dependencies import obter_usuario_atual
from backend.app.api.schemas.contribuicao import (
    ContribuicaoCriacao,
    ContribuicaoPublica,
    ContribuicaoUpdate,
)
from backend.app.db import get_session
from backend.app.domain import Usuario
from backend.app.domain.models import EstadoContribuicao
from backend.app.services.contribuicao_service import (
    criar_contribuicao,
    listar_contribuicoes_do_usuario,
    obter_contribuicao_do_usuario,
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


@router.patch(
    "/minhas/{id_contribuicao}",
    response_model=ContribuicaoPublica,
)
def atualizar_contribuicao(
    id_contribuicao: int,
    dados: ContribuicaoUpdate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    contribuicao = obter_contribuicao_do_usuario(
        session,
        usuario,
        id_contribuicao,
    )

    dados_dict = dados.model_dump(exclude_unset=True)
    for key, value in dados_dict.items():
        setattr(contribuicao, key, value)

    contribuicao.estado = EstadoContribuicao.PENDENTE
    contribuicao.atualizado_em = datetime.now(timezone.utc)
    session.add(contribuicao)
    session.commit()
    session.refresh(contribuicao)
    return contribuicao