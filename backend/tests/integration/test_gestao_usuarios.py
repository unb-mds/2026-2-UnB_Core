from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from backend.app.db import get_session
from backend.app.domain import (
    ConteudoAcademico,
    Contribuicao,
    Disciplina,
    EstadoContribuicao,
    TipoConteudo,
    Usuario,
)
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


def usuario(nome: str, email: str, perfil: str = "usuario") -> Usuario:
    return Usuario(nome=nome, email=email, senha_hash=hash_senha("senha-segura"), perfil=perfil)


def setup_function() -> None:
    app.dependency_overrides[get_session] = session_override
    app.router.lifespan_context = no_lifespan
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        disciplina = Disciplina(codigo="FGA0003", nome="COMPILADORES 1")
        admin = usuario("Ana Admin", "admin@example.com", "administrador")
        moderador = usuario("Mauro Moderador", "moderador@example.com", "moderador")
        estudante = usuario("Bia Estudante", "bia@example.com")
        outro = usuario("Caio", "caio@example.com")
        session.add_all([disciplina, admin, moderador, estudante, outro])
        session.flush()
        conteudo = ConteudoAcademico(
            disciplina_id=disciplina.id,
            tipo=TipoConteudo.RESUMO,
            titulo="Resumo publicado da Bia",
            corpo_ou_url="texto",
            autor_id=estudante.id,
        )
        session.add(conteudo)
        session.flush()
        session.add_all(
            [
                Contribuicao(
                    autor_id=estudante.id,
                    disciplina_id=disciplina.id,
                    conteudo_id=conteudo.id,
                    tipo=TipoConteudo.RESUMO,
                    titulo="Resumo publicado da Bia",
                    corpo_ou_url="texto",
                    estado=EstadoContribuicao.APROVADA,
                ),
                Contribuicao(
                    autor_id=estudante.id,
                    disciplina_id=disciplina.id,
                    tipo=TipoConteudo.DICA,
                    titulo="Dica pendente da Bia",
                    corpo_ou_url="texto",
                ),
            ]
        )
        session.commit()


def autenticar(client: TestClient, email: str, senha: str = "senha-segura") -> dict[str, str]:
    resposta = client.post("/api/v1/auth/login", json={"email": email, "senha": senha})
    assert resposta.status_code == 200, resposta.text
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


def ids_por_nome(resposta) -> dict[str, dict]:
    return {item["nome"]: item for item in resposta.json()}


def test_administrador_ve_todas_as_contas_com_email_e_contribuicoes() -> None:
    with TestClient(app) as client:
        admin = autenticar(client, "admin@example.com")
        resposta = client.get("/api/v1/usuarios/gestao", headers=admin)
        equipe = client.get("/api/v1/usuarios/gestao", headers=admin, params={"perfil": "equipe"})

    usuarios = ids_por_nome(resposta)
    assert set(usuarios) == {"Ana Admin", "Mauro Moderador", "Bia Estudante", "Caio"}
    assert usuarios["Bia Estudante"]["email"] == "bia@example.com"
    assert usuarios["Bia Estudante"]["total_contribuicoes"] == 2
    # Nem o hash da senha nem o campo aparecem na resposta.
    assert "senha_hash" not in resposta.text
    assert "$2b$" not in resposta.text
    assert set(ids_por_nome(equipe)) == {"Ana Admin", "Mauro Moderador"}


def test_moderador_ve_so_usuarios_comuns_e_sem_email() -> None:
    with TestClient(app) as client:
        moderador = autenticar(client, "moderador@example.com")
        resposta = client.get("/api/v1/usuarios/gestao", headers=moderador, params={"perfil": "administrador"})
        estudante = autenticar(client, "bia@example.com")
        sem_permissao = client.get("/api/v1/usuarios/gestao", headers=estudante)

    usuarios = ids_por_nome(resposta)
    # Mesmo pedindo administradores, o moderador só recebe usuários comuns.
    assert set(usuarios) == {"Bia Estudante", "Caio"}
    assert all(item["email"] is None for item in resposta.json())
    assert sem_permissao.status_code == 403


