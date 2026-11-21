"""Coleta a estrutura curricular ativa dos cursos de uma unidade no SIGAA.

O SIGAA lista as turmas por unidade, sem dizer a qual curso cada disciplina
pertence. Por isso, os 6 cursos do Gama (sigla "FCTE") recebiam as mesmas
disciplinas. A estrutura curricular pública de cada curso resolve isso: ela
lista os componentes (obrigatórios e optativos) daquele curso específico.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Final
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from sqlmodel import Session, select

from backend.app.crawler.crawlerDisciplina import DisciplinaColetada
from backend.app.crawler.crawlercursos import URL_CURSOS_GRADUACAO
from backend.app.domain import (
    ConteudoAcademico,
    Contribuicao,
    Curso,
    CursoDisciplina,
    Disciplina,
)


URL_CURRICULO: Final = "https://sigaa.unb.br/sigaa/public/curso/curriculo.jsf"
_PORTAL_ID = re.compile(r"portal\.jsf\?id=(\d+)")
_ACAO_ESTRUTURA = re.compile(r"\{'(formCurriculosCurso:[^']+)':'[^']+','id':'(\d+)'\}")
_COMPONENTE = re.compile(r"^([A-Z]{2,}\d+)\s*-\s*(.+?)\s*-\s*\d+h$")
_ESTRUTURA_ATIVA = re.compile(r"\bAtiva\b")
logger = logging.getLogger(__name__)


def _normalizar(texto: str) -> str:
    return " ".join(texto.split()).strip()


def extrair_portais_cursos_html(
    html: str,
) -> dict[tuple[str, str], str]:
    """Retorna {(sigla da unidade, nome do curso): id do portal no SIGAA}."""
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
        if not unidade_atual or len(celulas) < 7:
            continue
        link = linha.find("a", href=_PORTAL_ID)
        nome = _normalizar(celulas[0].get_text(" ", strip=True))
        if link is None or not nome:
            continue
        portais.setdefault(
            (unidade_atual.upper(), nome),
            _PORTAL_ID.search(link["href"]).group(1),
        )
    return portais


def extrair_estruturas_ativas_html(html: str) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """Retorna os campos e a primeira estrutura ativa encontrada."""
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
            break
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
) -> dict[tuple[str, str], list[DisciplinaColetada]]:
    """Retorna os componentes ativos de todos os cursos da UnB."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as cliente:
        resposta = await cliente.get(url_cursos)
        resposta.raise_for_status()
        portais = extrair_portais_cursos_html(resposta.text)
        if not portais:
            raise RuntimeError("Nenhum curso foi encontrado ao coletar curriculos.")

        semaforo = asyncio.Semaphore(8)

        async def coletar_curso(
            chave_curso: tuple[str, str],
            id_portal: str,
        ) -> tuple[tuple[str, str], list[DisciplinaColetada]] | None:
            async with semaforo:
                try:
                    resposta_curso = await cliente.get(
                        URL_CURRICULO,
                        params={"lc": "pt_BR", "id": id_portal},
                    )
                    resposta_curso.raise_for_status()
                    campos, acoes = extrair_estruturas_ativas_html(
                        resposta_curso.text
                    )
                    url_formulario = urljoin(
                        str(resposta_curso.url),
                        URL_CURRICULO,
                    )

                    componentes: dict[
                        str,
                        DisciplinaColetada,
                    ] = {}
                    for chave, id_estrutura in acoes:
                        detalhe = await cliente.post(
                            url_formulario,
                            data={
                                **campos,
                                chave: chave,
                                "id": id_estrutura,
                            },
                        )
                        detalhe.raise_for_status()
                        for componente in extrair_componentes_curriculares_html(
                            detalhe.text
                        ):
                            componentes.setdefault(
                                componente.codigo,
                                componente,
                            )
                    if not componentes:
                        return None
                    return chave_curso, list(componentes.values())
                except (httpx.HTTPError, RuntimeError):
                    sigla, nome = chave_curso
                    logger.warning(
                        "Falha ao coletar curriculo de %s - %s.",
                        sigla,
                        nome,
                        exc_info=True,
                    )
                    return None

        resultados = await asyncio.gather(*(
            coletar_curso(chave_curso, id_portal)
            for chave_curso, id_portal in portais.items()
        ))

        curriculos: dict[tuple[str, str], list[DisciplinaColetada]] = {}
        for resultado in resultados:
            if resultado is None:
                continue
            chave_curso, componentes = resultado
            curriculos[chave_curso] = componentes
        if not curriculos:
            raise RuntimeError(
                "Nenhuma estrutura curricular ativa foi encontrada no SIGAA."
            )
        return curriculos


def sincronizar_disciplinas_por_curriculo(
    session: Session,
    curriculos: dict[tuple[str, str], list[DisciplinaColetada]],
) -> int:
    """Deixa cada curso só com as disciplinas da sua estrutura curricular.

    Cursos sem estrutura coletada ficam como estão. Disciplinas fora da
    estrutura só são removidas se nenhum conteúdo ou contribuição as usa.
    """
    quantidade = 0
    cursos = session.exec(select(Curso)).all()
    for curso in cursos:
        componentes = curriculos.get((curso.sigla.upper(), curso.nome))
        if not componentes or curso.id is None:
            continue
        codigos = {componente.codigo for componente in componentes}
        existentes = {
            disciplina.codigo: disciplina
            for disciplina in session.exec(
                select(Disciplina)
                .join(
                    CursoDisciplina,
                    CursoDisciplina.disciplina_id == Disciplina.id,
                )
                .where(CursoDisciplina.curso_id == curso.id)
            ).all()
        }

        for componente in componentes:
            if componente.codigo not in existentes:
                disciplina = session.exec(
                    select(Disciplina).where(
                        Disciplina.codigo == componente.codigo
                    )
                ).first()
                if disciplina is None:
                    disciplina = Disciplina(
                        codigo=componente.codigo,
                        nome=componente.nome,
                        periodo=componente.periodo,
                    )
                    session.add(disciplina)
                    session.flush()
                if disciplina.id is not None:
                    session.add(
                        CursoDisciplina(
                            curso_id=curso.id,
                            disciplina_id=disciplina.id,
                        )
                    )
                existentes[componente.codigo] = disciplina
            else:
                disciplina = existentes[componente.codigo]
                if disciplina.id is not None:
                    session.merge(
                        CursoDisciplina(
                            curso_id=curso.id,
                            disciplina_id=disciplina.id,
                        )
                    )
            quantidade += 1

        for codigo, disciplina in existentes.items():
            if codigo in codigos or _disciplina_em_uso(session, disciplina.id):
                continue
            vinculo = session.exec(
                select(CursoDisciplina).where(
                    CursoDisciplina.curso_id == curso.id,
                    CursoDisciplina.disciplina_id == disciplina.id,
                )
            ).first()
            if vinculo is not None:
                session.delete(vinculo)
                session.flush()
                outro_vinculo = session.exec(
                    select(CursoDisciplina).where(
                        CursoDisciplina.disciplina_id == disciplina.id
                    )
                ).first()
                if outro_vinculo is None:
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
    if not curriculos:
        raise RuntimeError(
            "Nenhuma estrutura curricular ativa foi encontrada no SIGAA."
        )
    return sincronizar_disciplinas_por_curriculo(session, curriculos)
