import asyncio
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.pool import StaticPool

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

import backend.app.crawler.crawlerCurriculo as crawler_curriculo
from backend.app.crawler.crawlerCurriculo import (
    coletar_e_sincronizar_curriculos,
    extrair_componentes_curriculares_html,
    extrair_estruturas_ativas_html,
    extrair_portais_cursos_html,
    sincronizar_disciplinas_por_curriculo,
)
from backend.app.crawler.crawlerDisciplina import DisciplinaColetada
from backend.app.domain import (
    ConteudoAcademico,
    Curso,
    CursoDisciplina,
    Disciplina,
    GrauCurso,
    TipoConteudo,
    Usuario,
)


def _linha_curso(
    nome: str,
    id_portal: str,
    grau: str = "Bacharelado",
) -> str:
    return f"""
    <tr><td>{nome}</td><td>{grau}</td><td>DIURNO</td><td>BRASÍLIA</td>
      <td>Presencial</td><td>{grau}</td><td>COORDENAÇÃO</td>
      <td><a href="portal.jsf?id={id_portal}&lc=pt_BR&nivel=G">ver</a></td></tr>
    """


def test_extrair_portais_cursos_html_retorna_cursos_de_todas_as_unidades() -> None:
    html = f"""
    <table class="listagem">
      <tr><td colspan="7">CIC - DEPARTAMENTO DE CIÊNCIA DA COMPUTAÇÃO</td></tr>
      {_linha_curso("CIÊNCIA DA COMPUTAÇÃO", "100")}
      <tr><td colspan="7">FCTE - CAMPUS UNB GAMA: FACULDADE DE CIÊNCIAS</td></tr>
      {_linha_curso("ENGENHARIA DE SOFTWARE", "200")}
      {_linha_curso("ENGENHARIA AEROESPACIAL", "201")}
      <tr><td colspan="7">MAT - DEPARTAMENTO DE MATEMÁTICA</td></tr>
      {_linha_curso("MATEMÁTICA", "300", "Licenciatura")}
      {_linha_curso("MATEMÁTICA", "302", "Licenciatura")}
      {_linha_curso("MATEMÁTICA", "301", "Bacharelado")}
      <tr><td colspan="7">FCTE - CAMPUS UNB GAMA</td></tr>
      {_linha_curso("ENGENHARIA MECATRÔNICA", "400", "Engenheiro Mecatrônico")}
    </table>
    """

    assert extrair_portais_cursos_html(html) == {
        ("CIC", "CIÊNCIA DA COMPUTAÇÃO", "BACHARELADO"): ["100"],
        ("FCTE", "ENGENHARIA DE SOFTWARE", "BACHARELADO"): ["200"],
        ("FCTE", "ENGENHARIA AEROESPACIAL", "BACHARELADO"): ["201"],
        ("MAT", "MATEMÁTICA", "LICENCIATURA"): ["300", "302"],
        ("MAT", "MATEMÁTICA", "BACHARELADO"): ["301"],
        ("FCTE", "ENGENHARIA MECATRÔNICA", "BACHARELADO"): ["400"],
    }


def test_extrair_estruturas_ativas_html_ignora_estruturas_inativas() -> None:
    def acao(chave: str, id_estrutura: str) -> str:
        return (
            '<a href="#" title="Visualizar Estrutura Curricular" '
            "onclick=\"jsfcljs(document.getElementById('formCurriculosCurso'),"
            f"{{'formCurriculosCurso:{chave}':'formCurriculosCurso:{chave}',"
            f"'id':'{id_estrutura}'}},'');\">ver</a>"
        )

    html = f"""
    <form id="formCurriculosCurso">
      <input type="hidden" name="formCurriculosCurso" value="formCurriculosCurso" />
      <input type="hidden" name="javax.faces.ViewState" value="j_id1" />
      <table>
        <tr><td>6360/2, Criado em 2024</td><td>Ativa</td><td>{acao("a1", "11")}</td></tr>
        <tr><td>6360/1, Criado em 2017</td><td>Inativa</td><td>{acao("a2", "22")}</td></tr>
      </table>
    </form>
    """

    campos, acoes = extrair_estruturas_ativas_html(html)

    assert campos == {
        "formCurriculosCurso": "formCurriculosCurso",
        "javax.faces.ViewState": "j_id1",
    }
    assert acoes == [("formCurriculosCurso:a1", "11")]