def test_moderador_desativa_usuario_comum_mas_nao_a_equipe() -> None:
    with TestClient(app) as client:
        moderador = autenticar(client, "moderador@example.com")
        admin = autenticar(client, "admin@example.com")
        ids = ids_por_nome(client.get("/api/v1/usuarios/gestao", headers=admin))

        desativou = client.patch(f"/api/v1/usuarios/{ids['Caio']['id']}/situacao", headers=moderador, json={"ativo": False})
        no_admin = client.patch(f"/api/v1/usuarios/{ids['Ana Admin']['id']}/situacao", headers=moderador, json={"ativo": False})
        excluir_admin = client.delete(f"/api/v1/usuarios/{ids['Ana Admin']['id']}", headers=moderador)
        login_desativado = client.post("/api/v1/auth/login", json={"email": "caio@example.com", "senha": "senha-segura"})

    assert desativou.status_code == 200
    assert desativou.json()["ativo"] is False
    assert no_admin.status_code == 403
    assert excluir_admin.status_code == 403
    assert login_desativado.status_code == 422


def test_excluir_conta_mantem_conteudos_publicados_como_usuario_removido() -> None:
    with TestClient(app) as client:
        moderador = autenticar(client, "moderador@example.com")
        admin = autenticar(client, "admin@example.com")
        bia = ids_por_nome(client.get("/api/v1/usuarios/gestao", headers=admin))["Bia Estudante"]

        resposta = client.delete(f"/api/v1/usuarios/{bia['id']}", headers=moderador)
        conteudos = client.get("/api/v1/disciplinas/1/conteudos").json()["itens"]
        restantes = ids_por_nome(client.get("/api/v1/usuarios/gestao", headers=admin))
        login = client.post("/api/v1/auth/login", json={"email": "bia@example.com", "senha": "senha-segura"})

    assert resposta.status_code == 204
    # O conteúdo publicado continua na base, sem o nome da pessoa.
    assert [(item["titulo"], item["autor_nome"]) for item in conteudos] == [("Resumo publicado da Bia", "Usuário removido")]
    # A conta some da gestão, e a conta de sistema não aparece.
    assert set(restantes) == {"Ana Admin", "Mauro Moderador", "Caio"}
    assert login.status_code == 422
    with Session(engine) as session:
        assert session.query(Contribuicao).count() == 0


def test_administrador_nao_exclui_a_propria_conta_mas_exclui_moderador() -> None:
    with TestClient(app) as client:
        admin = autenticar(client, "admin@example.com")
        ids = ids_por_nome(client.get("/api/v1/usuarios/gestao", headers=admin))

        propria = client.delete(f"/api/v1/usuarios/{ids['Ana Admin']['id']}", headers=admin)
        moderador = client.delete(f"/api/v1/usuarios/{ids['Mauro Moderador']['id']}", headers=admin)

    assert propria.status_code == 422
    assert propria.json()["erro"]["mensagem"] == "Você não pode excluir a sua própria conta."
    assert moderador.status_code == 204


def test_administrador_nao_exclui_a_propria_conta_mesmo_com_outro_administrador() -> None:
    with Session(engine) as session:
        session.add(usuario("Beto Admin", "beto@example.com", "administrador"))
        session.commit()

    with TestClient(app) as client:
        admin = autenticar(client, "admin@example.com")
        ids = ids_por_nome(client.get("/api/v1/usuarios/gestao", headers=admin))

        propria = client.delete(f"/api/v1/usuarios/{ids['Ana Admin']['id']}", headers=admin)
        outro_admin = client.delete(f"/api/v1/usuarios/{ids['Beto Admin']['id']}", headers=admin)

    # Com outro administrador ativo, só a regra da própria conta impede a exclusão.
    assert propria.status_code == 422
    assert propria.json()["erro"]["mensagem"] == "Você não pode excluir a sua própria conta."
    assert outro_admin.status_code == 204


def test_senha_temporaria_so_por_administrador_e_sem_expor_a_senha() -> None:
    with TestClient(app) as client:
        admin = autenticar(client, "admin@example.com")
        moderador = autenticar(client, "moderador@example.com")
        caio = ids_por_nome(client.get("/api/v1/usuarios/gestao", headers=admin))["Caio"]

        por_moderador = client.post(f"/api/v1/usuarios/{caio['id']}/senha-temporaria", headers=moderador, json={"nova_senha": "temporaria-123"})
        curta = client.post(f"/api/v1/usuarios/{caio['id']}/senha-temporaria", headers=admin, json={"nova_senha": "123"})
        resposta = client.post(f"/api/v1/usuarios/{caio['id']}/senha-temporaria", headers=admin, json={"nova_senha": "temporaria-123"})
        login_novo = client.post("/api/v1/auth/login", json={"email": "caio@example.com", "senha": "temporaria-123"})

    assert por_moderador.status_code == 403
    assert curta.status_code == 422
    assert resposta.status_code == 200
    assert "senha_hash" not in resposta.text
    assert "$2b$" not in resposta.text
    assert "temporaria-123" not in resposta.text
    assert login_novo.status_code == 200
