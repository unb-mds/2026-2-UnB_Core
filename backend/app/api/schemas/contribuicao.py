from typing import Any

from pydantic import BaseModel


class ContribuicaoCreate(BaseModel):
    disciplina_id: int
    tipo: str
    payload: dict[str, Any]


class ContribuicaoAlteracao(BaseModel):
    disciplina_id: int
    tipo: str
    payload: dict[str, Any]
    conteudo_id: int