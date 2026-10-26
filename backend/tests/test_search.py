from types import SimpleNamespace
from unittest.mock import MagicMock

from backend.tests.test_config import test_engine
from backend.app.api.search import buscar


def test_buscar_retorna_listas_vazias_sem_termo():
    session = MagicMock()

    response = buscar(None, session)

    assert response.conteudos_academicos == []
    assert response.publicacoes_institucionais == []
    session.exec.assert_not_called()


def test_buscar_filtra_conteudos_e_publicacoes():
    conteudo = SimpleNamespace(
        id=1,
        disciplina_id=2,
        tipo="artigo",
        titulo="Python",
        corpo_ou_url="material Python",
        origem="UnB",
        estado="publicado",
        autor_id=3,
        criado_em=None,
        atualizado_em=None,
    )
    publicacao = SimpleNamespace(
        publicacao_id=4,
        titulo="Edital Python",
        resumo="Resumo",
        categoria="ensino",
        unidade_responsavel="UnB",
        url_oficial="https://unb.br/edital",
        estado="ativa",
        curso_id=None,
        prazo_inicio=None,
        prazo_fim=None,
        publicado_em=None,
        ultima_verificacao=None,
    )
    session = MagicMock()
    first = MagicMock()
    first.all.return_value = [conteudo]
    second = MagicMock()
    second.all.return_value = [publicacao]
    session.exec.side_effect = [first, second]

    response = buscar("Python", session)

    assert response.conteudos_academicos[0].titulo == "Python"
    assert response.publicacoes_institucionais[0].publicacao_id == 4
