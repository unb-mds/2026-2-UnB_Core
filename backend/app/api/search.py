from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select, or_

from backend.app.db import get_session
from backend.app.api.schema.ConteudoAcademico import ConteudoAcademico
from backend.app.api.schema.publicacao_institucional import PublicacaoInstitucional

routerBusca = APIRouter(prefix="/api/v1", tags=["busca"])


class ConteudoAcademicoResultado(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    disciplina_id: int
    tipo: str
    titulo: str | None = None
    corpo_ou_url: str
    origem: str
    estado: str
    autor_id: int | None = None
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None


class PublicacaoInstitucionalResultado(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    publicacao_id: int | None = None
    titulo: str
    resumo: str
    categoria: str
    unidade_responsavel: str
    url_oficial: str
    estado: str
    curso_id: int | None = None
    prazo_inicio: datetime | None = None
    prazo_fim: datetime | None = None
    publicado_em: datetime | None = None
    ultima_verificacao: datetime | None = None


class ResultadoBusca(BaseModel):
    conteudos_academicos: list[ConteudoAcademicoResultado]
    publicacoes_institucionais: list[PublicacaoInstitucionalResultado]


def escapar_termo(termo: str) -> str:
    escaped = (
        termo.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
    return f"%{escaped}%" # Agente recomenda adicionar isso para pesquisas com caracteres especiais e fazer buscas parciais


@routerBusca.get("/search", response_model=ResultadoBusca)
def buscar(
    termo: str | None = Query(default=None, description="Termo para busca"),
    session: Session = Depends(get_session),):
    termo_busca = (termo or "").strip()
    if not termo_busca:
        return ResultadoBusca(
            conteudos_academicos=[],
            publicacoes_institucionais=[],
        )

    padrao = escapar_termo(termo_busca)

    # busca em Conteúdo Acadêmico
    condicoes_conteudo = [
        ConteudoAcademico.corpo_ou_url.ilike(padrao, escape="\\"),
        ConteudoAcademico.origem.ilike(padrao, escape="\\"),
        ConteudoAcademico.tipo.ilike(padrao, escape="\\"),
    ]
    if hasattr(ConteudoAcademico, "titulo"):
        condicoes_conteudo.append(ConteudoAcademico.titulo.ilike(padrao, escape="\\"))

    query_conteudos = (
        select(ConteudoAcademico)
        .where(ConteudoAcademico.estado == "publicado")
        .where(or_(*condicoes_conteudo))
        .order_by(ConteudoAcademico.id)
    )
    conteudos = session.exec(query_conteudos).all()

    # busca em Publicações Institucionais (remover depois?)
    condicoes_publicacao = [
        PublicacaoInstitucional.titulo.ilike(padrao, escape="\\"),
        PublicacaoInstitucional.resumo.ilike(padrao, escape="\\"),
        PublicacaoInstitucional.unidade_responsavel.ilike(padrao, escape="\\"),
        PublicacaoInstitucional.categoria.ilike(padrao, escape="\\"),
    ]

    query_publicacoes = (
        select(PublicacaoInstitucional)
        .where(or_(*condicoes_publicacao))
        .order_by(PublicacaoInstitucional.publicacao_id)
    )
    publicacoes = session.exec(query_publicacoes).all()

    return ResultadoBusca(
        conteudos_academicos=[
            ConteudoAcademicoResultado(
                id=c.id,
                disciplina_id=c.disciplina_id,
                tipo=c.tipo,
                titulo=getattr(c, "titulo", None),
                corpo_ou_url=str(c.corpo_ou_url),
                origem=c.origem,
                estado=c.estado,
                autor_id=getattr(c, "autor_id", None),
                criado_em=getattr(c, "criado_em", None),
                atualizado_em=getattr(c, "atualizado_em", None),
            )
            for conteudo in conteudos
            for c in [conteudo]
        ],
        publicacoes_institucionais=[
            PublicacaoInstitucionalResultado(
                id=p.publicacao_id,
                publicacao_id=p.publicacao_id,
                titulo=p.titulo,
                resumo=p.resumo,
                categoria=p.categoria,
                unidade_responsavel=p.unidade_responsavel,
                url_oficial=str(p.url_oficial),
                estado=p.estado,
                curso_id=getattr(p, "curso_id", None),
                prazo_inicio=getattr(p, "prazo_inicio", None),
                prazo_fim=getattr(p, "prazo_fim", None),
                publicado_em=getattr(p, "publicado_em", None),
                ultima_verificacao=getattr(p, "ultima_verificacao", None),
            )
            for publicacao in publicacoes
            for p in [publicacao]
        ],
    )
