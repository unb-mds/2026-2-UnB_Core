from datetime import datetime

from pydantic import EmailStr, field_validator, ValidationError
from sqlalchemy import true
from sqlmodel import SQLModel, Field


class UsuarioBase(SQLModel):

    email : EmailStr = Field(unique=True, index=True)
    nome : str
    perfil : str
    status : str #troquei o literal pois SQLModel não aceita literal
    #senha_hash colocar depois
    ativo : bool # defini se o usuario é frequente ao site

    @field_validator("status")
    def validate_status(cls,v):
        permitido = ["Online","Offline","Aparecer Offline","Ausente"]
        if v not in permitido:
            raise ValueError(f"deve ser um dos status a sequir {permitido}")
        return v

    @field_validator("perfil")
    def validate_perfil(cls,v):
        permitido = ["usuario","moderador","administrador"]
        if v not in permitido:
            raise ValueError(f"Perfil de usuario não valido {v}")
        return v

class Usuario(UsuarioBase,table = True):
    id: int | None = Field(default=None,
                           primary_key=True)
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)


class UsuarioCreate(UsuarioBase):
    pass