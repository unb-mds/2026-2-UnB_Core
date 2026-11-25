from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from backend.app.api.security import criar_access_token, obter_usuario_token
from backend.app.settings.config import settings


def daqui_a(minutos: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutos)


def assert_recusado(token: str) -> None:
    with pytest.raises(HTTPException) as erro:
        obter_usuario_token(token)
    assert erro.value.status_code == 401


def test_token_criado_pela_api_e_aceito() -> None:
    payload = obter_usuario_token(criar_access_token(7, "moderador"))

    assert payload["sub"] == "7"
    assert payload["perfil"] == "moderador"


def test_token_assinado_com_outra_chave_e_recusado() -> None:
    # Sem conferir a assinatura, qualquer pessoa forjaria um login de administrador.
    forjado = jwt.encode(
        {"sub": "1", "perfil": "administrador", "exp": daqui_a(5)},
        "uma-chave-que-nao-e-a-da-api-com-mais-de-32-bytes",
        algorithm=settings.jwt_algorithm,
    )

    assert_recusado(forjado)


def test_token_sem_assinatura_e_recusado() -> None:
    sem_assinatura = jwt.encode({"sub": "1", "perfil": "administrador", "exp": daqui_a(5)}, None, algorithm="none")

    assert_recusado(sem_assinatura)


def test_token_vencido_e_recusado() -> None:
    vencido = jwt.encode(
        {"sub": "1", "perfil": "usuario", "exp": daqui_a(-1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    assert_recusado(vencido)


def test_token_sem_usuario_e_recusado() -> None:
    sem_usuario = jwt.encode(
        {"perfil": "usuario", "exp": daqui_a(5)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    assert_recusado(sem_usuario)


def test_texto_que_nao_e_token_e_recusado() -> None:
    assert_recusado("isto-nao-e-um-token")
