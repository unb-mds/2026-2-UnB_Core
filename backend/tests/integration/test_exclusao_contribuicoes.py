from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.app.db import get_session
from backend.app.domain import Curso, CursoDisciplina, Disciplina, Usuario
from backend.app.main import app
from backend.app.services.auth_service import hash_senha


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
        curso = Curso(nome="ENGENHARIA DE SOFTWARE", sigla="FCTE")
        disciplina = Disciplina(codigo="FGA0003", nome="COMPILADORES 1")
        session.add_all(
            [
                curso,
                disciplina,
                Usuario(
                    nome="Moderadora",
                    email="moderadora@example.com",
                    senha_hash=hash_senha("senha-segura"),
                    perfil="moderador",
                ),
                Usuario(
                    nome="Ana Souza",
                    email="ana@example.com",
                    senha_hash=hash_senha("senha-segura"),
                ),
                Usuario(
                    nome="Bruno",
                    email="bruno@example.com",
                    senha_hash=hash_senha("senha-segura"),
                ),
            ]
        )
        session.flush()
        session.add(CursoDisciplina(curso_id=curso.id, disciplina_id=disciplina.id))
        session.commit()


def autenticar(client: TestClient, email: str) -> dict[str, str]:
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "senha-segura"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def enviar(client: TestClient, autor: dict[str, str], titulo: str = "Resumo") -> int:
    return client.post(
        "/api/v1/contribuicoes",
        headers=autor,
        json={"disciplina_id": 1, "tipo": "resumo", "titulo": titulo, "corpo_ou_url": "Texto"},
    ).json()["id"]


def aprovar(client: TestClient, moderador: dict[str, str], contribuicao_id: int) -> None:
    resposta = client.post(
        f"/api/v1/moderacao/contribuicoes/{contribuicao_id}/decisao",
        headers=moderador,
        json={"decisao": "aprovar"},
    )
    assert resposta.status_code == 200


def test_autor_exclui_na_hora_contribuicao_nao_publicada() -> None:
    with TestClient(app) as client:
        ana = autenticar(client, "ana@example.com")
        contribuicao_id = enviar(client, ana)

        resposta = client.delete(f"/api/v1/contribuicoes/minhas/{contribuicao_id}", headers=ana)

        assert resposta.status_code == 204
        assert client.get("/api/v1/contribuicoes/minhas", headers=ana).json() == []


def test_publicada_exige_pedido_e_moderador_exclui_de_vez() -> None:
    with TestClient(app) as client:
        ana = autenticar(client, "ana@example.com")
        moderadora = autenticar(client, "moderadora@example.com")
        contribuicao_id = enviar(client, ana)
        aprovar(client, moderadora, contribuicao_id)
        conteudo_id = client.get(f"/api/v1/contribuicoes/minhas/{contribuicao_id}", headers=ana).json()["conteudo_id"]

        direto = client.delete(f"/api/v1/contribuicoes/minhas/{contribuicao_id}", headers=ana)
        assert direto.status_code == 422

        pedido = client.post(
            f"/api/v1/contribuicoes/minhas/{contribuicao_id}/pedido-exclusao",
            headers=ana,
            json={"motivo": "Encontrei um erro no resumo."},
        )
        assert pedido.status_code == 200
        assert pedido.json()["exclusao_solicitada_em"] is not None
        assert pedido.json()["motivo_exclusao"] == "Encontrei um erro no resumo."

        fila = client.get("/api/v1/moderacao/contribuicoes", headers=moderadora, params={"filtro": "exclusao"})
        assert [item["id"] for item in fila.json()] == [contribuicao_id]
        assert fila.json()[0]["autor_nome"] == "Ana Souza"
        assert fila.json()[0]["disciplina_nome"] == "COMPILADORES 1"

        exclusao = client.delete(f"/api/v1/moderacao/contribuicoes/{contribuicao_id}", headers=moderadora)
        assert exclusao.status_code == 204

        assert client.get(f"/api/v1/conteudos/{conteudo_id}").status_code == 404
        assert client.get("/api/v1/disciplinas/1/conteudos").json()["itens"] == []
        assert client.get("/api/v1/contribuicoes/minhas", headers=ana).json() == []


