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
