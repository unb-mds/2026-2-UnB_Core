from sqlmodel import Session, select

from backend.app.domain import Curso, CursoDisciplina, Disciplina


def listar_cursos(session: Session) -> list[Curso]:
    return list(
        session.exec(
            select(Curso).order_by(Curso.nome, Curso.grau)
        ).all()
    )


listar_cursos_ativos = listar_cursos


def listar_disciplinas_ativas(
    session: Session,
    curso_id: int,
) -> list[Disciplina]:
    return list(
        session.exec(
            select(Disciplina)
            .join(
                CursoDisciplina,
                CursoDisciplina.disciplina_id == Disciplina.id,
            )
            .where(
                CursoDisciplina.curso_id == curso_id,
                Disciplina.ativo,
            )
            .order_by(Disciplina.nome)
        ).all()
    )
