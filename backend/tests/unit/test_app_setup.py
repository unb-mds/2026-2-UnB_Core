import asyncio
from unittest.mock import MagicMock

from backend.app import db
from backend.app.api import router
from backend.app.api.schema import categoria
from backend.app.main import criar_aplicacao


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
