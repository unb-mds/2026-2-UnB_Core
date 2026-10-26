from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from backend.app.api.dependencies import obter_usuario_atual
from backend.app.api.schemas.auth import (
    CadastroRequest,
    LoginRequest,
    TokenResponse,
    UsuarioPublico,
)
from backend.app.db import get_session
from backend.app.domain import Usuario
from backend.app.services.auth_service import (
    autenticar_usuario,
    cadastrar_usuario,
    criar_sessao,
)

router = APIRouter(prefix="/auth", tags=["autenticação"])


@router.post(
    "/cadastro",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,
)
def cadastro(
    dados: CadastroRequest,
    session: Session = Depends(get_session),
):
    return cadastrar_usuario(session, **dados.model_dump())


@router.post("/login", response_model=TokenResponse)
def login(
    dados: LoginRequest,
    session: Session = Depends(get_session),
):
    usuario = autenticar_usuario(session, **dados.model_dump())
    return {
        "access_token": criar_sessao(usuario),
        "token_type": "bearer",
        "usuario": usuario,
    }


@router.get("/me", response_model=UsuarioPublico)
def me(usuario: Usuario = Depends(obter_usuario_atual)):
    return usuario
