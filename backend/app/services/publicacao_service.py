from datetime import datetime
from typing import Literal

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..api.schema.publicacao_institucional import (
    PublicacaoInstitucional,
    PublicacaoInstitucionalGet,
)

PrazoFiltro = Literal["aberto", "encerrado", "sem_prazo"]
PRAZOS_PERMITIDOS = {"aberto", "encerrado", "sem_prazo"}


def _contains(value: str) -> str: #não tenho certeza do porquê, mas o agente recomenda adicionar isso
    escaped_value = value.replace("\\", "\\\\").replace("%", "\\%").replace(
        "_", "\\_"
    )
    return f"%{escaped_value}%"


def listar_publicacoes(
    session: Session,
    *,
    termo: str | None = None,
    categoria: str | None = None,
    unidade: str | None = None,
    curso_id: int | None = None,
    estado: str | None = None,
    prazo: PrazoFiltro | None = None,
    agora: datetime | None = None,
) -> list[PublicacaoInstitucional]:

    if prazo is not None and prazo not in PRAZOS_PERMITIDOS:
        permitidos = ", ".join(sorted(PRAZOS_PERMITIDOS))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "codigo": "VALIDACAO",
                "mensagem": f"Prazo deve ser um dos seguintes valores: {permitidos}.",
            },
        )

    pesquisa = select(PublicacaoInstitucional)

    if termo and termo.strip():
        termo_pattern = _contains(termo.strip())
        pesquisa = pesquisa.where(
            PublicacaoInstitucional.titulo.ilike(termo_pattern, escape="\\")
            | PublicacaoInstitucional.resumo.ilike(termo_pattern, escape="\\")
        )

    if categoria and categoria.strip():
        pesquisa = pesquisa.where(
            PublicacaoInstitucional.categoria.ilike(categoria.strip())
        )

    if unidade and unidade.strip():
        pesquisa = pesquisa.where(
            PublicacaoInstitucional.unidade_responsavel.ilike(
                _contains(unidade.strip()), escape="\\"
            )
        )

    if curso_id is not None:
        pesquisa = pesquisa.where(PublicacaoInstitucional.curso_id == curso_id)

    if estado and estado.strip():
        pesquisa = pesquisa.where(PublicacaoInstitucional.estado.ilike(estado.strip()))

    if prazo is not None:
        referencia = agora or datetime.now()
        sem_datas = (
            PublicacaoInstitucional.prazo_inicio.is_(None)
            & PublicacaoInstitucional.prazo_fim.is_(None)
        )

        if prazo == "sem_prazo":
            pesquisa = pesquisa.where(
                (PublicacaoInstitucional.estado == "sem_prazo") | sem_datas
            )
        elif prazo == "aberto":
            pesquisa = pesquisa.where(
                ~sem_datas
                & (PublicacaoInstitucional.estado != "sem_prazo")
                & (
                    PublicacaoInstitucional.prazo_inicio.is_(None)
                    | (PublicacaoInstitucional.prazo_inicio <= referencia)
                )
                & (
                    PublicacaoInstitucional.prazo_fim.is_(None)
                    | (PublicacaoInstitucional.prazo_fim >= referencia)
                )
            )
        else:
            pesquisa = pesquisa.where(
                (PublicacaoInstitucional.estado == "encerrada")
                | (
                    (PublicacaoInstitucional.estado != "sem_prazo")
                    & (PublicacaoInstitucional.prazo_fim < referencia)
                )
            )

    pesquisa = pesquisa.order_by(PublicacaoInstitucional.publicacao_id)
    return list(session.exec(pesquisa).all())


def detalhar_publicacao(
    session: Session, publicacao_id: int
) -> PublicacaoInstitucionalGet:
    publicacao = session.get(PublicacaoInstitucional, publicacao_id)
    if publicacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "codigo": "NAO_ENCONTRADO",
                "mensagem": "Publicacao nao encontrada.",
            },
        )

    return PublicacaoInstitucionalGet.model_validate(publicacao)