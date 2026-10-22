from datetime import datetime, timezone
from pydantic import field_validator
from sqlmodel import SQLModel, Field


class SubmissaoBase(SQLModel):
    disciplina_id : int  = Field(foreign_key="disciplina.id")
    tipo : str 
    origem : str

class Submissao():
    id : int |None = Field(default=None,primary_key=True)
    autor_id : int
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    estado: str = Field(default = "pendente")

    @field_validator("estado")
    def validate_estado(cls, v):
        permitido = ["pendente", "publicado", "ajustes", "rejeitado", "arquivado"]
        if v not in permitido:
            raise ValueError(f"deve ser um dos status a sequir {permitido}")
        return v