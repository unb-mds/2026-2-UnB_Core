import secrets
from datetime import datetime, timezone

from sqlmodel import Session, func, select

from backend.app.api.errors import ErroValidacao, NaoEncontrado, PermissaoNegada
from backend.app.domain import ConteudoAcademico, Contribuicao, PerfilUsuario, Usuario
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


def garantir_usuario_admin(
    session: Session,
    *,
    nome: str,
    email: str,
    senha: str,
) -> Usuario:
    email_normalizado = email.strip().lower()
    usuario = session.exec(
        select(Usuario).where(Usuario.email == email_normalizado)
    ).first()
    if usuario is not None:
        if usuario.perfil != PerfilUsuario.ADMINISTRADOR:
            raise ErroValidacao(
                "O e-mail configurado para o administrador já pertence a "
                "uma conta sem perfil de administrador."
            )
        return usuario

    return criar_usuario_admin(
        session,
        nome=nome,
        email=email_normalizado,
        senha=senha,
        perfil=PerfilUsuario.ADMINISTRADOR,
    )


def atualizar_usuario(
    session: Session,
    usuario_id: int,
    *,
    perfil: PerfilUsuario | None,
    ativo: bool | None,
    usuario_atual_id: int | None = None,
) -> Usuario:
    usuario = session.get(Usuario, usuario_id)
    if usuario is None:
        raise NaoEncontrado("O usuário não foi encontrado.")
    if perfil is None and ativo is None:
        raise ErroValidacao("Informe ao menos o perfil ou o estado ativo.")

    # Impede que o administrador se bloqueie: ao desativar a própria conta ou
    # remover o próprio perfil de administrador, ele perderia o acesso
    # necessário para desfazer a alteração.
    if usuario_atual_id is not None and usuario.id == usuario_atual_id:
        if ativo is False:
            raise ErroValidacao("Você não pode desativar a sua própria conta.")
        if perfil is not None and perfil != PerfilUsuario.ADMINISTRADOR:
            raise ErroValidacao(
                "Você não pode remover o seu próprio perfil de administrador."
            )

    if perfil is not None:
        usuario.perfil = perfil
    if ativo is not None:
        usuario.ativo = ativo
    usuario.atualizado_em = datetime.now(timezone.utc)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


# ---------- Gestão de usuários (administradores e moderadores) ----------
# A senha nunca é lida nem devolvida: só pode ser redefinida por um administrador.

EMAIL_USUARIO_REMOVIDO = "usuario-removido@unbcore.example"
FILTROS_DE_PERFIL = {
    "usuario": [PerfilUsuario.USUARIO],
    "moderador": [PerfilUsuario.MODERADOR],
    "administrador": [PerfilUsuario.ADMINISTRADOR],
    "equipe": [PerfilUsuario.MODERADOR, PerfilUsuario.ADMINISTRADOR],
}


def _eh_administrador(usuario: Usuario) -> bool:
    return usuario.perfil == PerfilUsuario.ADMINISTRADOR


def _checar_alcance(ator: Usuario, alvo: Usuario) -> None:
    """Moderadores só agem sobre usuários comuns; ninguém age sobre a conta de sistema."""
    if alvo.email == EMAIL_USUARIO_REMOVIDO:
        raise ErroValidacao("Esta é uma conta de sistema e não pode ser alterada.")
    if not _eh_administrador(ator) and alvo.perfil != PerfilUsuario.USUARIO:
        raise PermissaoNegada("Moderadores só podem gerir contas de usuários comuns.")


def listar_usuarios_para_gestao(
    session: Session,
    ator: Usuario,
    *,
    busca: str | None = None,
    perfil: str | None = None,
    ativo: bool | None = None,
    recuperacao: bool | None = None,
) -> list[dict]:
    """Usuários com o total de contribuições. Moderadores veem só usuários comuns, sem e-mail."""
    perfis = FILTROS_DE_PERFIL.get(perfil or "", list(PerfilUsuario))
    if not _eh_administrador(ator):
        perfis = [PerfilUsuario.USUARIO]

    total = (
        select(Contribuicao.autor_id, func.count(Contribuicao.id).label("total"))
        .group_by(Contribuicao.autor_id)
        .subquery()
    )
    consulta = (
        select(Usuario, func.coalesce(total.c.total, 0))
        .outerjoin(total, total.c.autor_id == Usuario.id)
        .where(Usuario.perfil.in_(perfis), Usuario.email != EMAIL_USUARIO_REMOVIDO)
        .order_by(Usuario.nome)
    )
    if ativo is not None:
        consulta = consulta.where(Usuario.ativo == ativo)
    # Pedidos de nova senha: só administradores veem e filtram.
    if recuperacao and _eh_administrador(ator):
        consulta = consulta.where(Usuario.recuperacao_senha_solicitada_em.is_not(None))
    termo = (busca or "").strip().lower()
    if termo:
        filtro = func.lower(Usuario.nome).contains(termo)
        if _eh_administrador(ator):
            filtro = filtro | func.lower(Usuario.email).contains(termo)
        consulta = consulta.where(filtro)

    return [
        {
            "id": usuario.id,
            "nome": usuario.nome,
            # E-mail é dado pessoal: só administradores veem.
            "email": usuario.email if _eh_administrador(ator) else None,
            "perfil": usuario.perfil,
            "ativo": usuario.ativo,
            "criado_em": usuario.criado_em,
            "total_contribuicoes": total_contribuicoes,
            "recuperacao_senha_solicitada_em": (
                usuario.recuperacao_senha_solicitada_em if _eh_administrador(ator) else None
            ),
            "contato_recuperacao": usuario.contato_recuperacao if _eh_administrador(ator) else None,
        }
        for usuario, total_contribuicoes in session.exec(consulta).all()
    ]


