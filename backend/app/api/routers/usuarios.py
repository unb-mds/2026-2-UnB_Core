from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from backend.app.api.dependencies import exigir_administrador
from backend.app.api.schemas.usuarios import (
    UsuarioAdminAtualizacao,
    UsuarioAdminCriacao,
    UsuarioAdminPublico,
)
from backend.app.db import get_session
from backend.app.domain import Usuario
from backend.app.services.usuario_service import (
    atualizar_usuario,
    criar_usuario_admin,
    listar_usuarios,
)

router = APIRouter(prefix="/usuarios", tags=["administração"])


@router.get("", response_model=list[UsuarioAdminPublico])
def listar(
    session: Session = Depends(get_session),
    _: Usuario = Depends(exigir_administrador),
):
    return listar_usuarios(session)


@router.post(
    "",
    response_model=UsuarioAdminPublico,
    status_code=status.HTTP_201_CREATED,
)
def criar(
    dados: UsuarioAdminCriacao,
    session: Session = Depends(get_session),
    _: Usuario = Depends(exigir_administrador),
):
    return criar_usuario_admin(session, **dados.model_dump())


@router.patch("/{usuario_id}", response_model=UsuarioAdminPublico)
def atualizar(
    usuario_id: int,
    dados: UsuarioAdminAtualizacao,
    session: Session = Depends(get_session),
    _: Usuario = Depends(exigir_administrador),
):
    return atualizar_usuario(session, usuario_id, **dados.model_dump())
