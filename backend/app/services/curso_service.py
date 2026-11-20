import unicodedata

from sqlmodel import Session, select

from backend.app.domain import Curso, CursoDisciplina, Disciplina


def listar_cursos(session: Session) -> list[Curso]:
    return list(
        session.exec(
            select(Curso).order_by(Curso.nome, Curso.grau)
        ).all()
    )


listar_cursos_ativos = listar_cursos


def listar_disciplinas_ativas(
    session: Session,
    curso_id: int,
) -> list[Disciplina]:
    return list(
        session.exec(
            select(Disciplina)
            .join(
                CursoDisciplina,
                CursoDisciplina.disciplina_id == Disciplina.id,
            )
            .where(
                CursoDisciplina.curso_id == curso_id,
                Disciplina.ativo,
            )
            .order_by(Disciplina.nome)
        ).all()
    )


def _normalizar_busca(texto: str) -> str:
    # Remove acentos e diferenças de maiúsculas para que "calculo" encontre
    # "CÁLCULO 1". Feito em Python para funcionar igual no PostgreSQL e no
    # SQLite dos testes, sem depender da extensão unaccent.
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(
        caractere for caractere in decomposto
        if not unicodedata.combining(caractere)
    )
    return " ".join(sem_acento.casefold().split())


def buscar_disciplinas(
    session: Session,
    busca: str,
    limite: int = 20,
) -> list[Disciplina]:
    """Busca disciplinas ativas pelo código ou nome, sem exigir um curso."""
    termos = _normalizar_busca(busca).split()
    if not termos:
        return []
    consulta = " ".join(termos)

    encontradas: list[tuple[int, str, Disciplina]] = []
    for disciplina in session.exec(
        select(Disciplina).where(Disciplina.ativo)
    ).all():
        codigo = _normalizar_busca(disciplina.codigo)
        nome = _normalizar_busca(disciplina.nome)
        # Cada termo precisa ser o começo de uma palavra do código ou do nome:
        # "calc 2" encontra "CÁLCULO 2", mas não "CÁLCULO 1" (código MAT0025).
        palavras = f"{codigo} {nome}".split()
        if not all(
            any(palavra.startswith(termo) for palavra in palavras)
            for termo in termos
        ):
            continue
        if codigo.startswith(consulta):
            relevancia = 0
        elif nome.startswith(consulta):
            relevancia = 1
        else:
            relevancia = 2
        encontradas.append((relevancia, nome, disciplina))

    encontradas.sort(key=lambda item: (item[0], item[1], item[2].codigo))
    return [disciplina for _, _, disciplina in encontradas[:limite]]