def test_extrair_estruturas_ativas_html_pega_somente_a_primeira_ativa() -> None:
    def acao(chave: str, id_estrutura: str) -> str:
        return (
            '<a href="#" title="Visualizar Estrutura Curricular" '
            "onclick=\"jsfcljs(document.getElementById('formCurriculosCurso'),"
            f"{{'formCurriculosCurso:{chave}':'formCurriculosCurso:{chave}',"
            f"'id':'{id_estrutura}'}},'');\">ver</a>"
        )

    html = f"""
    <form id="formCurriculosCurso">
      <input type="hidden" name="formCurriculosCurso" value="formCurriculosCurso" />
      <input type="hidden" name="javax.faces.ViewState" value="j_id1" />
      <table>
        <tr><td>8150/1, Criado em 2018</td><td>Ativa</td><td>{acao("a1", "11")}</td></tr>
        <tr><td>8150/-2, Criado em 2017</td><td>Ativa</td><td>{acao("a2", "22")}</td></tr>
        <tr><td>8150/-3, Criado em 2015</td><td>Inativa</td><td>{acao("a3", "33")}</td></tr>
      </table>
    </form>
    """

    _, acoes = extrair_estruturas_ativas_html(html)

    assert acoes == [("formCurriculosCurso:a1", "11")]


def test_extrair_componentes_curriculares_html_le_codigo_e_nome() -> None:
    html = """
    <table class="subFormulario">
      <tr><td>FGA0003 - COMPILADORES 1 - 60h</td><td>Obrigatória</td></tr>
      <tr><td>MAT0025 - CÁLCULO 1 - 90h</td><td>Obrigatória</td></tr>
      <tr><td>FGA0003 - COMPILADORES 1 - 60h</td><td>Optativa</td></tr>
      <tr><td><b>Carga Horária Total:</b> 360h</td></tr>
    </table>
    """

    assert extrair_componentes_curriculares_html(html) == [
        DisciplinaColetada(codigo="FGA0003", nome="COMPILADORES 1", periodo=None),
        DisciplinaColetada(codigo="MAT0025", nome="CÁLCULO 1", periodo=None),
    ]


def test_sincronizacao_rejeita_resultado_vazio(monkeypatch) -> None:
    coletar = AsyncMock(return_value={})
    monkeypatch.setattr(crawler_curriculo, "coletar_curriculos", coletar)

    with pytest.raises(
        RuntimeError,
        match="Nenhuma estrutura curricular ativa",
    ):
        asyncio.run(coletar_e_sincronizar_curriculos(MagicMock()))


def test_sincroniza_cursos_homonimos_por_grau() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        licenciatura = Curso(
            nome="MATEMÁTICA",
            sigla="MAT",
            grau=GrauCurso.LICENCIATURA,
        )
        bacharelado = Curso(
            nome="MATEMÁTICA",
            sigla="MAT",
            grau=GrauCurso.BACHARELADO,
        )
        session.add_all([licenciatura, bacharelado])
        session.commit()
        session.refresh(licenciatura)
        session.refresh(bacharelado)

        curriculos = {
            ("MAT", "MATEMÁTICA", "LICENCIATURA"): [
                DisciplinaColetada("MAT0130", "MATEMÁTICA ELEMENTAR", None),
            ],
            ("MAT", "MATEMÁTICA", "BACHARELADO"): [
                DisciplinaColetada("MAT0025", "CÁLCULO 1", None),
            ],
        }

        sincronizar_disciplinas_por_curriculo(session, curriculos)

        def codigos(curso: Curso) -> set[str]:
            return {
                disciplina.codigo
                for disciplina in session.exec(
                    select(Disciplina)
                    .join(
                        CursoDisciplina,
                        CursoDisciplina.disciplina_id == Disciplina.id,
                    )
                    .where(CursoDisciplina.curso_id == curso.id)
                ).all()
            }

        assert codigos(licenciatura) == {"MAT0130"}
        assert codigos(bacharelado) == {"MAT0025"}


