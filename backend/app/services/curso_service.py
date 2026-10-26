from sqlmodel import Session, select

from backend.app.domain import Curso, Disciplina


def listar_cursos_ativos(session: Session) -> list[Curso]:
    return list(
        session.exec(
            select(Curso).where(Curso.ativo).order_by(Curso.nome)
        ).all()
    )


def listar_disciplinas_ativas(
    session: Session,
    curso_id: int,
) -> list[Disciplina]:
    return list(
        session.exec(
            select(Disciplina)
            .where(Disciplina.curso_id == curso_id, Disciplina.ativo)
            .order_by(Disciplina.nome)
        ).all()
    )
