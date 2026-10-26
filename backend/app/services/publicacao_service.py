from datetime import datetime
from typing import Literal

from fastapi import HTTPException, status,Depends
from sqlmodel import Session, select
from backend.app.db import get_session


from ..api.schema.publicacao_institucional import (
    PublicacaoInstitucional,
    PublicacaoInstitucionalGet,
)

PrazoFiltro = Literal[  "ativa",
                        "inativa",
                        "Sem informação"]
PRAZOS_PERMITIDOS = { "ativa",
                      "inativa",
                      "Sem informação"}


 


def listar_publicacoes(
    session: Session = Depends(get_session),
    *,
    termo: str | None = None,
    categoria: str | None = None,
    unidade: str | None = None,
    curso_id: int | None = None,
    estado: str | None = None,
    prazo_fim: PrazoFiltro | None = None,
    agora: datetime | None = None,
) -> list[PublicacaoInstitucional]:

    if prazo_fim is not None and prazo_fim not in PRAZOS_PERMITIDOS:
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

    if prazo_fim is not None:
        referencia = agora or datetime.now()

        if prazo_fim == "Sem informação":
            pesquisa = pesquisa.where(PublicacaoInstitucional.prazo_fim.is_(None))
        elif prazo_fim == "ativa":
            pesquisa = pesquisa.where(
                (PublicacaoInstitucional.estado == "ativa")
                & (
                    PublicacaoInstitucional.prazo_fim.is_(None)
                    | (PublicacaoInstitucional.prazo_fim >= referencia)
                )
            )
        else:
            pesquisa = pesquisa.where(
                (PublicacaoInstitucional.estado == "inativa")
                | (
                    PublicacaoInstitucional.prazo_fim.is_not(None)
                    & (PublicacaoInstitucional.prazo_fim < referencia)
                )
            )

    pesquisa = pesquisa.order_by(PublicacaoInstitucional.publicacao_id)
    return list(session.exec(pesquisa).all())


def _contains(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def detalhar_publicacao(
    publicacao_id : int,
    session: Session = Depends(get_session)
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