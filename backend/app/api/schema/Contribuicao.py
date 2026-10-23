from datetime import datetime
from pydantic import field_validator
from sqlmodel import Field, SQLModel, select, col, Session
from fastapi import APIRouter, HTTPException, Depends

# schemas
from backend.app.api.schema.SubmissaoBase import Submissao, SubmissaoBase
from backend.app.api.schema.usuario import get_usuario, Usuario
#session
from backend.app.db import get_session


class ContribuicaoBase(SubmissaoBase):
    conteudo_id: int
    payload: str  # dados submetidos para análise


class Contribuicao(ContribuicaoBase, Submissao, table=True):
    conteudo_id: int 
    autor_id: int = Field(foreign_key="usuario.id")
    justificativa_moderacao: str | None = None
    


class ContribuicaoCreate(ContribuicaoBase):
    autor_id : int
    pass


class ContribuicaoRead(ContribuicaoBase):
    pass

class ContribuicaoModeracao(ContribuicaoBase):
    id : int
    justificativa_moderacao: str | None = None

class ContribuicaoUpdate(SQLModel):
    payload: str




routerContribuicao = APIRouter()


@routerContribuicao.post("", response_model=ContribuicaoRead)
def criar_contribuicao(
        contribuicao: ContribuicaoCreate,
        session: Session = Depends(get_session),
        current_user: Usuario = Depends(get_usuario)
):
    if not contribuicao:
        raise HTTPException(
            status_code=422,
            detail="Erro de entrada ou parâmetros ausentes/inválidos"
        )
    contribuicao.autor_id = current_user.id
    db_contribuicao = Contribuicao.model_validate(contribuicao)

    session.add(db_contribuicao)
    session.commit()
    session.refresh(db_contribuicao)

    return db_contribuicao


@routerContribuicao.get("/minhas", response_model=list[ContribuicaoRead])
def listar_minhas_contribuicoes(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_usuario)
):
    statement = select(Contribuicao).where(
        col(Contribuicao.autor_id) == current_user.id
    )

    contribuicoes = session.exec(statement).all()
    return distribuicoes_ou_lista(contribuicoes)


def distribuicoes_ou_lista(contribuicoes):
    return contribuicoes or []


@routerContribuicao.delete("/minhas/remover/{contribuicao_removida_id}")
def delete_contribuicao(contribuicao_removida_id : int, usuario : Usuario = Depends(get_usuario),
                        session : Session = Depends(get_session)):

    contribuicao = session.get(Contribuicao,contribuicao_removida_id)
    if not contribuicao or usuario.id!= contribuicao.autor_id:
        raise HTTPException(status_code=403,
                    detail="Erro de entrada ou usuario invalido")
    session.delete(contribuicao)
    session.commit()
    return contribuicao

@routerContribuicao.patch("/minhas/editar/{contribuicao_id}",response_model= Contribuicao)
def editar_contribuicao(contribuicao_id : int, contribuicaoUpdate : ContribuicaoUpdate, session : Session = Depends(get_session),
                        usuario : Usuario = Depends(get_usuario)):
    contribuicao = session.get(Contribuicao,contribuicao_id) # procura a Contribuicao no database
    if not contribuicao or contribuicao.autor_id != usuario.id:
        raise HTTPException(status_code=403,
                            detail="Erro de entrada ou usuario invalido")

    #Edição da contribuicão
    contribuicao.payload = contribuicaoUpdate.payload
    contribuicao.atualizado_em = datetime.now()
    contribuicao.estado = "pendente"

    #update no database
    session.add(contribuicao) 
    session.commit()
    session.refresh(contribuicao)
    return contribuicao