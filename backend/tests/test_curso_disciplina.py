from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from backend.tests.test_config import test_engine
from backend.app.api.schema.disciplina import GetListaCurso


def test_listar_disciplinas_de_curso_sem_disciplinas():
    session = MagicMock()
    session.get.return_value = SimpleNamespace(
        nome="Computação",
        sigla="CC",
        ativo=True,
        disciplina_id=[],
    )

    assert GetListaCurso(1, session) == []


def test_listar_disciplinas_de_curso_inexistente():
    session = MagicMock()
    session.get.return_value = None

    with pytest.raises(HTTPException) as error:
        GetListaCurso(99, session)

    assert error.value.status_code == 404
