from collections.abc import Generator
from sqlmodel import Session, SQLModel, create_engine
from backend.app.settings.config import settings


engine = create_engine(
    settings.database_url,
    echo=True, # colocar echo = False depois de terminamos os tests
    pool_pre_ping=True,
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)