# Como rodar o projeto

Os comandos desta página consideram o Windows com PowerShell e devem ser
executados a partir da raiz do repositório, salvo indicação contrária.

## Opção recomendada: Docker

Instale e inicie o Docker Desktop. No PowerShell, configure as variáveis de
ambiente para os serviços:

```powershell
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "password"
$env:POSTGRES_DB = "unb_core"
$env:JWT_SECRET_KEY = "troque-por-uma-chave-secreta-com-pelo-menos-32-caracteres"
$env:VITE_API_URL = "http://localhost:8000/api/v1"
```

Opcionalmente, configure os dados do administrador inicial:

```powershell
$env:ADMIN_NAME = "Administrador"
$env:ADMIN_EMAIL = "admin@example.com"
$env:ADMIN_PASSWORD = "troque-esta-senha"
```

Inicie os serviços e confira o estado dos containers:

```powershell
docker compose up --build -d
docker compose ps
docker compose logs backend
```

Depois que os serviços estiverem prontos:

- Frontend: <http://localhost:5173>
- Documentação interativa da API: <http://localhost:8000/docs>

Para encerrar sem apagar os dados do banco:

```powershell
docker compose down
```

> **Atenção:** `docker compose down -v` também apaga o volume local do
> PostgreSQL e todos os dados de desenvolvimento nele armazenados.

## Execução manual

Esta opção requer Python, PostgreSQL 14 ou superior e Node.js 20.19 ou superior
(ou 22.12 ou superior).

### Backend

Crie e ative o ambiente virtual na raiz do repositório e instale as dependências:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

Crie um banco PostgreSQL vazio e configure a conexão e a chave JWT na mesma
janela do PowerShell que será usada para iniciar a API:

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://USUARIO:SENHA@localhost:5432/NOME_DO_BANCO"
$env:JWT_SECRET_KEY = "dev-only-change-this-secret-key-32-bytes-minimum"
```

Se `DATABASE_URL` não for configurada, o backend usa um banco SQLite local.
Com as variáveis configuradas, aplique as migrations e inicie a API:

```powershell
.\.venv\Scripts\alembic.exe -c backend\alembic.ini upgrade head
python -m uvicorn backend.app.main:app --reload
```

Em outro terminal, instale as dependências e inicie o frontend:

```powershell
cd frontend
npm ci
npm run dev
```

Abra <http://localhost:5173> para acessar a aplicação. A API fica disponível
em <http://127.0.0.1:8000> e sua documentação interativa em
<http://127.0.0.1:8000/docs>. Para parar cada servidor, pressione `Ctrl+C` no
terminal correspondente.

Crie um banco PostgreSQL vazio, por exemplo:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres unbcore
```

Para persistir a conexão no Windows:

```powershell
[Environment]::SetEnvironmentVariable(
  "DATABASE_URL",
  "postgresql+psycopg2://postgres:SUA_SENHA@localhost:5432/unbcore",
  "User"
)
```

Se o backend já tiver iniciado com dados antigos e todos os cursos do Gama
aparecerem com as mesmas disciplinas, sincronize as estruturas curriculares:

```powershell
python -c "import asyncio; from sqlmodel import Session; from backend.app.db import engine; from backend.app.crawler.crawlerCurriculo import coletar_e_sincronizar_curriculos; print(asyncio.run(coletar_e_sincronizar_curriculos(Session(engine))))"
```

### Primeiro administrador

Cadastre a conta normalmente e promova-a diretamente no banco:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d unbcore -c "UPDATE usuario SET perfil = 'ADMINISTRADOR' WHERE email = 'seu-email@exemplo.com';"
```

Saia e entre novamente na aplicação para carregar o novo perfil.

### Frontend

Verifique o Node.js instalado:

```powershell
node --version
```

Se necessário, atualize e reabra o terminal:

```powershell
winget upgrade OpenJS.NodeJS
```

Em outro terminal, instale as dependências e inicie o frontend:

```powershell
cd frontend
npm ci
npm run dev
```

Se `node_modules` estiver desatualizada ou ocorrer `Cannot find native binding`,
reinstale as dependências:

```powershell
cd frontend
Remove-Item node_modules -Recurse -Force
npm ci
npm run dev
```

Comandos de qualidade:

```powershell
npm run build
npm run lint
npm test
```

Não use `npm audit fix --force`; a atualização pode substituir versões
principais e quebrar o projeto.

## Testar a API

Abra <http://127.0.0.1:8000/docs> e, no Swagger UI:

1. Execute `POST /api/v1/auth/cadastro` para criar um usuário.
2. Execute `POST /api/v1/auth/login` com o mesmo e-mail e senha.
3. Copie o valor de `access_token` da resposta.
4. Clique em **Authorize**, informe `Bearer <access_token>` e confirme.
5. Execute `GET /api/v1/auth/me` para testar uma rota autenticada.

## Problemas comuns

- **O frontend não conecta à API:** confirme que a API está em
  <http://127.0.0.1:8000> e abra
  <http://127.0.0.1:8000/api/v1/cursos>.
- **Todas as rotas retornam `ERRO_INTERNO`:** confira `DATABASE_URL`, execute
  as migrations e reinicie a API:

  ```powershell
  echo $env:DATABASE_URL
  .\.venv\Scripts\alembic.exe -c backend\alembic.ini upgrade head
  ```

- **`relação "usuario" já existe`:** use um banco vazio ou remova as tabelas
  antigas após fazer backup.
- **`ERESOLVE` ou conflito de peer dependencies:** atualize a branch, remova
  `node_modules` e execute `npm ci` novamente.

## Backups

As instruções de criação e restauração de backups estão em
[Backups e restauração](backups.md).
