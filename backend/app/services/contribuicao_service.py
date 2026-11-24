from datetime import datetime, timezone

from sqlmodel import Session, select

from backend.app.api.errors import ErroValidacao, NaoEncontrado
from backend.app.domain import ConteudoAcademico, Contribuicao, Disciplina, Usuario


def criar_contribuicao(
    session: Session,
    usuario: Usuario,
    dados: dict,
) -> Contribuicao:
    disciplina = session.get(Disciplina, dados["disciplina_id"])
    if disciplina is None or not disciplina.ativo:
        raise NaoEncontrado("A disciplina selecionada não foi encontrada.")

    if dados.get("conteudo_id") is not None and not session.get(
        ConteudoAcademico, dados["conteudo_id"]
    ):
        raise ErroValidacao("O conteúdo relacionado não foi encontrado.")

    contribuicao = Contribuicao(
        **dados,
        autor_id=usuario.id,
    )
    session.add(contribuicao)
    session.commit()
    session.refresh(contribuicao)
    return contribuicao


def listar_contribuicoes_do_usuario(
    session: Session,
    usuario: Usuario,
) -> list[Contribuicao]:
    return list(
        session.exec(
            select(Contribuicao)
            .where(Contribuicao.autor_id == usuario.id)
            .order_by(Contribuicao.atualizado_em.desc())
        ).all()
    )


def obter_contribuicao_do_usuario(
    session: Session,
    usuario: Usuario,
    id_contribuicao: int,
) -> Contribuicao:
    contribuicao = (
        session.exec(
            select(Contribuicao)
            .where(Contribuicao.id == id_contribuicao)
        ).first()
    )

    if contribuicao is None:
        raise NaoEncontrado("Não foi encontrada contribuição com esse id")

    if contribuicao.autor_id != usuario.id:
        raise ErroValidacao("Usuario não tem permissão de editar essa contribuição")

    return contribuicao


def excluir_contribuicao_do_usuario(
    session: Session,
    usuario: Usuario,
    id_contribuicao: int,
) -> None:
    """O autor exclui na hora uma contribuição que ainda não foi publicada."""
    contribuicao = obter_contribuicao_do_usuario(session, usuario, id_contribuicao)
    if contribuicao.conteudo_id is not None:
        raise ErroValidacao(
            "Esta contribuição já está publicada. Peça a exclusão à moderação."
        )
    session.delete(contribuicao)
    session.commit()


def solicitar_exclusao(
    session: Session,
    usuario: Usuario,
    id_contribuicao: int,
    motivo: str,
) -> Contribuicao:
    """O autor pede à moderação a exclusão de uma contribuição já publicada."""
    contribuicao = obter_contribuicao_do_usuario(session, usuario, id_contribuicao)
    if contribuicao.conteudo_id is None:
        raise ErroValidacao(
            "Esta contribuição ainda não foi publicada: você pode excluí-la diretamente."
        )
    contribuicao.exclusao_solicitada_em = datetime.now(timezone.utc)
    contribuicao.motivo_exclusao = motivo.strip()
    session.add(contribuicao)
    session.commit()
    session.refresh(contribuicao)
    return contribuicao


def cancelar_pedido_exclusao(
    session: Session,
    usuario: Usuario,
    id_contribuicao: int,
) -> Contribuicao:
    contribuicao = obter_contribuicao_do_usuario(session, usuario, id_contribuicao)
    contribuicao.exclusao_solicitada_em = None
    contribuicao.motivo_exclusao = None
    session.add(contribuicao)
    session.commit()
    session.refresh(contribuicao)
    return contribuicao