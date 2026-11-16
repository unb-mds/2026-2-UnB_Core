"""Coleta a estrutura curricular ativa dos cursos de uma unidade no SIGAA.

O SIGAA lista as turmas por unidade, sem dizer a qual curso cada disciplina
pertence. Por isso, os 6 cursos do Gama (sigla "FCTE") recebiam as mesmas
disciplinas. A estrutura curricular pública de cada curso resolve isso: ela
lista os componentes (obrigatórios e optativos) daquele curso específico.
"""

from __future__ import annotations

import re
from typing import Final
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from sqlmodel import Session, select

from backend.app.crawler.crawlerDisciplina import DisciplinaColetada
from backend.app.crawler.crawlercursos import URL_CURSOS_GRADUACAO
from backend.app.domain import ConteudoAcademico, Contribuicao, Curso, Disciplina


SIGLA_CAMPUS_GAMA: Final = "FCTE"
URL_CURRICULO: Final = "https://sigaa.unb.br/sigaa/public/curso/curriculo.jsf"
_PORTAL_ID = re.compile(r"portal\.jsf\?id=(\d+)")
_ACAO_ESTRUTURA = re.compile(r"\{'(formCurriculosCurso:[^']+)':'[^']+','id':'(\d+)'\}")
_COMPONENTE = re.compile(r"^([A-Z]{2,}\d+)\s*-\s*(.+?)\s*-\s*\d+h$")
_ESTRUTURA_ATIVA = re.compile(r"\bAtiva\b")


def _normalizar(texto: str) -> str:
    return " ".join(texto.split()).strip()


def extrair_portais_cursos_html(
    html: str,
    sigla: str = SIGLA_CAMPUS_GAMA,
) -> dict[str, str]:
    """Retorna {nome do curso: id do portal no SIGAA} dos cursos da unidade."""
    soup = BeautifulSoup(html, "html.parser")
    tabela = soup.find("table", class_="listagem") or soup.find("table")
    if tabela is None:
        return {}

    unidade_atual = ""
    portais: dict[str, str] = {}
    for linha in tabela.find_all("tr"):
        celulas = linha.find_all(["th", "td"], recursive=False)
        if len(celulas) == 1 and str(celulas[0].get("colspan", "1")).isdigit():
            if int(celulas[0].get("colspan", "1")) >= 7:
                titulo = _normalizar(celulas[0].get_text(" ", strip=True))
                unidade_atual = titulo.split(" - ", maxsplit=1)[0].strip()
                continue
        if unidade_atual != sigla or len(celulas) < 7:
            continue
        link = linha.find("a", href=_PORTAL_ID)
        nome = _normalizar(celulas[0].get_text(" ", strip=True))
        if link is None or not nome:
            continue
        portais.setdefault(nome, _PORTAL_ID.search(link["href"]).group(1))
    return portais


def extrair_estruturas_ativas_html(html: str) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """Retorna os campos do formulário e as ações (chave, id) das estruturas ativas."""
    soup = BeautifulSoup(html, "html.parser")
    formulario = soup.find("form", id="formCurriculosCurso")
    if formulario is None:
        return {}, []

    campos = {
        campo["name"]: campo.get("value", "")
        for campo in formulario.find_all("input")
        if campo.get("name")
    }
    acoes: list[tuple[str, str]] = []
    for link in formulario.find_all("a", title="Visualizar Estrutura Curricular"):
        linha = link.find_parent("tr")
        texto = linha.get_text(" ", strip=True) if linha is not None else ""
        match = _ACAO_ESTRUTURA.search(link.get("onclick", ""))
        if match is not None and _ESTRUTURA_ATIVA.search(texto):
            acoes.append((match.group(1), match.group(2)))
    return campos, acoes


