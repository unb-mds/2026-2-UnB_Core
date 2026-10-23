
import os

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine, delete

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-with-at-least-32-bytes")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:password@localhost:5214/postgres",
)

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", os.environ["DATABASE_URL"])

try:
    test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    with test_engine.connect():
        pass
except (SQLAlchemyError, UnicodeDecodeError) as error:
    pytest.skip(
        f"PostgreSQL de testes indisponível em TEST_DATABASE_URL: {error}",
        allow_module_level=True,
    )

from backend.app.api.schema.usuario import Usuario
from backend.app.api.schema.disciplina import Disciplina
from backend.app.api.security import criar_access_token, obter_usuario_token


@pytest.fixture
def session():
    SQLModel.metadata.create_all(test_engine, tables=[Usuario.__table__])
    with Session(test_engine) as database_session:
        database_session.exec(delete(Usuario))
        database_session.commit()
        yield database_session


@pytest.fixture
def disciplina_session():
    SQLModel.metadata.create_all(test_engine, tables=[Disciplina.__table__])
    with Session(test_engine) as database_session:
        if test_engine.dialect.name == "postgresql":
            database_session.exec(
                text("TRUNCATE TABLE disciplina RESTART IDENTITY CASCADE")
            )
        else:
            database_session.exec(delete(Disciplina))
        database_session.commit()
        yield database_session


def test_security_token_contains_user_data():
    token = criar_access_token(7, "usuario")
    payload = obter_usuario_token(token)

    assert payload["sub"] == "7"
    assert payload["perfil"] == "usuario"


def test_security_rejects_invalid_token():
    with pytest.raises(Exception) as error:
        obter_usuario_token("token-invalido")

    assert error.value.status_code == 401
