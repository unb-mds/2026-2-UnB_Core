from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.app.domain import EstadoContribuicao, TipoConteudo


class ContribuicaoCriacao(BaseModel):
    disciplina_id: int
    conteudo_id: int | None = None
    tipo: TipoConteudo
    titulo: str = Field(min_length=1, max_length=200)
    corpo_ou_url: str = Field(min_length=1)
    origem: str | None = Field(default=None, max_length=500)


class ContribuicaoPublica(BaseModel):
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
