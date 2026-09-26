from _pydatetime import datetime
from datetime import datetime
from pydantic import field_validator
from sqlmodel import Field, SQLModel

from SubmissaoBase import Submissao,SubmissaoBase

class ContribuicaoBase(SubmissaoBase):
    conteudo_id : int
    autor_id: int
    payload: str # dados submetidos para analase,colocar verificaçao depois

    #@field_validator("payload")
    #def validate_payload(cls, v):
       # permitido = ["pendente", "publicado", "ajustes", "rejeitado", "arquivado"]
       # if v not in permitido:
        #    raise ValueError(f"deve ser um dos status a sequir {permitido}")
       # return v


class Contribuicao(ContribuicaoBase,Submissao,table=True):
    justificativa_moderacao: str | None = None
    pass

class ContribuicaoCreate(ContribuicaoBase):
    pass