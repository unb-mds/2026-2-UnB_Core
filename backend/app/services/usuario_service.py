from datetime import datetime, timezone

from sqlmodel import Session, select

from backend.app.api.errors import ErroValidacao, NaoEncontrado
from backend.app.domain import PerfilUsuario, Usuario
from backend.app.services.auth_service import hash_senha


def listar_usuarios(session: Session) -> list[Usuario]:
    return list(session.exec(select(Usuario).order_by(Usuario.nome)).all())


def criar_usuario_admin(
    session: Session,
    *,
    nome: str,
    email: str,
    senha: str,
    perfil: PerfilUsuario,
) -> Usuario:
    if session.exec(select(Usuario).where(Usuario.email == email.lower())).first():
        raise ErroValidacao("Já existe uma conta cadastrada com este e-mail.")

    usuario = Usuario(
        nome=nome.strip(),
        email=email.lower(),
        senha_hash=hash_senha(senha),
        perfil=perfil,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def atualizar_usuario(
    session: Session,
    usuario_id: int,
    *,
    perfil: PerfilUsuario | None,
    ativo: bool | None,
) -> Usuario:
    usuario = session.get(Usuario, usuario_id)
    if usuario is None:
        raise NaoEncontrado("O usuário não foi encontrado.")
    if perfil is None and ativo is None:
        raise ErroValidacao("Informe ao menos o perfil ou o estado ativo.")

    if perfil is not None:
        usuario.perfil = perfil
    if ativo is not None:
        usuario.ativo = ativo
    usuario.atualizado_em = datetime.now(timezone.utc)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario
