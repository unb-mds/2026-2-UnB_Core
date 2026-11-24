from datetime import datetime, timezone

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


def atualizar_perfil(
    session: Session,
    usuario: Usuario,
    *,
    nome: str | None = None,
    email: str | None = None,
    senha_atual: str | None = None,
    nova_senha: str | None = None,
) -> Usuario:
    nome = nome.strip() if nome is not None else None
    email = email.lower() if email is not None else None
    altera_email = email is not None and email != usuario.email
    altera_nome = nome is not None and nome != usuario.nome

    if nome is not None and not nome:
        raise ErroValidacao("Informe o seu nome.")
    if not (altera_nome or altera_email or nova_senha):
        raise ErroValidacao("Informe ao menos um dado para alterar.")

    # Trocar e-mail ou senha muda o acesso à conta, então exige a senha atual.
    if (altera_email or nova_senha) and (
        not senha_atual or not verificar_senha(senha_atual, usuario.senha_hash)
    ):
        raise ErroValidacao("A senha atual está incorreta.")

    if altera_email and session.exec(
        select(Usuario).where(Usuario.email == email, Usuario.id != usuario.id)
    ).first():
        raise ErroValidacao("Já existe uma conta cadastrada com este e-mail.")

    if altera_nome:
        usuario.nome = nome
    if altera_email:
        usuario.email = email
    if nova_senha:
        usuario.senha_hash = hash_senha(nova_senha)
        # A senha temporária foi trocada por uma escolhida pela pessoa.
        usuario.trocar_senha = False
    usuario.atualizado_em = datetime.now(timezone.utc)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def criar_sessao(usuario: Usuario) -> str:
    if usuario.id is None:
        raise ErroValidacao("Não foi possível criar a sessão da conta.")
    return criar_access_token(usuario.id, usuario.perfil.value)


MENSAGEM_RECUPERACAO = (
    "Se o e-mail estiver cadastrado, a equipe do UnB Core vai definir uma senha "
    "temporária e entrar em contato com você."
)


def solicitar_recuperacao_senha(
    session: Session,
    email: str,
    contato: str | None = None,
) -> str:
    """Registra o pedido de nova senha para os administradores verem.

    A resposta é sempre a mesma, exista a conta ou não, para não revelar quem
    tem cadastro.
    """
    usuario = session.exec(select(Usuario).where(Usuario.email == email.lower())).first()
    if usuario is not None and usuario.ativo:
        usuario.recuperacao_senha_solicitada_em = datetime.now(timezone.utc)
        usuario.contato_recuperacao = (contato or "").strip() or None
        session.add(usuario)
        session.commit()
    return MENSAGEM_RECUPERACAO
