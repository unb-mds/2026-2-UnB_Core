from datetime import datetime, timezone

from sqlmodel import Session, select

from backend.app.api.errors import ErroValidacao, NaoEncontrado
from backend.app.api.schemas.moderacao import DecisaoModeracao, FiltroModeracao
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


def listar_para_moderacao(
    session: Session,
    filtro: FiltroModeracao = FiltroModeracao.REVISAR,
) -> list[Contribuicao]:
    """Contribuições para a moderação.

    - revisar (padrão): pendentes e com ajustes solicitados, das mais antigas para as mais novas;
    - exclusao: com pedido de exclusão do autor, na ordem dos pedidos;
    - todas: todas, das atualizadas mais recentemente para as mais antigas.
    """
    consulta = select(Contribuicao)
    if filtro == FiltroModeracao.EXCLUSAO:
        consulta = consulta.where(Contribuicao.exclusao_solicitada_em.is_not(None)).order_by(
            Contribuicao.exclusao_solicitada_em
        )
    elif filtro == FiltroModeracao.TODAS:
        consulta = consulta.order_by(Contribuicao.atualizado_em.desc(), Contribuicao.id.desc())
    else:
        consulta = consulta.where(
            Contribuicao.estado.in_(
                [EstadoContribuicao.PENDENTE, EstadoContribuicao.AJUSTES]
            )
        ).order_by(Contribuicao.criado_em)
    return list(session.exec(consulta).all())


def obter_para_moderacao(session: Session, contribuicao_id: int) -> Contribuicao:
    contribuicao = session.get(Contribuicao, contribuicao_id)
    if contribuicao is None:
        raise NaoEncontrado("A contribuição não foi encontrada.")
    return contribuicao


def excluir_contribuicao(session: Session, contribuicao_id: int) -> None:
    """Exclui de vez a contribuição e, se houver, o conteúdo publicado a partir dela."""
    contribuicao = obter_para_moderacao(session, contribuicao_id)
    conteudo_id = contribuicao.conteudo_id
    session.delete(contribuicao)
    if conteudo_id is not None:
        # Outras contribuições que propunham mudanças nesse conteúdo perdem o vínculo.
        outras = session.exec(
            select(Contribuicao).where(Contribuicao.conteudo_id == conteudo_id)
        ).all()
        for outra in outras:
            if outra.id != contribuicao_id:
                outra.conteudo_id = None
                session.add(outra)
        conteudo = session.get(ConteudoAcademico, conteudo_id)
        if conteudo is not None:
            session.flush()
            session.delete(conteudo)
    session.commit()


def recusar_exclusao(
    session: Session,
    contribuicao_id: int,
    justificativa: str,
) -> Contribuicao:
    """Mantém a contribuição publicada e responde ao autor com a justificativa."""
    contribuicao = obter_para_moderacao(session, contribuicao_id)
    if contribuicao.exclusao_solicitada_em is None:
        raise ErroValidacao("Esta contribuição não tem pedido de exclusão.")
    contribuicao.exclusao_solicitada_em = None
    contribuicao.motivo_exclusao = None
    contribuicao.justificativa_moderacao = (
        f"Pedido de exclusão recusado: {justificativa.strip()}"
    )
    contribuicao.atualizado_em = datetime.now(timezone.utc)
    session.add(contribuicao)
    session.commit()
    session.refresh(contribuicao)
    return contribuicao


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
    if contribuicao.conteudo_id is None:
        # Liga a contribuição ao conteúdo criado. Sem isso, aprovar de novo
        # depois de uma edição criava um segundo conteúdo e o antigo
        # continuava publicado.
        session.flush()
        contribuicao.conteudo_id = conteudo.id
    return conteudo
