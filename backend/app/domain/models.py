from datetime import datetime, timezone
from enum import StrEnum

from sqlmodel import Field, SQLModel


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


class PerfilUsuario(StrEnum):
    USUARIO = "usuario"
    MODERADOR = "moderador"
    ADMINISTRADOR = "administrador"


class TipoConteudo(StrEnum):
    RESUMO = "resumo"
    DICA = "dica"
    DIFICULDADE = "dificuldade"
    PROVA = "prova"
    IMPLEMENTACAO = "implementacao"
    LINK = "link"


class EstadoConteudo(StrEnum):
    PUBLICADO = "publicado"
    ARQUIVADO = "arquivado"


class EstadoContribuicao(StrEnum):
    PENDENTE = "pendente"
    AJUSTES = "ajustes"
    REJEITADA = "rejeitada"
    APROVADA = "aprovada"
    ARQUIVADA = "arquivada"


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(unique=True, index=True)
    senha_hash: str
    perfil: PerfilUsuario = Field(default=PerfilUsuario.USUARIO)
    ativo: bool = Field(default=True)
    criado_em: datetime = Field(default_factory=agora_utc)
    atualizado_em: datetime = Field(default_factory=agora_utc)


class Curso(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    sigla: str
    ativo: bool = Field(default=True)


class Disciplina(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    curso_id: int = Field(foreign_key="curso.id", index=True)
    codigo: str
    nome: str
    periodo: str | None = None
    ativo: bool = Field(default=True)


class ConteudoAcademico(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    disciplina_id: int = Field(foreign_key="disciplina.id", index=True)
    tipo: TipoConteudo
    titulo: str
    corpo_ou_url: str
    autor_id: int = Field(foreign_key="usuario.id")
    origem: str | None = None
    estado: EstadoConteudo = Field(default=EstadoConteudo.PUBLICADO)
    criado_em: datetime = Field(default_factory=agora_utc)
    atualizado_em: datetime = Field(default_factory=agora_utc)


class Contribuicao(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    autor_id: int = Field(foreign_key="usuario.id", index=True)
    conteudo_id: int | None = Field(default=None, foreign_key="conteudoacademico.id")
    disciplina_id: int = Field(foreign_key="disciplina.id")
    tipo: TipoConteudo
    titulo: str
    corpo_ou_url: str
    origem: str | None = None
    estado: EstadoContribuicao = Field(default=EstadoContribuicao.PENDENTE)
    justificativa_moderacao: str | None = None
    criado_em: datetime = Field(default_factory=agora_utc)
    atualizado_em: datetime = Field(default_factory=agora_utc)
