from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status
from sqlmodel import Session

from backend.app.api.dependencies import exigir_administrador, exigir_moderador
from backend.app.api.schemas.usuarios import (
    SenhaTemporaria,
    SituacaoUsuario,
    UsuarioAdminAtualizacao,
    UsuarioAdminCriacao,
    UsuarioAdminPublico,
    UsuarioGestao,
)
from backend.app.db import get_session
from backend.app.domain import Usuario
from backend.app.services.usuario_service import (
    alterar_situacao,
    atualizar_usuario,
    criar_usuario_admin,
    definir_senha_temporaria,
    excluir_usuario,
    listar_usuarios,
    listar_usuarios_para_gestao,
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
    administrador: Usuario = Depends(exigir_administrador),
):
    return atualizar_usuario(
        session,
        usuario_id,
        **dados.model_dump(),
        usuario_atual_id=administrador.id,
    )


# ---------- Gestão de contas ----------
# Administradores gerem todas as contas; moderadores só as de usuários comuns,
# sem ver o e-mail. Ninguém lê a senha de outra pessoa.


@router.get("/gestao", response_model=list[UsuarioGestao])
def listar_para_gestao(
    busca: str | None = Query(default=None, max_length=100),
    perfil: Literal["usuario", "moderador", "administrador", "equipe"] | None = Query(default=None),
    ativo: bool | None = Query(default=None),
    session: Session = Depends(get_session),
    ator: Usuario = Depends(exigir_moderador),
):
    return listar_usuarios_para_gestao(session, ator, busca=busca, perfil=perfil, ativo=ativo)


@router.patch("/{usuario_id}/situacao", response_model=UsuarioAdminPublico)
def alterar_situacao_da_conta(
    usuario_id: int,
    dados: SituacaoUsuario,
    session: Session = Depends(get_session),
    ator: Usuario = Depends(exigir_moderador),
):
    return alterar_situacao(session, ator, usuario_id, dados.ativo)


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def excluir_conta(
    usuario_id: int,
    session: Session = Depends(get_session),
    ator: Usuario = Depends(exigir_moderador),
):
    """Exclui a conta de vez; os conteúdos publicados ficam como "Usuário removido"."""
    excluir_usuario(session, ator, usuario_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{usuario_id}/senha-temporaria", response_model=UsuarioAdminPublico)
def senha_temporaria(
    usuario_id: int,
    dados: SenhaTemporaria,
    session: Session = Depends(get_session),
    _: Usuario = Depends(exigir_administrador),
):
    """Define uma senha temporária sem expor a anterior; a pessoa troca em Meu perfil."""
    return definir_senha_temporaria(session, usuario_id, dados.nova_senha)
