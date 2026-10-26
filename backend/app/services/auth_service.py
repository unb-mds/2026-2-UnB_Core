from passlib.context import CryptContext
from sqlmodel import Session, select

from backend.app.api.errors import ErroValidacao
from backend.app.api.security import criar_access_token
from backend.app.domain import PerfilUsuario, Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha[:72])


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha[:72], senha_hash)


def cadastrar_usuario(
    session: Session,
    *,
    nome: str,
    email: str,
    senha: str,
) -> Usuario:
    if session.exec(select(Usuario).where(Usuario.email == email)).first():
        raise ErroValidacao("Já existe uma conta cadastrada com este e-mail.")

    usuario = Usuario(
        nome=nome.strip(),
        email=email.lower(),
        senha_hash=hash_senha(senha),
        perfil=PerfilUsuario.USUARIO,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def autenticar_usuario(
    session: Session,
    *,
    email: str,
    senha: str,
) -> Usuario:
    usuario = session.exec(
        select(Usuario).where(Usuario.email == email.lower())
    ).first()
    if usuario is None or not usuario.ativo or not verificar_senha(
        senha, usuario.senha_hash
    ):
        raise ErroValidacao("E-mail ou senha incorretos.")
    return usuario


def criar_sessao(usuario: Usuario) -> str:
    if usuario.id is None:
        raise ErroValidacao("Não foi possível criar a sessão da conta.")
    return criar_access_token(usuario.id, usuario.perfil.value)
