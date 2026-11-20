from enum import StrEnum

from sqlmodel import Session, func, select

from backend.app.api.errors import NaoEncontrado
from backend.app.domain import (
    ConteudoAcademico,
    CursoDisciplina,
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


class OrdemConteudos(StrEnum):
    RECENTES = "recentes"
    ANTIGOS = "antigos"
    TITULO = "titulo"


ORDENACOES = {
    OrdemConteudos.RECENTES: (
        ConteudoAcademico.atualizado_em.desc(),
        ConteudoAcademico.id.desc(),
    ),
    OrdemConteudos.ANTIGOS: (
        ConteudoAcademico.atualizado_em.asc(),
        ConteudoAcademico.id.asc(),
    ),
    OrdemConteudos.TITULO: (
        func.lower(ConteudoAcademico.titulo).asc(),
        ConteudoAcademico.id.asc(),
    ),
}


def filtrar_conteudos(
    session: Session,
    *,
    tipo: TipoConteudo | None = None,
    curso_id: int | None = None,
    disciplina_id: int | None = None,
    ordem: OrdemConteudos = OrdemConteudos.RECENTES,
    limite: int = 6,
    deslocamento: int = 0,
) -> tuple[list[ConteudoAcademico], int]:
    """Conteúdos publicados de todas as disciplinas, com filtros opcionais.

    Retorna a página pedida e o total de conteúdos que atendem aos filtros.
    """
    filtros = [ConteudoAcademico.estado == EstadoConteudo.PUBLICADO]
    if tipo is not None:
        filtros.append(ConteudoAcademico.tipo == tipo)
    if disciplina_id is not None:
        filtros.append(ConteudoAcademico.disciplina_id == disciplina_id)
    if curso_id is not None:
        # Conteúdos das disciplinas que o curso oferece (vínculo em curso_disciplina).
        filtros.append(
            ConteudoAcademico.disciplina_id.in_(
                select(CursoDisciplina.disciplina_id).where(
                    CursoDisciplina.curso_id == curso_id
                )
            )
        )

    total = session.exec(
        select(func.count()).select_from(ConteudoAcademico).where(*filtros)
    ).one()
    itens = session.exec(
        select(ConteudoAcademico)
        .where(*filtros)
        .order_by(*ORDENACOES[ordem])
        .offset(deslocamento)
        .limit(limite)
    ).all()
    return list(itens), total


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
    pertence_ao_curso = session.exec(
        select(CursoDisciplina).where(
            CursoDisciplina.disciplina_id == disciplina_id,
            CursoDisciplina.curso_id == curso_id,
        )
    ).first()
    if disciplina is None or not disciplina.ativo or pertence_ao_curso is None:
        raise NaoEncontrado(
            "A disciplina não pertence ao curso selecionado ou está indisponível."
        )
    return disciplina
