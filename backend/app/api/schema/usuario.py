from datetime import datetime

from pydantic import EmailStr, field_validator, ValidationError
from sqlalchemy import true
from sqlmodel import SQLModel, Field
from fastapi import HTTPException,Depends
from sqlmodel import SQLModel, Field, Session, create_engine, select,select, col

engine = create_engine()
def get_session():
    with Session(engine) as session:
        yield session
class UsuarioBase(SQLModel):

    email : EmailStr = Field(unique=True, index=True)
    nome : str
    #perfil : str  movi para a classe Usuario
    status : str #troquei o literal pois SQLModel não aceita literal
    #senha_hash colocar depois
    ativo : bool # defini se o usuario é frequente ao site

    @field_validator("status")
    def validate_status(cls,v):
        permitido = ["Online","Offline","Aparecer Offline","Ausente"]
        if v not in permitido:
            raise ValueError(f"deve ser um dos status a sequir {permitido}")
        return v

    

class Usuario(UsuarioBase,table = True):
    id: int | None = Field(default=None,
                           primary_key=True)
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)
    perfil : str = Field(default= "usuario")

    @field_validator("perfil")
    def validate_perfil(cls,v):
            permitido = ["usuario","moderador","administrador"]
            if v not in permitido:
                raise ValueError(f"Perfil de usuario não valido {v}")
            return v

class UsuarioCreate(UsuarioBase):
    pass

class get_current_user(UsuarioBase):
    id : int
    perfil : str

def get_usuario(id_usuario : int, session : get_session):
    get_user = session.get(Usuario,id_usuario)
    if get_user:
        usuario = get_current_user.model_validate(get_user)
        return usuario
        
    raise HTTPException(status_code=401,
                        detail="Usuario sem cadastro")


def verificar_admin_moderador(usuario : get_current_user,session : get_session):
    if usuario.perfil == "administrador" or usuario.perfil == "moderador":
        return usuario
    
    raise HTTPException(status_code=403,
                        detail=f"{usuario.nome} não tem permição para acessar essa pagina")