def extrair_componentes_curriculares_html(html: str) -> list[DisciplinaColetada]:
    soup = BeautifulSoup(html, "html.parser")
    componentes: list[DisciplinaColetada] = []
    vistos: set[str] = set()
    for celula in soup.find_all("td"):
        match = _COMPONENTE.match(_normalizar(celula.get_text(" ", strip=True)))
        if match is None or match.group(1) in vistos:
            continue
        componentes.append(
            DisciplinaColetada(
                codigo=match.group(1),
                nome=match.group(2).strip(),
                periodo=None,
            )
        )
        vistos.add(match.group(1))
    return componentes


async def coletar_curriculos(
    url_cursos: str = URL_CURSOS_GRADUACAO,
    *,
    sigla: str = SIGLA_CAMPUS_GAMA,
) -> dict[str, list[DisciplinaColetada]]:
    """Retorna {nome do curso: componentes das estruturas curriculares ativas}."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as cliente:
        resposta = await cliente.get(url_cursos)
        resposta.raise_for_status()
        portais = extrair_portais_cursos_html(resposta.text, sigla)

        curriculos: dict[str, list[DisciplinaColetada]] = {}
        for nome, id_portal in portais.items():
            resposta = await cliente.get(
                URL_CURRICULO,
                params={"lc": "pt_BR", "id": id_portal},
            )
            resposta.raise_for_status()
            campos, acoes = extrair_estruturas_ativas_html(resposta.text)
            url_formulario = urljoin(str(resposta.url), URL_CURRICULO)

            componentes: dict[str, DisciplinaColetada] = {}
            for chave, id_estrutura in acoes:
                detalhe = await cliente.post(
                    url_formulario,
                    data={**campos, chave: chave, "id": id_estrutura},
                )
                detalhe.raise_for_status()
                for componente in extrair_componentes_curriculares_html(detalhe.text):
                    componentes.setdefault(componente.codigo, componente)
            if componentes:
                curriculos[nome] = list(componentes.values())
        return curriculos


def sincronizar_disciplinas_por_curriculo(
    session: Session,
    curriculos: dict[str, list[DisciplinaColetada]],
    *,
    sigla: str = SIGLA_CAMPUS_GAMA,
) -> int:
    """Deixa cada curso da unidade só com as disciplinas da sua estrutura curricular.

    Cursos sem estrutura coletada ficam como estão. Disciplinas fora da
    estrutura só são removidas se nenhum conteúdo ou contribuição as usa.
    """
    quantidade = 0
    cursos = session.exec(select(Curso).where(Curso.sigla == sigla)).all()
    for curso in cursos:
        componentes = curriculos.get(curso.nome)
        if not componentes or curso.id is None:
            continue
        codigos = {componente.codigo for componente in componentes}
        existentes = {
            disciplina.codigo: disciplina
            for disciplina in session.exec(
                select(Disciplina).where(Disciplina.curso_id == curso.id)
            ).all()
        }

        for componente in componentes:
            if componente.codigo not in existentes:
                session.add(
                    Disciplina(
                        curso_id=curso.id,
                        codigo=componente.codigo,
                        nome=componente.nome,
                        periodo=componente.periodo,
                    )
                )
            quantidade += 1

        for codigo, disciplina in existentes.items():
            if codigo in codigos or _disciplina_em_uso(session, disciplina.id):
                continue
            session.delete(disciplina)
    session.commit()
    return quantidade


def _disciplina_em_uso(session: Session, disciplina_id: int | None) -> bool:
    if disciplina_id is None:
        return False
    conteudo = session.exec(
        select(ConteudoAcademico.id).where(ConteudoAcademico.disciplina_id == disciplina_id)
    ).first()
    if conteudo is not None:
        return True
    contribuicao = session.exec(
        select(Contribuicao.id).where(Contribuicao.disciplina_id == disciplina_id)
    ).first()
    return contribuicao is not None


async def coletar_e_sincronizar_curriculos(
    session: Session,
    url_cursos: str = URL_CURSOS_GRADUACAO,
) -> int:
    curriculos = await coletar_curriculos(url_cursos)
    return sincronizar_disciplinas_por_curriculo(session, curriculos)