def test_moderador_recusa_pedido_e_autor_ve_a_justificativa() -> None:
    with TestClient(app) as client:
        ana = autenticar(client, "ana@example.com")
        moderadora = autenticar(client, "moderadora@example.com")
        contribuicao_id = enviar(client, ana)
        aprovar(client, moderadora, contribuicao_id)

        sem_pedido = client.post(
            f"/api/v1/moderacao/contribuicoes/{contribuicao_id}/recusar-exclusao",
            headers=moderadora,
            json={"justificativa": "Conteúdo está correto."},
        )
        assert sem_pedido.status_code == 422

        client.post(
            f"/api/v1/contribuicoes/minhas/{contribuicao_id}/pedido-exclusao",
            headers=ana,
            json={"motivo": "Quero tirar do ar."},
        )
        recusa = client.post(
            f"/api/v1/moderacao/contribuicoes/{contribuicao_id}/recusar-exclusao",
            headers=moderadora,
            json={"justificativa": "O conteúdo está correto e ajuda a turma."},
        )

        assert recusa.status_code == 200
        minha = client.get(f"/api/v1/contribuicoes/minhas/{contribuicao_id}", headers=ana).json()
        assert minha["exclusao_solicitada_em"] is None
        assert minha["justificativa_moderacao"] == "Pedido de exclusão recusado: O conteúdo está correto e ajuda a turma."
        assert client.get("/api/v1/moderacao/contribuicoes", headers=moderadora, params={"filtro": "exclusao"}).json() == []


def test_autor_cancela_o_proprio_pedido() -> None:
    with TestClient(app) as client:
        ana = autenticar(client, "ana@example.com")
        moderadora = autenticar(client, "moderadora@example.com")
        contribuicao_id = enviar(client, ana)
        aprovar(client, moderadora, contribuicao_id)
        client.post(
            f"/api/v1/contribuicoes/minhas/{contribuicao_id}/pedido-exclusao",
            headers=ana,
            json={"motivo": "Mudei de ideia depois."},
        )

        cancelado = client.delete(f"/api/v1/contribuicoes/minhas/{contribuicao_id}/pedido-exclusao", headers=ana)

        assert cancelado.status_code == 200
        assert cancelado.json()["exclusao_solicitada_em"] is None


def test_regras_de_permissao_e_validacao() -> None:
    with TestClient(app) as client:
        ana = autenticar(client, "ana@example.com")
        bruno = autenticar(client, "bruno@example.com")
        contribuicao_id = enviar(client, ana)

        # Pedido só vale para publicadas; motivo precisa de pelo menos 5 caracteres.
        nao_publicada = client.post(
            f"/api/v1/contribuicoes/minhas/{contribuicao_id}/pedido-exclusao",
            headers=ana,
            json={"motivo": "Quero excluir."},
        )
        motivo_curto = client.post(
            f"/api/v1/contribuicoes/minhas/{contribuicao_id}/pedido-exclusao",
            headers=ana,
            json={"motivo": "não"},
        )
        assert nao_publicada.status_code == 422
        assert motivo_curto.status_code == 422

        # Outra pessoa não exclui nem pede exclusão; usuário comum não usa a moderação.
        assert client.delete(f"/api/v1/contribuicoes/minhas/{contribuicao_id}", headers=bruno).status_code == 422
        assert client.delete(f"/api/v1/moderacao/contribuicoes/{contribuicao_id}", headers=bruno).status_code == 403
        assert client.get(f"/api/v1/moderacao/contribuicoes/{contribuicao_id}", headers=bruno).status_code == 403
        assert client.delete(f"/api/v1/contribuicoes/minhas/{contribuicao_id}").status_code == 401

        # A contribuição continua lá.
        assert len(client.get("/api/v1/contribuicoes/minhas", headers=ana).json()) == 1


def test_moderador_lista_todas_e_ve_o_detalhe() -> None:
    with TestClient(app) as client:
        ana = autenticar(client, "ana@example.com")
        moderadora = autenticar(client, "moderadora@example.com")
        primeira = enviar(client, ana, "Primeira")
        segunda = enviar(client, ana, "Segunda")
        aprovar(client, moderadora, primeira)

        revisar = client.get("/api/v1/moderacao/contribuicoes", headers=moderadora)
        todas = client.get("/api/v1/moderacao/contribuicoes", headers=moderadora, params={"filtro": "todas"})
        detalhe = client.get(f"/api/v1/moderacao/contribuicoes/{segunda}", headers=moderadora)
        inexistente = client.get("/api/v1/moderacao/contribuicoes/999", headers=moderadora)

        # Sem filtro continua como antes: só as que esperam revisão.
        assert [item["id"] for item in revisar.json()] == [segunda]
        assert {item["id"] for item in todas.json()} == {primeira, segunda}
        assert detalhe.json()["titulo"] == "Segunda"
        assert detalhe.json()["autor_nome"] == "Ana Souza"
        assert inexistente.status_code == 404