def alterar_situacao(session: Session, ator: Usuario, usuario_id: int, ativo: bool) -> Usuario:
    """Ativa ou desativa uma conta, respeitando o alcance de quem age."""
    alvo = session.get(Usuario, usuario_id)
    if alvo is None:
        raise NaoEncontrado("O usuário não foi encontrado.")
    _checar_alcance(ator, alvo)
    if alvo.id == ator.id and not ativo:
        raise ErroValidacao("Você não pode desativar a sua própria conta.")
    alvo.ativo = ativo
    alvo.atualizado_em = datetime.now(timezone.utc)
    session.add(alvo)
    session.commit()
    session.refresh(alvo)
    return alvo


def _obter_usuario_removido(session: Session) -> Usuario:
    conta = session.exec(select(Usuario).where(Usuario.email == EMAIL_USUARIO_REMOVIDO)).first()
    if conta is None:
        conta = Usuario(
            nome="Usuário removido",
            email=EMAIL_USUARIO_REMOVIDO,
            # Senha aleatória e conta desativada: ninguém consegue entrar com ela.
            senha_hash=hash_senha(secrets.token_urlsafe(32)),
            perfil=PerfilUsuario.USUARIO,
            ativo=False,
        )
        session.add(conta)
        session.flush()
    return conta


def excluir_usuario(session: Session, ator: Usuario, usuario_id: int) -> None:
    """Exclui a conta de vez.

    Os conteúdos já publicados continuam na base, com o autor "Usuário removido";
    as contribuições da pessoa (publicadas ou não) são apagadas.
    """
    alvo = session.get(Usuario, usuario_id)
    if alvo is None:
        raise NaoEncontrado("O usuário não foi encontrado.")
    _checar_alcance(ator, alvo)
    if alvo.id == ator.id:
        raise ErroValidacao("Você não pode excluir a sua própria conta.")
    if alvo.perfil == PerfilUsuario.ADMINISTRADOR:
        outros_admins = session.exec(
            select(func.count(Usuario.id)).where(
                Usuario.perfil == PerfilUsuario.ADMINISTRADOR,
                Usuario.ativo,
                Usuario.id != alvo.id,
            )
        ).one()
        if outros_admins == 0:
            raise ErroValidacao("Não é possível excluir o último administrador ativo.")

    removido = _obter_usuario_removido(session)
    for conteudo in session.exec(
        select(ConteudoAcademico).where(ConteudoAcademico.autor_id == alvo.id)
    ).all():
        conteudo.autor_id = removido.id
        session.add(conteudo)
    for contribuicao in session.exec(
        select(Contribuicao).where(Contribuicao.autor_id == alvo.id)
    ).all():
        session.delete(contribuicao)
    session.flush()
    session.delete(alvo)
    session.commit()


def definir_senha_temporaria(session: Session, usuario_id: int, nova_senha: str) -> Usuario:
    """Só administradores: define uma senha nova sem ver a anterior."""
    alvo = session.get(Usuario, usuario_id)
    if alvo is None:
        raise NaoEncontrado("O usuário não foi encontrado.")
    if alvo.email == EMAIL_USUARIO_REMOVIDO:
        raise ErroValidacao("Esta é uma conta de sistema e não pode ser alterada.")
    alvo.senha_hash = hash_senha(nova_senha)
    # Pedido atendido; a pessoa troca a senha temporária ao entrar.
    alvo.recuperacao_senha_solicitada_em = None
    alvo.contato_recuperacao = None
    alvo.trocar_senha = True
    alvo.atualizado_em = datetime.now(timezone.utc)
    session.add(alvo)
    session.commit()
    session.refresh(alvo)
    return alvo
