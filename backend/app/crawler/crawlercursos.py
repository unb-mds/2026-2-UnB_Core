from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import httpx
from bs4 import BeautifulSoup
from sqlmodel import Session, select

from backend.app.domain import Curso, GrauCurso


URL_CURSOS_GRADUACAO: Final = (
    "https://sigaa.unb.br/sigaa/public/curso/lista.jsf"
    "?nivel=G&aba=p-graduacao"
)


@dataclass(frozen=True)
class CursoColetado:
    nome: str
    sigla: str
    grau: GrauCurso


def _normalizar(texto: str) -> str:
    return " ".join(texto.split()).strip()


def _extrair_sigla(departamento: str) -> str:
    return departamento.split(" - ", maxsplit=1)[0].strip()


def _extrair_grau(grau: str) -> GrauCurso | None:
    return {
        "BACHARELADO": GrauCurso.BACHARELADO,
        "LICENCIATURA": GrauCurso.LICENCIATURA,
    }.get(grau.upper())


def extrair_cursos_html(html: str) -> list[CursoColetado]:
    soup = BeautifulSoup(html, "html.parser")
    tabela = soup.find("table", class_="listagem") or soup.find("table")
    if tabela is None:
        return []

    departamento = ""
    cursos: list[CursoColetado] = []
    vistos: set[tuple[str, str, GrauCurso]] = set()
    for linha in tabela.find_all("tr"):
        row = [
            (
                _normalizar(celula.get_text(" ", strip=True)),
                int(celula.get("colspan", "1"))
                if str(celula.get("colspan", "1")).isdigit()
                else 1,
            )
            for celula in linha.find_all(["th", "td"], recursive=False)
        ]
        if len(row) == 1 and row[0][1] >= 7:
            departamento = _extrair_sigla(row[0][0])
            continue
        if len(row) < 7 or not departamento:
            continue
        nome = row[0][0]
        if not nome or nome.lower() == "nome":
            continue
        grau = _extrair_grau(row[5][0])
        if grau is None:
            continue
        curso = CursoColetado(
            nome=nome,
            sigla=departamento,
            grau=grau,
        )
        if (curso.nome, curso.sigla, curso.grau) not in vistos:
            cursos.append(curso)
            vistos.add((curso.nome, curso.sigla, curso.grau))
    return cursos


async def coletar_cursos(
    url: str = URL_CURSOS_GRADUACAO,
    *,
    headless: bool = True,
) -> list[CursoColetado]:
    del headless
    async with httpx.AsyncClient(timeout=60.0) as cliente:
        resposta = await cliente.get(url)
        resposta.raise_for_status()
        return extrair_cursos_html(resposta.text)


def salvar_cursos(session: Session, cursos: list[CursoColetado]) -> int:
    quantidade_alterada = 0
    for curso in cursos:
        existente = session.exec(
            select(Curso).where(
                Curso.nome == curso.nome,
                Curso.sigla == curso.sigla,
                Curso.grau == curso.grau,
            )
        ).first()
        if existente is None:
            session.add(
                Curso(
                    nome=curso.nome,
                    sigla=curso.sigla,
                    grau=curso.grau,
                )
            )
        quantidade_alterada += 1
    session.commit()
    return quantidade_alterada


async def coletar_e_salvar_cursos(
    session: Session,
    url: str = URL_CURSOS_GRADUACAO,
) -> int:
    cursos = await coletar_cursos(url)
    return salvar_cursos(session, cursos)