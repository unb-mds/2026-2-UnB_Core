from collections.abc import Generator
from sqlmodel import Session, SQLModel, create_engine
from backend.app.settings.config import settings


engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    from backend.app.domain import (
        ConteudoAcademico,
        Contribuicao,
        Curso,
        Disciplina,
        Usuario,
    )
    SQLModel.metadata.create_all(engine)
