import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import select

from backend.tests.test_config import disciplina_session, test_engine
from backend.app.api.schema.disciplina import (
    Disciplina,
    crud_disciplina_router,
)


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(crud_disciplina_router, prefix="/link_temporario")

    def override_get_session():
        from sqlmodel import Session

        with Session(test_engine) as database_session:
            yield database_session

    from backend.app.api.schema.disciplina import get_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client


def disciplina_payload(
    codigo="CIC-0123",
    nome="Introdução à Computação",
    periodo="2024-01-01T00:00:00",
    ativo=True,
):
    return {
        "codigo": codigo,
        "nome": nome,
        "periodo": periodo,
        "ativo": ativo,
    }


def create_disciplina(session, **kwargs):
    disciplina = Disciplina(
        curso_id=[],
        **disciplina_payload(**kwargs),
    )
    session.add(disciplina)
    session.commit()
    session.refresh(disciplina)
    return disciplina


def test_criar_disciplina_retorna_disciplina(client, disciplina_session):
    response = client.post(
        "/link_temporario/criar",
        json=disciplina_payload(codigo="cic0123"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["codigo"] == "CIC-0123"
    assert body["nome"] == "Introdução à Computação"
    assert body["id"] is not None

    created = disciplina_session.get(Disciplina, body["id"])
    assert created is not None
    assert created.codigo == "CIC-0123"


def test_criar_disciplina_rejeita_codigo_invalido(client, disciplina_session):
    response = client.post(
        "/link_temporario/criar",
        json=disciplina_payload(codigo="ADM-0123"),
    )

    assert response.status_code == 422
    assert disciplina_session.exec(select(Disciplina)).first() is None


def test_buscar_disciplina_existente(client, disciplina_session):
    disciplina = create_disciplina(disciplina_session, codigo="MAT-0123")

    response = client.get(f"/link_temporario/{disciplina.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": disciplina.id,
        "codigo": "MAT-0123",
        "nome": "Introdução à Computação",
        "periodo": "2024-01-01T00:00:00",
        "ativo": True,
    }


def test_buscar_disciplina_inexistente_retorna_404(client, disciplina_session):
    response = client.get("/link_temporario/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "publicação com Id 9999 não existe"
