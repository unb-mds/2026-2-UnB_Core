from collections.abc import Callable

from fastapi import Depends
from sqlmodel import Session

from backend.app.api.errors import NaoAutenticado, PermissaoNegada
from backend.app.api.security import obter_usuario_token
from backend.app.db import get_session
from backend.app.domain import PerfilUsuario, Usuario


def obter_usuario_atual(
    payload: dict = Depends(obter_usuario_token),
    session: Session = Depends(get_session),
) -> Usuario:
    usuario_id = payload.get("sub")
    if not usuario_id:
        raise NaoAutenticado()

    usuario = session.get(Usuario, int(usuario_id))
    if usuario is None or not usuario.ativo:
        raise NaoAutenticado("A conta não existe ou está inativa.")
    return usuario


def exigir_perfil(*perfis: PerfilUsuario) -> Callable:
    def dependencia(
        usuario: Usuario = Depends(obter_usuario_atual),
    ) -> Usuario:
        if usuario.perfil not in perfis:
            raise PermissaoNegada()
        return usuario

    return dependencia


exigir_moderador = exigir_perfil(
    PerfilUsuario.MODERADOR,
    PerfilUsuario.ADMINISTRADOR,
)
exigir_administrador = exigir_perfil(PerfilUsuario.ADMINISTRADOR)
