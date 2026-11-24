import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from backend.app.domain import (
    ConteudoAcademico,
    Contribuicao,
    Disciplina,
    EstadoConteudo,
    EstadoContribuicao,
    Usuario,
)
from backend.app.scripts.importar_conteudos import (
    ARQUIVO_PADRAO,
    carregar_arquivo,
    importar,
    validar_dados,
)


def criar_sessao() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    session.add_all(
        [
            Disciplina(codigo="FGA0003", nome="COMPILADORES 1"),
            Disciplina(codigo="MAT0025", nome="CÁLCULO 1"),
        ]
    )
    session.commit()
    return session


def dados_de_exemplo() -> dict:
    return {
        "autor": {"nome": "Equipe (demonstração)", "email": "Demo@Exemplo.local"},
        "origem_padrao": "Conteúdo de demonstração.",
        "conteudos": [
            {"disciplina": "FGA0003", "tipo": "resumo", "titulo": "Fases", "corpo": "Texto"},
            {
                "disciplina": "MAT0025",
                "tipo": "link",
                "titulo": "Material",
                "corpo": "https://exemplo.org",
                "origem": "Link indicado.",
            },
            {
                "disciplina": "MAT0025",
                "tipo": "dica",
                "titulo": "Para moderar",
                "corpo": "Texto",
                "estado": "pendente",
            },
            {"disciplina": "XXX9999", "tipo": "dica", "titulo": "Sem disciplina", "corpo": "Texto"},
        ],
    }


def test_importa_publicados_e_pendentes_pelo_codigo_da_disciplina() -> None:
    session = criar_sessao()

    resultado = importar(session, dados_de_exemplo())
    session.commit()

    assert resultado.publicados == 2
    assert resultado.pendentes == 1
    assert resultado.disciplinas_nao_encontradas == ["XXX9999"]

    conteudos = session.exec(select(ConteudoAcademico)).all()
    assert {conteudo.titulo for conteudo in conteudos} == {"Fases", "Material"}
    assert all(conteudo.estado == EstadoConteudo.PUBLICADO for conteudo in conteudos)
    origem = {conteudo.titulo: conteudo.origem for conteudo in conteudos}
    assert origem == {"Fases": "Conteúdo de demonstração.", "Material": "Link indicado."}

    pendente = session.exec(select(Contribuicao)).one()
    assert pendente.titulo == "Para moderar"
    assert pendente.estado == EstadoContribuicao.PENDENTE


def test_autor_e_uma_conta_desativada() -> None:
    session = criar_sessao()

    importar(session, dados_de_exemplo())
    session.commit()

    autor = session.exec(select(Usuario)).one()
    assert autor.email == "demo@exemplo.local"
    assert autor.ativo is False


def test_rodar_de_novo_nao_duplica() -> None:
    session = criar_sessao()
    importar(session, dados_de_exemplo())
    session.commit()

    resultado = importar(session, dados_de_exemplo())
    session.commit()

    assert (resultado.publicados, resultado.pendentes, resultado.ja_existentes) == (0, 0, 3)
    assert len(session.exec(select(ConteudoAcademico)).all()) == 2
    assert len(session.exec(select(Contribuicao)).all()) == 1
    assert len(session.exec(select(Usuario)).all()) == 1


@pytest.mark.parametrize(
    ("alteracao", "mensagem"),
    [
        ({"tipo": "poema"}, "tipo"),
        ({"titulo": ""}, "titulo"),
        ({"estado": "aprovado"}, "estado"),
        ({"titulo": "x" * 201}, "200"),
    ],
)
def test_validacao_recusa_itens_invalidos(alteracao, mensagem) -> None:
    dados = dados_de_exemplo()
    dados["conteudos"][0].update(alteracao)

    with pytest.raises(ValueError, match=mensagem):
        validar_dados(dados)


def test_arquivo_de_demonstracao_e_valido() -> None:
    dados = carregar_arquivo(ARQUIVO_PADRAO)
    conteudos = dados["conteudos"]

    assert len(conteudos) >= 30
    # Sem provas: o tipo depende de decisão da equipe e não deve ser inventado.
    assert all(item["tipo"] != "prova" for item in conteudos)
    # Todo conteúdo fica identificado como demonstração.
    assert "demonstração" in dados["autor"]["nome"]
    assert "demonstração" in dados["origem_padrao"]
    assert all("demonstração" in item["origem"] for item in conteudos if "origem" in item)