def test_sincronizar_disciplinas_por_curriculo_separa_os_cursos_do_gama() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        software = Curso(nome="ENGENHARIA DE SOFTWARE", sigla="FCTE")
        aeroespacial = Curso(nome="ENGENHARIA AEROESPACIAL", sigla="FCTE")
        energia = Curso(nome="ENGENHARIA DE ENERGIA", sigla="FCTE")
        autor = Usuario(nome="Autor", email="autor@unb.br", senha_hash="hash")
        session.add_all([software, aeroespacial, energia, autor])
        session.commit()
        for curso in (software, aeroespacial, energia):
            session.refresh(curso)
            for codigo, nome in (
                ("FGA0003", "COMPILADORES 1"),
                ("FGA0109", "DINÂMICA DOS FLUIDOS"),
            ):
                disciplina = Disciplina(codigo=codigo, nome=nome)
                session.add(disciplina)
                session.flush()
                session.add(
                    CursoDisciplina(
                        curso_id=curso.id,
                        disciplina_id=disciplina.id,
                    )
                )
        session.commit()
        session.refresh(autor)

        def disciplina(curso: Curso, codigo: str) -> Disciplina:
            return session.exec(
                select(Disciplina).where(
                    CursoDisciplina.disciplina_id == Disciplina.id,
                    CursoDisciplina.curso_id == curso.id,
                    Disciplina.codigo == codigo,
                )
            ).one()

        fluidos_software = disciplina(software, "FGA0109")
        compiladores_aero = disciplina(aeroespacial, "FGA0003")
        session.add(
            ConteudoAcademico(
                disciplina_id=compiladores_aero.id,
                tipo=TipoConteudo.RESUMO,
                titulo="Resumo",
                corpo_ou_url="texto",
                autor_id=autor.id,
            )
        )
        session.commit()

        curriculos = {
            ("FCTE", "ENGENHARIA DE SOFTWARE", "BACHARELADO"): [
                DisciplinaColetada("FGA0003", "COMPILADORES 1", None),
                DisciplinaColetada("MAT0025", "CÁLCULO 1", None),
            ],
            ("FCTE", "ENGENHARIA AEROESPACIAL", "BACHARELADO"): [
                DisciplinaColetada("FGA0109", "DINÂMICA DOS FLUIDOS", None),
            ],
        }

        assert sincronizar_disciplinas_por_curriculo(session, curriculos) == 3
        # Rodar de novo não duplica nem remove mais nada.
        assert sincronizar_disciplinas_por_curriculo(session, curriculos) == 3

        def codigos(curso: Curso) -> set[str]:
            return {
                disciplina.codigo
                for disciplina in session.exec(
                    select(Disciplina)
                    .join(
                        CursoDisciplina,
                        CursoDisciplina.disciplina_id == Disciplina.id,
                    )
                    .where(CursoDisciplina.curso_id == curso.id)
                ).all()
            }

        assert codigos(software) == {"FGA0003", "MAT0025"}
        assert session.get(Disciplina, fluidos_software.id) is None
        # FGA0003 está fora da grade de Aeroespacial, mas tem conteúdo
        # publicado, então fica para não quebrar a referência.
        assert codigos(aeroespacial) == {"FGA0109", "FGA0003"}
        # Curso sem estrutura coletada fica como estava.
        assert codigos(energia) == {"FGA0003", "FGA0109"}
