import importlib.util
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from backend.app.domain import (
    ConteudoAcademico,
    Contribuicao,
    Curso,
    CursoDisciplina,
    Disciplina,
    TipoConteudo,
    Usuario,
)


ARQUIVO_MIGRACAO = (
    Path(__file__).resolve().parents[2]
    / "alembic"
    / "versions"
    / "0005_unificar_disciplinas_repetidas.py"
)


def carregar_migracao():
    spec = importlib.util.spec_from_file_location("migracao_0005", ARQUIVO_MIGRACAO)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def criar_banco():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def test_unifica_copias_da_mesma_disciplina_e_preserva_referencias() -> None:
    migracao = carregar_migracao()
    engine = criar_banco()

    with Session(engine) as session:
        cursos = [
            Curso(nome="ENGENHARIA DE SOFTWARE", sigla="FCTE"),
            Curso(nome="ENGENHARIA DE ENERGIA", sigla="FCTE"),
            Curso(nome="ENGENHARIA AEROESPACIAL", sigla="FCTE"),
        ]
        autor = Usuario(nome="Autor", email="autor@unb.br", senha_hash="hash")
        # Uma cópia de FGA0003 por curso, como ficavam os bancos antes da 0004.
        copias = [Disciplina(codigo="FGA0003", nome="COMPILADORES 1") for _ in cursos]
        calculo = Disciplina(codigo="MAT0025", nome="CÁLCULO 1")
        session.add_all([*cursos, autor, *copias, calculo])
        session.flush()
        for curso, copia in zip(cursos, copias):
            session.add(CursoDisciplina(curso_id=curso.id, disciplina_id=copia.id))
        # O curso 1 também já estava ligado à segunda cópia: não pode duplicar.
        session.add(CursoDisciplina(curso_id=cursos[0].id, disciplina_id=copias[1].id))
        session.add(CursoDisciplina(curso_id=cursos[0].id, disciplina_id=calculo.id))
        session.add(
            ConteudoAcademico(
                disciplina_id=copias[1].id,
                tipo=TipoConteudo.RESUMO,
                titulo="Resumo",
                corpo_ou_url="texto",
                autor_id=autor.id,
            )
        )
        session.add(
            Contribuicao(
                disciplina_id=copias[2].id,
                autor_id=autor.id,
                tipo=TipoConteudo.DICA,
                titulo="Dica",
                corpo_ou_url="texto",
            )
        )
        session.commit()
        mantida_id = copias[0].id
        calculo_id = calculo.id
        ids_cursos = sorted(curso.id for curso in cursos)

    with engine.begin() as conexao:
        assert migracao.unificar_disciplinas_repetidas(conexao) == 2

    with Session(engine) as session:
        restantes = session.exec(
            select(Disciplina).where(Disciplina.codigo == "FGA0003")
        ).all()
        assert [disciplina.id for disciplina in restantes] == [mantida_id]

        cursos_da_mantida = session.exec(
            select(CursoDisciplina.curso_id).where(
                CursoDisciplina.disciplina_id == mantida_id
            )
        ).all()
        assert sorted(cursos_da_mantida) == ids_cursos

        conteudo = session.exec(select(ConteudoAcademico)).one()
        contribuicao_salva = session.exec(select(Contribuicao)).one()
        assert conteudo.disciplina_id == mantida_id
        assert contribuicao_salva.disciplina_id == mantida_id

        # Disciplina sem cópias não muda.
        assert session.get(Disciplina, calculo_id) is not None

    # Rodar de novo não altera nada.
    with engine.begin() as conexao:
        assert migracao.unificar_disciplinas_repetidas(conexao) == 0


def test_consolida_vinculos_gravados_na_tabela_com_nome_errado() -> None:
    migracao = carregar_migracao()
    engine = criar_banco()

    with Session(engine) as session:
        software = Curso(nome="ENGENHARIA DE SOFTWARE", sigla="FCTE")
        energia = Curso(nome="ENGENHARIA DE ENERGIA", sigla="FCTE")
        calculo = Disciplina(codigo="MAT0025", nome="CÁLCULO 1")
        session.add_all([software, energia, calculo])
        session.flush()
        session.add(CursoDisciplina(curso_id=software.id, disciplina_id=calculo.id))
        session.commit()
        ids = (software.id, energia.id, calculo.id)

    # Tabela que o create_all() criava antes do __tablename__ no model.
    with engine.begin() as conexao:
        conexao.execute(
            text("CREATE TABLE cursodisciplina (curso_id INTEGER, disciplina_id INTEGER)")
        )
        conexao.execute(
            text("INSERT INTO cursodisciplina VALUES (:s, :d), (:e, :d)"),
            {"s": ids[0], "e": ids[1], "d": ids[2]},
        )

    with engine.begin() as conexao:
        # Software já estava na tabela certa; só Energia é copiado.
        assert migracao.consolidar_tabela_de_vinculos(conexao) == 1

    assert not inspect(engine).has_table("cursodisciplina")
    with Session(engine) as session:
        vinculos = session.exec(select(CursoDisciplina.curso_id)).all()
        assert sorted(vinculos) == [ids[0], ids[1]]

    # Sem a tabela errada, não faz nada.
    with engine.begin() as conexao:
        assert migracao.consolidar_tabela_de_vinculos(conexao) == 0


def test_mantem_a_copia_ativa_quando_a_primeira_esta_inativa() -> None:
    migracao = carregar_migracao()
    engine = criar_banco()

    with Session(engine) as session:
        curso = Curso(nome="ENGENHARIA DE SOFTWARE", sigla="FCTE")
        inativa = Disciplina(codigo="FGA0030", nome="ESTRUTURAS DE DADOS 2", ativo=False)
        ativa = Disciplina(codigo="FGA0030", nome="ESTRUTURAS DE DADOS 2")
        session.add_all([curso, inativa, ativa])
        session.flush()
        session.add(CursoDisciplina(curso_id=curso.id, disciplina_id=inativa.id))
        session.commit()
        ativa_id = ativa.id

    with engine.begin() as conexao:
        assert migracao.unificar_disciplinas_repetidas(conexao) == 1

    with Session(engine) as session:
        restante = session.exec(select(Disciplina)).one()
        assert restante.id == ativa_id
        assert restante.ativo is True
        assert session.exec(select(CursoDisciplina.disciplina_id)).all() == [ativa_id]
