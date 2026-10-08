from datetime import datetime
from pydantic import field_validator
from sqlmodel import Field, SQLModel, select, col, Session
from fastapi import APIRouter, HTTPException, Depends

# schemas
from SubmissaoBase import Submissao, SubmissaoBase
from usuario import get_current_user, Usuario
#session
from backend.app.db import get_session


class ContribuicaoBase(SubmissaoBase):
    conteudo_id: int
    autor_id: int
    payload: str  # dados submetidos para análise


class Contribuicao(ContribuicaoBase, Submissao, table=True):
    justificativa_moderacao: str | None = None
    


class ContribuicaoCreate(ContribuicaoBase):
    pass


class ContribuicaoRead(ContribuicaoBase):
    pass

class ContribuicaoModeracao(ContribuicaoBase):
    id : int
    justificativa_moderacao: str | None = None






routerContribuicao = APIRouter(prefix="/api/v1/contribuicoes", tags=["contribuições"])


@routerContribuicao.post("", response_model=ContribuicaoRead)
async def criar_contribuicao(
        contribuicao: ContribuicaoCreate,
        session: Session = Depends(get_session),
        current_user: Usuario = Depends(get_current_user)
):
    if not contribuicao:
        raise HTTPException(
            status_code=422,
            detail="Erro de entrada ou parâmetros ausentes/inválidos"
        )

    db_contribuicao = Contribuicao.model_validate(contribuicao)
    db_contribuicao.autor_id = current_user.id

    session.add(db_contribuicao)
    session.commit()
    session.refresh(db_contribuicao)

    return db_contribuicao


@routerContribuicao.get("/minhas", response_model=list[ContribuicaoRead])
async def listar_minhas_contribuicoes(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    statement = select(Contribuicao).where(
        col(Contribuicao.autor_id) == current_user.id
    )

    contribuicoes = session.exec(statement).all()
    return distribuicoes_ou_lista(contribuicoes)


def distribuicoes_ou_lista(contribuicoes):
    return contribuicoes or []