from backend.app.services.curso_service import (
    listar_cursos_ativos,
    listar_disciplinas_ativas,
)


def test_lista_cursos_ativos(session):
    expected = [object()]
    session.exec.return_value.all.return_value = expected

    assert listar_cursos_ativos(session) == expected


def test_lista_disciplinas_ativas(session):
    expected = [object()]
    session.exec.return_value.all.return_value = expected

    assert listar_disciplinas_ativas(session, 10) == expected
