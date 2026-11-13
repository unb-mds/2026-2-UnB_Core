from unittest.mock import MagicMock

import pytest

from backend.app.api.routers import academico, auth, contribuicoes, moderacao, usuarios
from backend.app.api.schemas.auth import LoginRequest
from backend.app.api.schemas.contribuicao import ContribuicaoCriacao
from backend.app.api.schemas.moderacao import DecisaoModeracao, DecisaoRequest
from backend.app.api.schemas.usuarios import UsuarioAdminAtualizacao
from backend.app.domain import PerfilUsuario, TipoConteudo


def test_rotas_auth_delegam_para_servicos(monkeypatch, usuario):
    session = MagicMock()
    monkeypatch.setattr(auth, "autenticar_usuario", lambda *_args, **_kwargs: usuario)
    monkeypatch.setattr(auth, "criar_sessao", lambda *_args: "token")

    result = auth.login(LoginRequest(
        email="ana@example.com",
        senha="senha",
    ), session)

    assert result["access_token"] == "token"
    assert result["usuario"] is usuario


def test_auth_me_retorna_usuario(usuario):
    assert auth.me(usuario) is usuario


def test_rotas_de_contribuicao_delegam_para_servicos(monkeypatch, session, usuario):
    payload = ContribuicaoCriacao(
        disciplina_id=1,
        tipo=TipoConteudo.RESUMO,
        titulo="Resumo",
        corpo_ou_url="texto",
    )
    expected = object()
    monkeypatch.setattr(contribuicoes, "criar_contribuicao", lambda *args: expected)

    assert contribuicoes.criar(payload, session, usuario) is expected


def test_rotas_academicas_rejeitam_curso_inexistente(session):
    session.get.return_value = None

    with pytest.raises(Exception):
        academico.listar_disciplinas(1, session)


def test_rotas_academicas_listam_cursos(monkeypatch, session):
    expected = [object()]
    monkeypatch.setattr(academico, "listar_cursos_ativos", lambda *_: expected)

    assert academico.listar_cursos(session) == {"itens": expected}


def test_rotas_academicas_listam_disciplinas(monkeypatch, session):
    session.get.return_value = object()
    expected = [object()]
    monkeypatch.setattr(academico, "listar_disciplinas_ativas", lambda *_: expected)

    assert academico.listar_disciplinas(1, session) == {"itens": expected}


def test_rotas_academicas_listam_conteudo(monkeypatch, session):
    session.get.return_value = object()
    expected = [object()]
    monkeypatch.setattr(academico, "listar_conteudos_publicados", lambda *_: expected)

    assert academico.listar_conteudos(1, None, session) == {"itens": expected}


def test_rotas_academicas_rejeitam_disciplina_inexistente(session):
    session.get.return_value = None

    with pytest.raises(Exception):
        academico.listar_conteudos(1, None, session)


def test_rotas_academicas_detalham_conteudo(monkeypatch, session):
    expected = object()
    monkeypatch.setattr(academico, "obter_conteudo_publicado", lambda *_: expected)

    assert academico.detalhar_conteudo(1, session) is expected


def test_rota_admin_atualizacao_delega_para_servico(monkeypatch, session, usuario):
    expected = object()
    monkeypatch.setattr(usuarios, "atualizar_usuario", lambda *args, **kwargs: expected)

    result = usuarios.atualizar(
        1,
        UsuarioAdminAtualizacao(ativo=False),
        session,
        usuario,
    )

    assert result is expected


def test_rota_admin_lista_delega_para_servico(monkeypatch, session, usuario):
    expected = [object()]
    monkeypatch.setattr(usuarios, "listar_usuarios", lambda *_: expected)

    assert usuarios.listar(session, usuario) == expected


def test_rota_admin_criacao_delega_para_servico(monkeypatch, session, usuario):
    expected = object()
    monkeypatch.setattr(usuarios, "criar_usuario_admin", lambda *_args, **_kwargs: expected)
    from backend.app.api.schemas.usuarios import UsuarioAdminCriacao

    result = usuarios.criar(
        UsuarioAdminCriacao(
            nome="Admin",
            email="admin@example.com",
            senha="senha-segura",
        ),
        session,
        usuario,
    )

    assert result is expected


def test_rota_moderacao_delega_para_servico(monkeypatch, session, moderador):
    expected = object()
    monkeypatch.setattr(moderacao, "decidir_contribuicao", lambda *args: expected)

    result = moderacao.decidir(
        1,
        DecisaoRequest(
            decisao=DecisaoModeracao.APROVAR,
            justificativa=None,
        ),
        session,
        moderador,
    )

    assert result is expected


def test_rota_moderacao_lista_delega_para_servico(monkeypatch, session, moderador):
    expected = [object()]
    monkeypatch.setattr(moderacao, "listar_para_moderacao", lambda *_: expected)

    assert moderacao.listar_contribuicoes(session, moderador) == expected


def test_rota_lista_de_contribuicoes_delega_para_servico(monkeypatch, session, usuario):
    expected = [object()]
    monkeypatch.setattr(
        contribuicoes,
        "listar_contribuicoes_do_usuario",
        lambda *_: expected,
    )

    assert contribuicoes.minhas(session, usuario) == expected
