from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from backend.app.domain import (
    Contribuicao,
    Disciplina,
    EstadoContribuicao,
    EstadoConteudo,
    PerfilUsuario,
    TipoConteudo,
    Usuario,
)


@pytest.fixture
def session():
    return MagicMock()


@pytest.fixture
def usuario():
    return Usuario(
        id=1,
        nome="Ana",
        email="ana@example.com",
        senha_hash="hash",
        perfil=PerfilUsuario.USUARIO,
    )


@pytest.fixture
def moderador():
    return Usuario(
        id=2,
        nome="Moderador",
        email="moderador@example.com",
        senha_hash="hash",
        perfil=PerfilUsuario.MODERADOR,
    )


@pytest.fixture
def disciplina():
    return Disciplina(
        id=1,
        curso_id=10,
        codigo="CIC-0123",
        nome="Computação",
    )


@pytest.fixture
def contribuicao():
    return Contribuicao(
        id=1,
        autor_id=1,
        disciplina_id=1,
        tipo=TipoConteudo.RESUMO,
        titulo="Resumo",
        corpo_ou_url="Conteúdo",
        estado=EstadoContribuicao.PENDENTE,
    )
