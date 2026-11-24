"""Importa conteúdos de um arquivo JSON para o banco.

Uso, na raiz do projeto e com a DATABASE_URL do banco desejado:

    python -m backend.app.scripts.importar_conteudos
    python -m backend.app.scripts.importar_conteudos --simular
    python -m backend.app.scripts.importar_conteudos caminho/arquivo.json

- A disciplina é encontrada pelo CÓDIGO (ex.: FGA0003), que é igual em todos
  os bancos; os ids mudam de banco para banco.
- Itens com "estado": "pendente" viram contribuições pendentes (aparecem na
  moderação); os demais viram conteúdos já publicados.
- O autor é uma conta desativada, sem login, criada se não existir.
- Rodar de novo não duplica nada: itens com o mesmo título na mesma disciplina
  são ignorados.
- O script só acrescenta dados; não altera nem apaga o que já existe.
"""

from __future__ import annotations

import argparse
import json
import secrets
from dataclasses import dataclass, field
from pathlib import Path

from email_validator import EmailNotValidError, validate_email
from sqlmodel import Session, select

from backend.app.domain import (
    ConteudoAcademico,
    Contribuicao,
    Disciplina,
    EstadoConteudo,
    EstadoContribuicao,
    PerfilUsuario,
    TipoConteudo,
    Usuario,
)
from backend.app.services.auth_service import hash_senha

ARQUIVO_PADRAO = Path(__file__).resolve().parents[1] / "seeds" / "conteudos_demonstracao.json"
ESTADOS_VALIDOS = {"publicado", "pendente"}


@dataclass
class Resultado:
    publicados: int = 0
    pendentes: int = 0
    ja_existentes: int = 0
    disciplinas_nao_encontradas: list[str] = field(default_factory=list)


def carregar_arquivo(caminho: Path) -> dict:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    validar_dados(dados)
    return dados


def validar_dados(dados: dict) -> None:
    """Confere o formato do arquivo antes de tocar no banco."""
    autor = dados.get("autor") or {}
    if not autor.get("nome") or not autor.get("email"):
        raise ValueError("O arquivo precisa de autor.nome e autor.email.")
    try:
        # Mesma regra do cadastro: domínios reservados como .local são recusados.
        validate_email(autor["email"], check_deliverability=False)
    except EmailNotValidError as erro:
        raise ValueError(f"E-mail do autor inválido: {erro}") from erro

    tipos = {tipo.value for tipo in TipoConteudo}
    vistos: set[tuple[str, str]] = set()
    for posicao, item in enumerate(dados.get("conteudos") or [], start=1):
        for campo in ("disciplina", "tipo", "titulo", "corpo"):
            if not str(item.get(campo) or "").strip():
                raise ValueError(f"Item {posicao}: campo '{campo}' vazio.")
        if item["tipo"] not in tipos:
            raise ValueError(f"Item {posicao}: tipo '{item['tipo']}' inválido.")
        if len(item["titulo"]) > 200:
            raise ValueError(f"Item {posicao}: título com mais de 200 caracteres.")
        if len(item.get("origem") or dados.get("origem_padrao") or "") > 500:
            raise ValueError(f"Item {posicao}: origem com mais de 500 caracteres.")
        if item.get("estado", "publicado") not in ESTADOS_VALIDOS:
            raise ValueError(f"Item {posicao}: estado deve ser 'publicado' ou 'pendente'.")
        chave = (item["disciplina"], item["titulo"])
        if chave in vistos:
            raise ValueError(f"Item {posicao}: título repetido na disciplina {item['disciplina']}.")
        vistos.add(chave)


def obter_autor(
    session: Session,
    nome: str,
    email: str,
    emails_antigos: list[str] | None = None,
) -> Usuario:
    autor = session.exec(select(Usuario).where(Usuario.email == email.lower())).first()
    if autor is None:
        # Conta criada por uma versão anterior do arquivo, com outro e-mail:
        # reaproveita e atualiza o e-mail, em vez de criar uma segunda conta.
        for antigo in emails_antigos or []:
            autor = session.exec(select(Usuario).where(Usuario.email == antigo.lower())).first()
            if autor is not None:
                autor.email = email.lower()
                session.add(autor)
                session.flush()
                return autor
    if autor is None:
        autor = Usuario(
            nome=nome,
            email=email.lower(),
            # Senha aleatória e conta desativada: ninguém consegue entrar com ela.
            senha_hash=hash_senha(secrets.token_urlsafe(32)),
            perfil=PerfilUsuario.USUARIO,
            ativo=False,
        )
        session.add(autor)
        session.flush()
    return autor


def importar(session: Session, dados: dict) -> Resultado:
    resultado = Resultado()
    autor = obter_autor(
        session,
        dados["autor"]["nome"],
        dados["autor"]["email"],
        dados["autor"].get("emails_antigos"),
    )
    origem_padrao = dados.get("origem_padrao")

    for item in dados.get("conteudos") or []:
        disciplina = session.exec(
            select(Disciplina).where(Disciplina.codigo == item["disciplina"])
        ).first()
        if disciplina is None:
            if item["disciplina"] not in resultado.disciplinas_nao_encontradas:
                resultado.disciplinas_nao_encontradas.append(item["disciplina"])
            continue

        campos = {
            "disciplina_id": disciplina.id,
            "tipo": TipoConteudo(item["tipo"]),
            "titulo": item["titulo"].strip(),
            "corpo_ou_url": item["corpo"].strip(),
            "autor_id": autor.id,
            "origem": item.get("origem") or origem_padrao,
        }

        if item.get("estado") == "pendente":
            existente = session.exec(
                select(Contribuicao.id).where(
                    Contribuicao.disciplina_id == disciplina.id,
                    Contribuicao.titulo == campos["titulo"],
                )
            ).first()
            if existente is not None:
                resultado.ja_existentes += 1
                continue
            session.add(Contribuicao(**campos, estado=EstadoContribuicao.PENDENTE))
            resultado.pendentes += 1
        else:
            existente = session.exec(
                select(ConteudoAcademico.id).where(
                    ConteudoAcademico.disciplina_id == disciplina.id,
                    ConteudoAcademico.titulo == campos["titulo"],
                )
            ).first()
            if existente is not None:
                resultado.ja_existentes += 1
                continue
            session.add(ConteudoAcademico(**campos, estado=EstadoConteudo.PUBLICADO))
            resultado.publicados += 1

    return resultado


def main(argumentos: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("arquivo", nargs="?", type=Path, default=ARQUIVO_PADRAO)
    parser.add_argument(
        "--simular",
        action="store_true",
        help="Mostra o que seria importado, sem gravar nada no banco.",
    )
    args = parser.parse_args(argumentos)

    from backend.app.db import engine

    dados = carregar_arquivo(args.arquivo)
    with Session(engine) as session:
        resultado = importar(session, dados)
        if args.simular:
            session.rollback()
        else:
            session.commit()

    prefixo = "[simulação] " if args.simular else ""
    print(f"{prefixo}Conteúdos publicados criados: {resultado.publicados}")
    print(f"{prefixo}Contribuições pendentes criadas: {resultado.pendentes}")
    print(f"{prefixo}Já existiam (ignorados): {resultado.ja_existentes}")
    if resultado.disciplinas_nao_encontradas:
        codigos = ", ".join(resultado.disciplinas_nao_encontradas)
        print(f"{prefixo}Disciplinas não encontradas neste banco: {codigos}")


if __name__ == "__main__":
    main()
