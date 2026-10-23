from backend.app.api.schema.Contribuicao import (
    Contribuicao,
    ContribuicaoModeracao,
    ContribuicaoRead,
)
from backend.app.api.schema.usuario import get_current_user
from backend.app.api.schema.usuario import Usuario, verificar_admin_moderador
from datetime import datetime

from pydantic import field_validator
from sqlmodel import SQLModel,Session
from fastapi import APIRouter, Depends, HTTPException
#session
from backend.app.db import get_session
routerModeracao = APIRouter(prefix="/api/v1/moderacao", tags=["contribuições"])

class Decisao(SQLModel):
    justificativa_moderacao : str
    estado: str 
    
    @field_validator("estado")
    def validate_estado(cls, v):
            permitido = ["aprovada", "ajustes", "rejeitado", "arquivado"]
            if v not in permitido:
                raise ValueError(f"deve ser um dos status a sequir {permitido}")
            return v


def get_usuario(id_usuario : int, session : get_session):
    get_user = session.get(Usuario,id_usuario)
    if get_user:
        usuario = get_current_user.model_validate(get_user)
        if usuario.perfil == "moderador" or usuario.perfil == "administrador":
            return usuario.id
        
        else:
            nome = usuario.nome
            raise HTTPException(status_code=403,
                                detail=f"Usuario {nome} não autorizado")
        
    raise HTTPException(status_code=401,
                        detail="Usuario sem cadastro")


def get_contribuicao(id: int, session: Session = Depends(get_session)):
    contribuicao = session.get(Contribuicao, id)
    
    if not contribuicao:
        raise HTTPException(status_code=404, detail="Contribuição não encontrada")
        
    return contribuicao
        
        
        
    




@routerModeracao.post("/{id}/decisao",response_model= Contribuicao)
def get_decisao(decisao : Decisao, session : Session = Depends(get_session),
                contribuicao : Contribuicao = Depends(get_contribuicao), admin : Usuario = Depends(verificar_admin_moderador)):

    #se a decisao for aprovada a contribuição é publicada
    if decisao.estado == "aprovada":
        contribuicao.estado = "publicado"
    else:
        contribuicao.estado = decisao.estado

    contribuicao.justificativa_moderacao = decisao.justificativa_moderacao
    contribuicao.atualizado_em = datetime.now()
    session.add(contribuicao)
    session.commit()
    session.refresh(contribuicao)

    return contribuicao
    







        
    