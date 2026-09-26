from email.policy import default
from datetime import datetime
from pydantic import field_validator
from sqlmodel import SQLModel, Field


class SubmissaoBase(SQLModel):
    disciplina_id : int #colocar validação depois
    tipo : str # COLOCAR VERIFICAÇÃO DEPOIS
    origem : str #Muda tipo tipos
    estado : str

    @field_validator("estado")
    def validate_estado(cls, v):
        permitido = ["pendente","publicado","ajustes","rejeitado","arquivado"]
        if v not in permitido:
            raise ValueError(f"deve ser um dos status a sequir {permitido}")
        return v

class Submissao():
    id : int |None = Field(default=None,primary_key=True)
    autor_id : int
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)