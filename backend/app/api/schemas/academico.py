from datetime import datetime

from pydantic import AliasPath, BaseModel, ConfigDict, Field

from backend.app.domain import GrauCurso, TipoConteudo


class CursoPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    sigla: str
    grau: GrauCurso


class DisciplinaPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    curso_id: list[int]
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
    # Lidos dos relacionamentos do model; ficam vazios se não houver.
    disciplina_codigo: str | None = Field(
        default=None,
        validation_alias=AliasPath("disciplina", "codigo"),
    )
    disciplina_nome: str | None = Field(
        default=None,
        validation_alias=AliasPath("disciplina", "nome"),
    )
    autor_nome: str | None = Field(
        default=None,
        validation_alias=AliasPath("autor", "nome"),
    )


class ListaResposta[T](BaseModel):
    itens: list[T]


class ListaPaginada[T](BaseModel):
    itens: list[T]
    # Total de itens que atendem aos filtros, somando todas as páginas.
    total: int
