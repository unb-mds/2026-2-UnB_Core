from collections.abc import Generator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.app.db import get_session
from backend.app.domain import (
    ConteudoAcademico,
    Curso,
    CursoDisciplina,
    Disciplina,
    EstadoConteudo,
    TipoConteudo,
    Usuario,
)
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
    agora = datetime(2026, 11, 20, 12, tzinfo=timezone.utc)
    with Session(engine) as session:
        software = Curso(nome="ENGENHARIA DE SOFTWARE", sigla="FCTE")
        energia = Curso(nome="ENGENHARIA DE ENERGIA", sigla="FCTE")
        compiladores = Disciplina(codigo="FGA0003", nome="COMPILADORES 1")
        calculo = Disciplina(codigo="MAT0025", nome="CÁLCULO 1")
        fluidos = Disciplina(codigo="FGA0109", nome="MECÂNICA DOS FLUIDOS 1")
        autora = Usuario(nome="Ana", email="ana@example.com", senha_hash="hash")
        session.add_all([software, energia, compiladores, calculo, fluidos, autora])
        session.flush()
        session.add_all(
            [
                # Cálculo 1 é dos dois cursos; Compiladores só de Software; Fluidos só de Energia.
                CursoDisciplina(curso_id=software.id, disciplina_id=compiladores.id),
                CursoDisciplina(curso_id=software.id, disciplina_id=calculo.id),
                CursoDisciplina(curso_id=energia.id, disciplina_id=calculo.id),
                CursoDisciplina(curso_id=energia.id, disciplina_id=fluidos.id),
            ]
        )
        for horas, titulo, disciplina, tipo, estado in [
            (4, "Bernoulli na prática", fluidos, TipoConteudo.RESUMO, EstadoConteudo.PUBLICADO),
            (3, "Arquivado", compiladores, TipoConteudo.RESUMO, EstadoConteudo.ARQUIVADO),
            (2, "Derivadas", calculo, TipoConteudo.DICA, EstadoConteudo.PUBLICADO),
            (1, "Análise léxica", compiladores, TipoConteudo.RESUMO, EstadoConteudo.PUBLICADO),
            (0, "Prova 2025.1", calculo, TipoConteudo.PROVA, EstadoConteudo.PUBLICADO),
        ]:
            momento = agora - timedelta(hours=horas)
            session.add(
                ConteudoAcademico(
                    disciplina_id=disciplina.id,
                    tipo=tipo,
                    titulo=titulo,
                    corpo_ou_url="texto",
                    autor_id=autora.id,
                    estado=estado,
                    criado_em=momento,
                    atualizado_em=momento,
                )
            )
        session.commit()


def titulos(resposta) -> list[str]:
    return [item["titulo"] for item in resposta.json()["itens"]]


def test_sem_filtros_lista_todos_os_publicados_do_mais_recente_ao_mais_antigo() -> None:
    with TestClient(app) as client:
        resposta = client.get("/api/v1/conteudos", params={"limite": 50})

    assert resposta.status_code == 200
    assert titulos(resposta) == [
        "Prova 2025.1",
        "Análise léxica",
        "Derivadas",
        "Bernoulli na prática",
    ]
    assert resposta.json()["total"] == 4


def test_ordena_do_mais_antigo_e_por_titulo() -> None:
    with TestClient(app) as client:
        antigos = client.get("/api/v1/conteudos", params={"limite": 50, "ordem": "antigos"})
        por_titulo = client.get("/api/v1/conteudos", params={"limite": 50, "ordem": "titulo"})
        invalida = client.get("/api/v1/conteudos", params={"ordem": "aleatoria"})

    assert titulos(antigos) == [
        "Bernoulli na prática",
        "Derivadas",
        "Análise léxica",
        "Prova 2025.1",
    ]
    assert titulos(por_titulo) == [
        "Análise léxica",
        "Bernoulli na prática",
        "Derivadas",
        "Prova 2025.1",
    ]
    assert invalida.status_code == 422


def test_filtra_por_curso_disciplina_e_tipo() -> None:
    with TestClient(app) as client:
        energia = client.get("/api/v1/conteudos", params={"curso_id": 2, "limite": 50})
        calculo = client.get("/api/v1/conteudos", params={"disciplina_id": 2, "limite": 50})
        resumos_software = client.get(
            "/api/v1/conteudos",
            params={"curso_id": 1, "tipo": "resumo", "limite": 50},
        )
        curso_inexistente = client.get("/api/v1/conteudos", params={"curso_id": 999})

    # Energia tem Cálculo 1 (compartilhada com Software) e Fluidos.
    assert titulos(energia) == ["Prova 2025.1", "Derivadas", "Bernoulli na prática"]
    assert titulos(calculo) == ["Prova 2025.1", "Derivadas"]
    assert titulos(resumos_software) == ["Análise léxica"]
    assert resumos_software.json()["total"] == 1
    assert curso_inexistente.json() == {"itens": [], "total": 0}


def test_pagina_os_resultados_e_mantem_o_total() -> None:
    with TestClient(app) as client:
        primeira = client.get("/api/v1/conteudos", params={"limite": 3, "pagina": 1})
        segunda = client.get("/api/v1/conteudos", params={"limite": 3, "pagina": 2})
        pagina_zero = client.get("/api/v1/conteudos", params={"pagina": 0})

    assert titulos(primeira) == ["Prova 2025.1", "Análise léxica", "Derivadas"]
    assert titulos(segunda) == ["Bernoulli na prática"]
    assert primeira.json()["total"] == segunda.json()["total"] == 4
    assert pagina_zero.status_code == 422
