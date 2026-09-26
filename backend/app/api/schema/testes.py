import pytest
from pydantic import ValidationError
from sqlmodel import Session, SQLModel, create_engine
from typing import Generator

# Importando os modelos criados
from usuario import Usuario, UsuarioCreate
from SubmissaoBase import Submissao,SubmissaoBase
from ConteudoAcademico import ConteudoAcademico, ConteudoAcademicoCreate
from Contribuicao import Contribuicao, ContribuicaoCreate


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


# ==========================================
# TESTES: USUÁRIO
# ==========================================
def test_usuario_create_valido():
    # Testa os campos base e tipos em usuario.py
    usuario_in = UsuarioCreate(
        email="aluno@unb.br",
        nome="João",
        perfil="Aluno",
        status="Online"
    )
    assert usuario_in.nome == "João"


def test_usuario_email_invalido():
    # Testa a tipagem EmailStr do Pydantic
    with pytest.raises(ValidationError, match="value is not a valid email address"):
        UsuarioCreate(
            email="email_quebrado",
            nome="João",
            perfil="Aluno",
            status="Online"
        )


def test_usuario_status_invalido():
    # Testa o @field_validator("status") de usuario.py
    with pytest.raises(ValidationError, match="deve ser um dos status"):
        UsuarioCreate(
            email="aluno@unb.br",
            nome="João",
            perfil="Aluno",
            status="Inexistente"
        )


def test_salvar_usuario_no_banco(session: Session):
    usuario_in = UsuarioCreate(
        email="aluno@unb.br",
        nome="João",
        perfil="Aluno",
        status="Online"
    )

    # Valida e converte, gerando as datas automaticamente pelo banco
    usuario_db = Usuario.model_validate(usuario_in)
    session.add(usuario_db)
    session.commit()
    session.refresh(usuario_db)

    assert usuario_db.id is not None
    assert usuario_db.criado_em is not None


# ==========================================
# TESTES: CONTEUDO ACADÊMICO
# ==========================================
def test_conteudo_create_valido():
    conteudo_in = ConteudoAcademicoCreate(
        disciplina_id=1,
        tipo="Artigo",
        origem="Web",
        estado="pendente",
        corpo_ou_url="https://github.com"
    )
    # HttpUrl do Pydantic converte a string para um objeto de URL seguro
    assert str(conteudo_in.corpo_ou_url) == "https://github.com"


def test_conteudo_estado_invalido():
    # Testa o validador herdado de SubmissaoBase.py
    with pytest.raises(ValidationError, match="deve ser um dos status"):
        ConteudoAcademicoCreate(
            disciplina_id=1,
            tipo="Artigo",
            origem="Web",
            estado="invalido",
            corpo_ou_url="https://github.com"
        )


def test_salvar_conteudo_no_banco(session: Session):
    conteudo_in = ConteudoAcademicoCreate(
        disciplina_id=1,
        tipo="Artigo",
        origem="Web",
        estado="pendente",
        corpo_ou_url="https://github.com"
    )

    # Injeção de dados do servidor: o update adiciona os campos que faltam
    # para a classe do banco (como o autor_id que isolamos na arquitetura)
    conteudo_db = ConteudoAcademico.model_validate(conteudo_in, update={"autor_id": 42})

    session.add(conteudo_db)
    session.commit()
    session.refresh(conteudo_db)

    assert conteudo_db.id is not None
    assert conteudo_db.autor_id == 42


# ==========================================
# TESTES: CONTRIBUIÇÃO
# ==========================================
def test_contribuicao_create_valido():
    contribuicao_in = ContribuicaoCreate(
        disciplina_id=2,
        tipo="Ajuste",
        origem="Sistema",
        estado="pendente",
        conteudo_id=10,
        autor_id=5,
        payload="publicado",
        justificativa_moderacao="Corrigindo erro de digitação"
    )
    assert contribuicao_in.conteudo_id == 10


def test_contribuicao_payload_invalido():
    # Testa o @field_validator("payload") específico de Contribuicao.py
    with pytest.raises(ValidationError, match="deve ser um dos status"):
        ContribuicaoCreate(
            disciplina_id=2,
            tipo="Ajuste",
            origem="Sistema",
            estado="pendente",
            conteudo_id=10,
            autor_id=5,
            payload="dado_invalido",
            justificativa_moderacao="Corrigindo erro de digitação"
        )


def test_salvar_contribuicao_no_banco(session: Session):
    contribuicao_in = ContribuicaoCreate(
        disciplina_id=2,
        tipo="Ajuste",
        origem="Sistema",
        estado="pendente",
        conteudo_id=10,
        autor_id=5,
        payload="publicado",
        justificativa_moderacao="Corrigindo erro"
    )

    contribuicao_db = Contribuicao.model_validate(contribuicao_in)
    session.add(contribuicao_db)
    session.commit()
    session.refresh(contribuicao_db)

    assert contribuicao_db.id is not None