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
(ou 22.12 ou superior). Crie e ative o ambiente virtual na raiz do repositório
e instale as dependências do backend:

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

Para configuração detalhada do banco, solução de problemas e outros comandos,
consulte a seção **Como rodar localmente** do README do projeto.
