import asyncio
from unittest.mock import AsyncMock, MagicMock

from backend.app import db
from backend.app.api import router
from backend.app.api.schema import categoria
from backend.app.main import criar_aplicacao
import backend.app.main as main_module


def test_roteador_api_tem_prefixo_esperado():
    assert router.api_router.prefix == "/api/v1"


def test_modelos_categoria_sao_importaveis():
    category = categoria.Categoria(nome="Ensino")

    assert category.nome == "Ensino"


def test_dependencia_sessao_fecha_apos_yield(monkeypatch):
    session = MagicMock()
    context = MagicMock()
    context.__enter__.return_value = session
    context.__exit__.return_value = None
    monkeypatch.setattr(db, "Session", lambda _engine: context)

    yielded = db.get_session()

    assert next(yielded) is session
    with __import__("pytest").raises(StopIteration):
        next(yielded)
    context.__exit__.assert_called_once()


def test_cria_banco_e_tabelas(monkeypatch):
    create_all = MagicMock()
    monkeypatch.setattr(db.SQLModel.metadata, "create_all", create_all)

    db.create_db_and_tables()

    create_all.assert_called_once_with(db.engine)


def test_fabrica_aplicacao():
    application = criar_aplicacao()

    assert application.title == "UNB CORE API"


def test_ciclo_de_vida_cria_banco(monkeypatch):
    create_tables = MagicMock()
    monkeypatch.setattr("backend.app.main.create_db_and_tables", create_tables)

    async def run_lifespan():
        async with __import__("backend.app.main", fromlist=["lifespan"]).lifespan(
            MagicMock()
        ):
            pass

    asyncio.run(run_lifespan())

    create_tables.assert_called_once()


def test_carga_inicial_vazia_carrega_cursos_disciplinas_e_curriculos(monkeypatch):
    session = MagicMock()
    session.exec.return_value.first.side_effect = [None, None]
    context = MagicMock()
    context.__enter__.return_value = session
    context.__exit__.return_value = None
    monkeypatch.setattr(main_module, "Session", lambda _engine: context)

    cursos = AsyncMock(return_value=2)
    disciplinas = AsyncMock(return_value=5)
    curriculos = AsyncMock(return_value=8)
    monkeypatch.setattr(main_module, "coletar_e_salvar_cursos", cursos)
    monkeypatch.setattr(main_module, "coletar_e_salvar_disciplinas", disciplinas)
    monkeypatch.setattr(
        main_module,
        "coletar_e_sincronizar_curriculos",
        curriculos,
    )

    asyncio.run(main_module._carregar_dados_iniciais())

    cursos.assert_awaited_once_with(session)
    disciplinas.assert_awaited_once_with(session)
    curriculos.assert_awaited_once_with(session)


def test_carga_inicial_existente_apenas_sincroniza_curriculos(monkeypatch):
    session = MagicMock()
    session.exec.return_value.first.side_effect = [1, 1]
    context = MagicMock()
    context.__enter__.return_value = session
    context.__exit__.return_value = None
    monkeypatch.setattr(main_module, "Session", lambda _engine: context)

    cursos = AsyncMock(return_value=0)
    disciplinas = AsyncMock(return_value=0)
    curriculos = AsyncMock(return_value=3)
    monkeypatch.setattr(main_module, "coletar_e_salvar_cursos", cursos)
    monkeypatch.setattr(main_module, "coletar_e_salvar_disciplinas", disciplinas)
    monkeypatch.setattr(
        main_module,
        "coletar_e_sincronizar_curriculos",
        curriculos,
    )

    asyncio.run(main_module._carregar_dados_iniciais())

    cursos.assert_not_awaited()
    disciplinas.assert_not_awaited()
    curriculos.assert_awaited_once_with(session)


def test_falha_de_disciplina_nao_bloqueia_sincronizacao(monkeypatch):
    session = MagicMock()
    session.exec.return_value.first.side_effect = [1, None]
    context = MagicMock()
    context.__enter__.return_value = session
    context.__exit__.return_value = None
    monkeypatch.setattr(main_module, "Session", lambda _engine: context)

    disciplinas = AsyncMock(side_effect=RuntimeError("falha parcial"))
    curriculos = AsyncMock(return_value=4)
    monkeypatch.setattr(main_module, "coletar_e_salvar_disciplinas", disciplinas)
    monkeypatch.setattr(
        main_module,
        "coletar_e_sincronizar_curriculos",
        curriculos,
    )

    asyncio.run(main_module._carregar_dados_iniciais())

    disciplinas.assert_awaited_once_with(session)
    curriculos.assert_awaited_once_with(session)
