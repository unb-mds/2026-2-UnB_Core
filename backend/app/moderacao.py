from backend.app.api.schema.Contribuicao import Contribuicao, ContribuicaoModeracao, ContribuicaoRead
from backend.app.api.schema.usuario import Usuario,get_current_user, verificar_admin_moderador

from pydantic import model_validator,field_validator
from sqlmodel import Session, create_engine,select,select,SQLModel
from fastapi import FastAPI,HTTPException,APIRouter,Depends

engine = create_engine()
routerModeracao = APIRouter(prefix="/api/v1/moderacao", tags=["contribuições"])

class Decisao(SQLModel):
    justificativa_moderacao : str
    estado: str 
    
    @field_validator("estado")
    def validate_estado(cls, v):
            permitido = ["publicado", "ajustes", "rejeitado", "arquivado"]
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


def get_contribuicao(id_contribuicao : int, session : get_session):

    get_contribuicao = session.get(Contribuicao,id_contribuicao)
    if get_contribuicao:
        usuario = Contribuicao.model_validate(get_contribuicao)
        return Contribuicao
        
        
        
    raise HTTPException(status_code=401,
                        detail=f"Contribuição {id_contribuicao} não existe")


def get_session():
    with Session(engine) as session:
        yield session

@routerModeracao.post("/{id}/decisao",response_model=[Contribuicao])
def get_decisao(decisao : Decisao, session : get_session,
                contribuicao : Contribuicao = Depends(get_contribuicao), admin : Usuario = Depends(verificar_admin_moderador)):

    
    
    contribuicao.justificativa_moderacao = Decisao.justificativa_moderacao
    contribuicao.estado = Decisao.estado

    session.add(contribuicao)
    session.commit()
    session.refresh(contribuicao)

    return Contribuicao
    







        
    