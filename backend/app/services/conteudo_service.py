from sqlmodel import Session, select

from backend.app.api.errors import NaoEncontrado
from backend.app.domain import (
    ConteudoAcademico,
    Disciplina,
    EstadoConteudo,
    TipoConteudo,
)


def listar_conteudos_publicados(
    session: Session,
    disciplina_id: int,
    tipo: TipoConteudo | None = None,
) -> list[ConteudoAcademico]:
    filtros = [
        ConteudoAcademico.disciplina_id == disciplina_id,
        ConteudoAcademico.estado == EstadoConteudo.PUBLICADO,
    ]
    if tipo is not None:
        filtros.append(ConteudoAcademico.tipo == tipo)

    return list(
        session.exec(
            select(ConteudoAcademico)
            .where(*filtros)
            .order_by(ConteudoAcademico.atualizado_em.desc())
        ).all()
    )


def obter_conteudo_publicado(
    session: Session,
    conteudo_id: int,
) -> ConteudoAcademico:
    conteudo = session.get(ConteudoAcademico, conteudo_id)
    if conteudo is None or conteudo.estado != EstadoConteudo.PUBLICADO:
        raise NaoEncontrado("O conteúdo publicado não foi encontrado.")
    return conteudo


def validar_disciplina_do_curso(
    session: Session,
    disciplina_id: int,
    curso_id: int,
) -> Disciplina:
    disciplina = session.get(Disciplina, disciplina_id)
    if disciplina is None or not disciplina.ativo or disciplina.curso_id != curso_id:
        raise NaoEncontrado(
            "A disciplina não pertence ao curso selecionado ou está indisponível."
        )
    return disciplina
