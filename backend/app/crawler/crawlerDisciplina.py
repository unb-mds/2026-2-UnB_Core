from __future__ import annotations

from dataclasses import dataclass
import re
from collections.abc import Callable
from typing import Final
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from sqlmodel import Session, select

from backend.app.domain import Curso, Disciplina


URL_TURMAS_GRADUACAO: Final = (
    "https://sigaa.unb.br/sigaa/public/home.jsf"
)
UNIDADE_CIC: Final = "508"
_CODIGO_DISCIPLINA = re.compile(r"([A-Z]{2,}\d+)\s*-\s*(.+)")


@dataclass(frozen=True)
class DisciplinaColetada:
    codigo: str
    nome: str
    periodo: str | None


def extrair_disciplinas_html(html: str) -> list[DisciplinaColetada]:
    soup = BeautifulSoup(html, "html.parser")
    tabela = soup.find("table", class_="listagem")
    if tabela is None:
        return []

    disciplinas: list[DisciplinaColetada] = []
    vistos: set[str] = set()
    for linha in tabela.find_all("tr"):
        classes = linha.get("class", [])
        if "agrupador" in classes:
            titulo = linha.find("span", class_="tituloDisciplina")
            if titulo is None:
                continue
            match = _CODIGO_DISCIPLINA.search(titulo.get_text(" ", strip=True))
            if match is None or match.group(1) in vistos:
                continue
            disciplinas.append(
                DisciplinaColetada(
                    codigo=match.group(1),
                    nome=match.group(2).strip(),
                    periodo=None,
                )
            )
            vistos.add(match.group(1))
            continue

        if not disciplinas or disciplinas[-1].periodo is not None:
            continue
        textos = [celula.get_text(" ", strip=True) for celula in linha.find_all("td")]
        periodo = next(
            (texto for texto in textos if re.fullmatch(r"\d{4}\.\d", texto)),
            None,
        )
        if periodo is not None:
            anterior = disciplinas[-1]
            disciplinas[-1] = DisciplinaColetada(
                codigo=anterior.codigo,
                nome=anterior.nome,
                periodo=periodo,
            )
    return disciplinas


def _extrair_formulario(html: str, unidade: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    formulario = soup.find("form", id="formTurma") or soup.find("form")
    if formulario is None:
        raise RuntimeError("Formulário de turmas não encontrado no SIGAA.")

    dados: dict[str, str] = {}
    for campo in formulario.find_all(["input", "select"]):
        nome = campo.get("name")
        if not nome:
            continue
        if campo.name == "input":
            tipo = campo.get("type", "").lower()
            valor = campo.get("value", "")
            if tipo == "submit" and valor != "Buscar":
                continue
            dados[nome] = valor
            continue
        selecionada = campo.find("option", selected=True)
        opcao = selecionada or campo.find("option")
        if opcao is not None:
            dados[nome] = opcao.get("value", "")

    dados["formTurma:inputNivel"] = "G"
    dados["formTurma:inputDepto"] = unidade
    return dados


async def coletar_disciplinas(
    url: str = URL_TURMAS_GRADUACAO,
    *,
    unidade: str | None = None,
    headless: bool = True,
    ao_concluir_unidade: Callable[
        [str, list[DisciplinaColetada]], None
    ] | None = None,
) -> list[DisciplinaColetada]:
    del headless
    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as cliente:
        resposta_inicial = await cliente.get(url)
        resposta_inicial.raise_for_status()
        soup = BeautifulSoup(resposta_inicial.text, "html.parser")
        link_turmas = soup.find("a", href=re.compile(r"turmas/listar\.jsf"))
        if link_turmas is None or not link_turmas.get("href"):
            raise RuntimeError("Link de turmas não encontrado no SIGAA.")
        url_turmas = urljoin(str(resposta_inicial.url), link_turmas["href"])

        resposta_formulario = await cliente.get(url_turmas)
        resposta_formulario.raise_for_status()
        soup_formulario = BeautifulSoup(
            resposta_formulario.text,
            "html.parser",
        )
        select_unidades = soup_formulario.find(
            "select",
            id="formTurma:inputDepto",
        )
        if unidade:
            unidades = [unidade]
        elif select_unidades is None:
            raise RuntimeError("Lista de unidades não encontrada no SIGAA.")
        else:
            unidades = [
                str(opcao.get("value"))
                for opcao in select_unidades.find_all("option")
                if opcao.get("value") not in (None, "0")
            ]

        disciplinas: list[DisciplinaColetada] = []
        vistos: set[str] = set()
        for unidade_atual in unidades:
            resposta_formulario = await cliente.get(url_turmas)
            resposta_formulario.raise_for_status()
            dados_formulario = _extrair_formulario(
                resposta_formulario.text,
                unidade_atual,
            )
            resposta = await cliente.post(
                url_turmas,
                data=dados_formulario,
            )
            resposta.raise_for_status()
            html_resultado = resposta.text
            disciplinas_novas: list[DisciplinaColetada] = []
            for disciplina in extrair_disciplinas_html(html_resultado):
                if disciplina.codigo not in vistos:
                    disciplinas.append(disciplina)
                    disciplinas_novas.append(disciplina)
                    vistos.add(disciplina.codigo)
            if ao_concluir_unidade is not None:
                ao_concluir_unidade(unidade_atual, disciplinas_novas)
        return disciplinas


def _sigla_por_codigo(codigo: str) -> str:
    match = re.match(r"^([A-Z]+)", codigo)
    return match.group(1) if match else ""


def salvar_disciplinas(
    session: Session,
    disciplinas: list[DisciplinaColetada],
) -> int:
    cursos = {
        curso.sigla.upper(): curso
        for curso in session.exec(select(Curso)).all()
    }
    quantidade = 0
    for disciplina in disciplinas:
        curso = cursos.get(_sigla_por_codigo(disciplina.codigo))
        if curso is None:
            continue
        if curso.id is None:
            continue
        existente = session.exec(
            select(Disciplina).where(
                Disciplina.curso_id == curso.id,
                Disciplina.codigo == disciplina.codigo,
            )
        ).first()
        if existente is None:
            session.add(
                Disciplina(
                    curso_id=curso.id,
                    codigo=disciplina.codigo,
                    nome=disciplina.nome,
                    periodo=disciplina.periodo,
                )
            )
        quantidade += 1
    session.commit()
    return quantidade


async def coletar_e_salvar_disciplinas(
    session: Session,
    url: str = URL_TURMAS_GRADUACAO,
) -> int:
    quantidade = 0

    def salvar_unidade(
        _: str,
        disciplinas: list[DisciplinaColetada],
    ) -> None:
        nonlocal quantidade
        quantidade += salvar_disciplinas(session, disciplinas)

    await coletar_disciplinas(
        url,
        ao_concluir_unidade=salvar_unidade,
    )
    return quantidade
