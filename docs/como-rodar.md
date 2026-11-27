# Como rodar o projeto

Os comandos desta página consideram Windows com PowerShell e devem ser
executados a partir da raiz do repositório.

Para publicar a aplicação, consulte também o
[guia de publicação no Vercel, Render e Neon](publicacao.md).

## Opção recomendada: Docker

Instale e inicie o Docker Desktop. No PowerShell, configure as variáveis dos
serviços:

```powershell
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "password"
$env:POSTGRES_DB = "unb_core"
$env:JWT_SECRET_KEY = "troque-por-uma-chave-secreta-com-pelo-menos-32-caracteres"
$env:VITE_API_URL = "http://localhost:8000/api/v1"

$env:ADMIN_NAME = "Administrador"
$env:ADMIN_EMAIL = "admin@example.com"
$env:ADMIN_PASSWORD = "troque-esta-senha"
```

Inicie os serviços e confira o estado:

```powershell
docker compose up --build -d
docker compose ps
docker compose logs backend
```

- Frontend: <http://localhost:5173>
- API: <http://localhost:8000>
- Documentação da API: <http://localhost:8000/docs>

Para encerrar sem apagar os dados:

```powershell
docker compose down
```

Para apagar também o banco local e começar do zero:

```powershell
docker compose down -v
```

> `docker compose down -v` remove permanentemente o volume PostgreSQL local.

## Execução manual

Esta opção requer Python 3.11 ou superior, PostgreSQL 14 ou superior e Node.js
20.19 ou superior (ou 22.12 ou superior).

### Backend

Crie e ative o ambiente virtual na raiz do repositório:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

Crie um banco PostgreSQL vazio e configure a conexão e a chave JWT na mesma
janela do PowerShell:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres unbcore

$env:DATABASE_URL = "postgresql+psycopg2://postgres:SUA_SENHA@localhost:5432/unbcore"
$env:JWT_SECRET_KEY = "dev-only-change-this-secret-key-32-bytes-minimum"
```

Sem `DATABASE_URL`, o backend usa SQLite local. Aplique as migrations e inicie
a API:

```powershell
.\.venv\Scripts\alembic.exe -c backend\alembic.ini upgrade head
python -m uvicorn backend.app.main:app --reload
```

A API fica em <http://127.0.0.1:8000> e sua documentação em
<http://127.0.0.1:8000/docs>.

Para persistir a `DATABASE_URL` no Windows:

```powershell
[Environment]::SetEnvironmentVariable(
  "DATABASE_URL",
  "postgresql+psycopg2://postgres:SUA_SENHA@localhost:5432/unbcore",
  "User"
)
```

Para aumentar o tempo da sessão durante uma apresentação:

```powershell
$env:ACCESS_TOKEN_EXPIRE_MINUTES = "480"
```

### Primeiro administrador

Cadastre uma conta normalmente e promova-a no banco:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d unbcore -c "UPDATE usuario SET perfil = 'ADMINISTRADOR' WHERE email = 'seu-email@exemplo.com';"
```

Saia e entre novamente para carregar o novo perfil.

### Frontend

Em outro terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Abra <http://localhost:5173>.

Se `node_modules` estiver desatualizada ou ocorrer
`Cannot find native binding`:

```powershell
cd frontend
Remove-Item node_modules -Recurse -Force
npm ci
npm run dev
```

## Testar a API

Abra <http://127.0.0.1:8000/docs> e, no Swagger UI:

1. Execute `POST /api/v1/auth/cadastro`.
2. Execute `POST /api/v1/auth/login`.
3. Copie o `access_token`.
4. Clique em **Authorize** e informe `Bearer <access_token>`.
5. Execute `GET /api/v1/auth/me`.

## Testes

Backend:

```powershell
python -m pytest backend/tests/integration
python -m pytest backend/tests/unit backend/tests/contract
```

Frontend:

```powershell
cd frontend
npm test
npm run build
npm run lint
```

## Teste de sabotagem

O teste de sabotagem planta um defeito proposital em cada módulo crítico do
backend e do frontend, executa as suítes de testes e verifica se os defeitos
são detectados. Os arquivos originais são restaurados ao final de cada caso,
mesmo quando a execução é interrompida por um erro.

Na raiz do repositório:

```powershell
.\.venv\Scripts\python.exe scripts/teste_sabotagem.py
.\.venv\Scripts\python.exe scripts/teste_sabotagem.py --parte backend
.\.venv\Scripts\python.exe scripts/teste_sabotagem.py --parte frontend
.\.venv\Scripts\python.exe scripts/teste_sabotagem.py --listar
```

Para cada módulo, o resultado é:

- **Pegou:** a suíte de testes falhou, como deveria.
- **Escapou:** a suíte passou com o defeito, indicando que falta cobertura.

O comando termina com erro se algum defeito escapar. Antes de plantar as
sabotagens, ele verifica se a suíte já passa sem defeitos.

Os módulos críticos e os defeitos ficam na lista `SABOTAGENS` do arquivo
[scripts/teste_sabotagem.py](https://github.com/unb-mds/2026-2-UnB_Core/blob/main/scripts/teste_sabotagem.py).
Exemplos: conta desativada consegue entrar, token assinado com outra chave é
aceito, moderador gere contas da equipe, rejeição sem justificativa e link
`javascript:` aceito.

Ao criar uma regra de negócio ou segurança, acrescente o módulo correspondente
à lista `SABOTAGENS`.

Se a execução for interrompida à força, confira `git status`. Caso algum arquivo
tenha sido alterado, restaure apenas o arquivo afetado:

```powershell
git checkout -- <arquivo>
```

## Backups do banco

O Docker cria backups em `backups/` a cada 24 horas.

```powershell
docker compose logs db-backup
docker compose up -d --force-recreate db-backup

Get-ChildItem .\backups\*.dump |
  Sort-Object LastWriteTime -Descending
```

Para restaurar um arquivo existente:

```powershell
docker compose stop backend
$env:RESTORE_FILE = "unb_core-AAAAMMDD-HHMMSS.dump"
docker compose run --rm db-restore
Remove-Item Env:RESTORE_FILE
docker compose start backend
```

## Problemas comuns

- **O frontend não conecta à API:** confirme se a API está em
  <http://127.0.0.1:8000> e se o navegador abre
  <http://127.0.0.1:8000/api/v1/cursos>.
- **Todas as rotas retornam `ERRO_INTERNO`:** confira a `DATABASE_URL`, aplique
  as migrations e reinicie a API.
- **A porta 5432 está em uso:** pare o PostgreSQL local ou execute o projeto
  sem Docker.
- **`ERESOLVE` no npm:** remova `node_modules`, atualize a branch e execute
  `npm ci` novamente.
- **`relação "usuario" já existe`:** use um banco vazio ou remova as tabelas
  antigas após fazer backup.
