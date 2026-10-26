from datetime import datetime, timezone

from sqlmodel import Session, select

from backend.app.api.errors import ErroValidacao, NaoEncontrado
from backend.app.api.schemas.moderacao import DecisaoModeracao
from backend.app.domain import (
    ConteudoAcademico,
    Contribuicao,
    EstadoContribuicao,
    EstadoConteudo,
)

TRANSICOES_VALIDAS = {
    EstadoContribuicao.PENDENTE: {
        DecisaoModeracao.APROVAR,
        DecisaoModeracao.AJUSTES,
        DecisaoModeracao.REJEITAR,
        DecisaoModeracao.ARQUIVAR,
    },
    EstadoContribuicao.AJUSTES: set(),
}


def listar_para_moderacao(session: Session) -> list[Contribuicao]:
    return list(
        session.exec(
            select(Contribuicao)
            .where(
                Contribuicao.estado.in_(
                    [EstadoContribuicao.PENDENTE, EstadoContribuicao.AJUSTES]
                )
            )
            .order_by(Contribuicao.criado_em)
        ).all()
    )


def decidir_contribuicao(
    session: Session,
    contribuicao_id: int,
    decisao: DecisaoModeracao,
    justificativa: str | None,
) -> Contribuicao:
    contribuicao = session.get(Contribuicao, contribuicao_id)
    if contribuicao is None:
        raise NaoEncontrado("A contribuição não foi encontrada.")

    if decisao == DecisaoModeracao.AJUSTES:
        novo_estado = EstadoContribuicao.AJUSTES
    elif decisao == DecisaoModeracao.APROVAR:
        novo_estado = EstadoContribuicao.APROVADA
    elif decisao == DecisaoModeracao.REJEITAR:
        novo_estado = EstadoContribuicao.REJEITADA
    else:
        novo_estado = EstadoContribuicao.ARQUIVADA

    if decisao not in TRANSICOES_VALIDAS.get(contribuicao.estado, set()):
        raise ErroValidacao(
            f"A decisão '{decisao.value}' não é válida para o estado atual."
        )

    if decisao == DecisaoModeracao.AJUSTES and not (justificativa or "").strip():
        raise ErroValidacao("Informe uma justificativa ao solicitar ajustes.")

    if decisao == DecisaoModeracao.APROVAR:
        publicar_conteudo(session, contribuicao)

    contribuicao.estado = novo_estado
    contribuicao.justificativa_moderacao = (
        justificativa.strip() if justificativa else None
    )
    contribuicao.atualizado_em = datetime.now(timezone.utc)
    session.add(contribuicao)
    session.commit()
    session.refresh(contribuicao)
    return contribuicao


def publicar_conteudo(
    session: Session,
    contribuicao: Contribuicao,
) -> ConteudoAcademico:
    if contribuicao.conteudo_id is None:
        conteudo = ConteudoAcademico(
            disciplina_id=contribuicao.disciplina_id,
            tipo=contribuicao.tipo,
            titulo=contribuicao.titulo,
            corpo_ou_url=contribuicao.corpo_ou_url,
            autor_id=contribuicao.autor_id,
            origem=contribuicao.origem,
        )
    else:
        conteudo = session.get(ConteudoAcademico, contribuicao.conteudo_id)
        if conteudo is None:
            raise NaoEncontrado("O conteúdo relacionado não foi encontrado.")
        conteudo.disciplina_id = contribuicao.disciplina_id
        conteudo.tipo = contribuicao.tipo
        conteudo.titulo = contribuicao.titulo
        conteudo.corpo_ou_url = contribuicao.corpo_ou_url
        conteudo.origem = contribuicao.origem
        conteudo.estado = EstadoConteudo.PUBLICADO
        conteudo.atualizado_em = datetime.now(timezone.utc)

    session.add(conteudo)
    return conteudo
