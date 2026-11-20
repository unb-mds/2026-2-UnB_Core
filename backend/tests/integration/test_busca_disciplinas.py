from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.app.db import get_session
from backend.app.domain import Curso, CursoDisciplina, Disciplina
from backend.app.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def session_override() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def no_lifespan(_app):
    yield


def setup_function() -> None:
    app.dependency_overrides[get_session] = session_override
    app.router.lifespan_context = no_lifespan
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        software = Curso(nome="ENGENHARIA DE SOFTWARE", sigla="FCTE")
        energia = Curso(nome="ENGENHARIA DE ENERGIA", sigla="FCTE")
        calculo = Disciplina(codigo="MAT0025", nome="CÁLCULO 1")
        calculo_2 = Disciplina(codigo="MAT0026", nome="CÁLCULO 2")
        compiladores = Disciplina(codigo="FGA0003", nome="COMPILADORES 1")
        inativa = Disciplina(codigo="FGA9999", nome="CÁLCULO ANTIGO", ativo=False)
        session.add_all([software, energia, calculo, calculo_2, compiladores, inativa])
        session.flush()
        session.add_all(
            [
                CursoDisciplina(curso_id=software.id, disciplina_id=calculo.id),
                CursoDisciplina(curso_id=energia.id, disciplina_id=calculo.id),
                CursoDisciplina(curso_id=software.id, disciplina_id=calculo_2.id),
                CursoDisciplina(curso_id=software.id, disciplina_id=compiladores.id),
            ]
        )
        session.commit()


def test_busca_disciplina_pelo_nome_sem_acento_e_sem_curso() -> None:
    with TestClient(app) as client:
        resposta = client.get("/api/v1/disciplinas", params={"busca": "calculo"})

    assert resposta.status_code == 200
    itens = resposta.json()["itens"]
    assert [item["codigo"] for item in itens] == ["MAT0025", "MAT0026"]
    # A mesma disciplina aparece uma vez, com todos os cursos que a oferecem.
    assert sorted(itens[0]["curso_id"]) == [1, 2]


def test_busca_disciplina_pelo_codigo_e_por_varios_termos() -> None:
    with TestClient(app) as client:
        por_codigo = client.get("/api/v1/disciplinas", params={"busca": "fga0003"})
        por_termos = client.get("/api/v1/disciplinas", params={"busca": "calc 2"})

    assert [item["nome"] for item in por_codigo.json()["itens"]] == ["COMPILADORES 1"]
    assert [item["codigo"] for item in por_termos.json()["itens"]] == ["MAT0026"]


def test_busca_disciplina_ignora_inativas_e_respeita_limite() -> None:
    with TestClient(app) as client:
        resposta = client.get(
            "/api/v1/disciplinas",
            params={"busca": "calculo", "limite": 1},
        )

    assert [item["codigo"] for item in resposta.json()["itens"]] == ["MAT0025"]


def test_busca_disciplina_valida_o_termo() -> None:
    with TestClient(app) as client:
        sem_termo = client.get("/api/v1/disciplinas")
        termo_curto = client.get("/api/v1/disciplinas", params={"busca": "c"})
        limite_alto = client.get(
            "/api/v1/disciplinas",
            params={"busca": "calculo", "limite": 500},
        )

    assert sem_termo.status_code == 422
    assert termo_curto.status_code == 422
    assert limite_alto.status_code == 422
