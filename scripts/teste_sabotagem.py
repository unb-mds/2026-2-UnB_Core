"""Teste de sabotagem dos módulos críticos do UNB CORE.

Para cada módulo crítico, planta um defeito proposital no código, roda a suíte
de testes e confere se ela quebra. Depois devolve o arquivo original, mesmo que
algo dê errado no meio.

- "pegou": a suíte quebrou, como deveria.
- "escapou": a suíte passou com o defeito; falta um teste para esse módulo.

Na raiz do repositório:
    .\\.venv\\Scripts\\python.exe scripts/teste_sabotagem.py
    .\\.venv\\Scripts\\python.exe scripts/teste_sabotagem.py --parte frontend
    .\\.venv\\Scripts\\python.exe scripts/teste_sabotagem.py --listar

Termina com código 1 se algum defeito escapar ou se um trecho não for encontrado.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Sabotagem:
    parte: str  # "backend" ou "frontend"
    modulo: str
    defeito: str
    arquivo: str  # caminho a partir da raiz do repositório
    trecho: str  # texto que existe uma única vez no arquivo
    troca: str  # o mesmo texto com o defeito


SABOTAGENS = [
    # ---------- Backend ----------
    Sabotagem(
        "backend", "Login (auth_service)", "conta desativada consegue entrar",
        "backend/app/services/auth_service.py",
        "if usuario is None or not usuario.ativo or not verificar_senha(",
        "if usuario is None or not verificar_senha(",
    ),
    Sabotagem(
        "backend", "Recuperação de senha (auth_service)", "conta desativada gera pedido de senha",
        "backend/app/services/auth_service.py",
        "if usuario is not None and usuario.ativo:",
        "if usuario is not None:",
    ),
    Sabotagem(
        "backend", "Token de login (security)", "token assinado com outra chave é aceito",
        "backend/app/api/security.py",
        "algorithms=[settings.jwt_algorithm],",
        'algorithms=[settings.jwt_algorithm], options={"verify_signature": False},',
    ),
    Sabotagem(
        "backend", "Permissão por perfil (dependencies)", "qualquer perfil acessa rotas restritas",
        "backend/app/api/dependencies.py",
        "if usuario.perfil not in perfis:",
        "if False:",
    ),
    Sabotagem(
        "backend", "Edição de contribuição (contribuicao_service)", "pessoa edita contribuição de outra",
        "backend/app/services/contribuicao_service.py",
        "if contribuicao.autor_id != usuario.id:",
        "if False:",
    ),
    Sabotagem(
        "backend", "Decisão da moderação (moderacao_service)", "pedido de ajustes sem justificativa",
        "backend/app/services/moderacao_service.py",
        'if decisao == DecisaoModeracao.AJUSTES and not (justificativa or "").strip():',
        "if False:",
    ),
    Sabotagem(
        "backend", "Gestão de usuários (usuario_service)", "moderador gere contas da equipe",
        "backend/app/services/usuario_service.py",
        "if not _eh_administrador(ator) and alvo.perfil != PerfilUsuario.USUARIO:",
        "if False:",
    ),
    # A proteção do último administrador fica de fora: pela API, ela só é alcançada
    # quando a regra da própria conta falha (só um administrador ativo exclui outro,
    # e ele mesmo conta como "outro"), então funciona como uma segunda barreira.
    Sabotagem(
        "backend", "Exclusão de contas (usuario_service)", "pessoa exclui a própria conta",
        "backend/app/services/usuario_service.py",
        'raise ErroValidacao("Você não pode excluir a sua própria conta.")',
        "pass",
    ),
    # ---------- Frontend ----------
    Sabotagem(
        "frontend", "Cliente da API (api.js)", "token não é enviado à API",
        "frontend/src/services/api.js",
        "requestHeaders.set('Authorization'",
        "requestHeaders.set('X-Token'",
    ),
    Sabotagem(
        "frontend", "Sessão (auth.js)", "validade do token comparada em segundos, não em milissegundos",
        "frontend/src/state/auth.js",
        "payload.exp * 1000 <= agora",
        "payload.exp <= agora",
    ),
    Sabotagem(
        "frontend", "Formulário de login e cadastro (AuthForm)", "senha de 7 caracteres aceita",
        "frontend/src/components/auth/AuthForm.jsx",
        "form.senha.length < 8",
        "form.senha.length < 7",
    ),
    Sabotagem(
        "frontend", "Tela de login (LoginPage)", "senha temporária não leva a Meu perfil",
        "frontend/src/pages/LoginPage.jsx",
        "onNavigate(session?.trocar_senha ? '/perfil' : '/base-de-conhecimentos')",
        "onNavigate('/base-de-conhecimentos')",
    ),
    Sabotagem(
        "frontend", "Envio de contribuição (ContribuicaoPage)", "tipo de conteúdo deixa de ser obrigatório",
        "frontend/src/pages/ContribuicaoPage.jsx",
        "if (!form.tipo) missingFields.push('tipo de conteúdo')",
        "",
    ),
    Sabotagem(
        "frontend", "Edição de contribuição (EditarContribuicaoForm)", "título deixa de ser obrigatório",
        "frontend/src/components/contribuicoes/EditarContribuicaoForm.jsx",
        "if (!form.titulo.trim()) missingFields.push('título')",
        "",
    ),
    Sabotagem(
        "frontend", "Decisão da moderação (DecisaoModal)", "rejeição sem justificativa",
        "frontend/src/components/moderacao/DecisaoModal.jsx",
        "['ajustes', 'rejeitar'].includes(decisao)",
        "['ajustes'].includes(decisao)",
    ),
    Sabotagem(
        "frontend", "Acesso à moderação (ModeracaoPage)", "usuário comum entra na moderação",
        "frontend/src/pages/ModeracaoPage.jsx",
        "const canModerate = ['moderador', 'administrador'].includes(user?.perfil)",
        "const canModerate = ['usuario', 'moderador', 'administrador'].includes(user?.perfil)",
    ),
    Sabotagem(
        "frontend", "Gestão de usuários (AdminUsuariosPage)", "moderador vê as ações de administrador",
        "frontend/src/pages/AdminUsuariosPage.jsx",
        "const isAdmin = user?.perfil === 'administrador'",
        "const isAdmin = user?.perfil !== 'usuario'",
    ),
    Sabotagem(
        "frontend", "Busca de disciplina (DisciplinaBusca)", "busca começa com 1 letra",
        "frontend/src/components/conteudos/DisciplinaBusca.jsx",
        "const MIN_CARACTERES = 2",
        "const MIN_CARACTERES = 1",
    ),
    Sabotagem(
        "frontend", "Links dos conteúdos (formatacao)", "qualquer esquema vira link, inclusive javascript:",
        "frontend/src/components/conteudos/formatacao.js",
        r"/^https?:\/\/\S+$/i",
        r"/^[a-z]+:\S+$/i",
    ),
]


def comandos_da_suite(parte: str) -> list[tuple[list[str], Path]]:
    """Comandos que rodam a suíte de uma parte; param no primeiro teste que falhar."""
    if parte == "backend":
        pytest = [sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider"]
        return [
            (pytest + ["backend/tests/integration"], RAIZ),
            # O test_errors.py de unit/ precisa do bs4 e já falhava antes deste script.
            (pytest + ["backend/tests/unit", "backend/tests/contract", "--ignore=backend/tests/unit/test_errors.py"], RAIZ),
        ]
    npx = shutil.which("npx")
    if npx is None:
        raise SystemExit("O npx não foi encontrado. Instale o Node.js para testar o frontend.")
    return [([npx, "vitest", "run", "--bail", "1"], RAIZ / "frontend")]


def suite_passa(parte: str) -> bool:
    ambiente = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", NO_COLOR="1")
    for comando, pasta in comandos_da_suite(parte):
        resultado = subprocess.run(comando, cwd=pasta, env=ambiente, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if resultado.returncode != 0:
            return False
    return True


def aplicar(sabotagem: Sabotagem) -> bytes:
    """Planta o defeito e devolve o conteúdo original do arquivo."""
    caminho = RAIZ / sabotagem.arquivo
    original = caminho.read_bytes()
    texto = original.decode("utf-8")
    vezes = texto.count(sabotagem.trecho)
    if vezes != 1:
        raise ValueError(f"o trecho aparece {vezes} vez(es) em {sabotagem.arquivo}; precisa aparecer 1")
    caminho.write_bytes(texto.replace(sabotagem.trecho, sabotagem.troca).encode("utf-8"))
    return original


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--parte", choices=["backend", "frontend"], help="roda só uma parte")
    parser.add_argument("--listar", action="store_true", help="só lista os módulos críticos e os defeitos")
    args = parser.parse_args()

    escolhidas = [s for s in SABOTAGENS if args.parte in (None, s.parte)]
    if args.listar:
        for s in escolhidas:
            print(f"[{s.parte}] {s.modulo}: {s.defeito}")
        return 0

    partes = sorted({s.parte for s in escolhidas})
    for parte in partes:
        print(f"Conferindo se a suíte do {parte} passa sem defeitos...", flush=True)
        if not suite_passa(parte):
            print(f"A suíte do {parte} já falha sem nenhum defeito. Corrija os testes antes de sabotar.")
            return 1

    resultados = []
    for indice, s in enumerate(escolhidas, start=1):
        inicio = time.monotonic()
        print(f"[{indice}/{len(escolhidas)}] {s.modulo}: {s.defeito}...", flush=True)
        try:
            original = aplicar(s)
        except ValueError as erro:
            resultados.append((s, "não aplicado", str(erro)))
            continue
        try:
            pegou = not suite_passa(s.parte)
        finally:
            (RAIZ / s.arquivo).write_bytes(original)
        resultados.append((s, "pegou" if pegou else "escapou", f"{time.monotonic() - inicio:.0f}s"))

    print()
    print("Resultado do teste de sabotagem")
    print("-" * 100)
    for s, situacao, detalhe in resultados:
        print(f"{situacao:13} [{s.parte}] {s.modulo}: {s.defeito} ({detalhe})")
    pegos = sum(1 for _, situacao, _ in resultados if situacao == "pegou")
    print("-" * 100)
    print(f"{pegos} de {len(resultados)} módulos críticos quebram a suíte com um defeito proposital ({100 * pegos // len(resultados)}%).")
    return 0 if pegos == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
