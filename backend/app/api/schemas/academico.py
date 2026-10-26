from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.app.domain import TipoConteudo


class CursoPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    sigla: str


class DisciplinaPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    curso_id: int
    codigo: str
    nome: str
    periodo: str | None


class ConteudoPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    disciplina_id: int
    tipo: TipoConteudo
    titulo: str
    corpo_ou_url: str
    autor_id: int
    origem: str | None
    atualizado_em: datetime


class ListaResposta[T](BaseModel):
    itens: list[T]
