from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from backend.app.domain import EstadoContribuicao, TipoConteudo


class DecisaoModeracao(StrEnum):
    APROVAR = "aprovar"
    AJUSTES = "ajustes"
    REJEITAR = "rejeitar"
    ARQUIVAR = "arquivar"


class DecisaoRequest(BaseModel):
    decisao: DecisaoModeracao
    justificativa: str | None = Field(default=None, max_length=2000)


class ContribuicaoModeracao(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    autor_id: int
    conteudo_id: int | None
    disciplina_id: int
    tipo: TipoConteudo
    titulo: str
    corpo_ou_url: str
    origem: str | None
    estado: EstadoContribuicao
    justificativa_moderacao: str | None
    criado_em: datetime
    atualizado_em: datetime
