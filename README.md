# UNB CORE

[![Static Badge](https://img.shields.io/badge/Python-Black?style=for-the-badge&logo=Python&label=3.11%2B&color=%23ffe45d)](https://www.python.org/downloads/release/python-31318/)
[![Static Badge](https://img.shields.io/badge/React-Black?style=for-the-badge&logo=react&color=black)](https://react.dev/)
[![Static Badge](https://img.shields.io/badge/PostgreSQL-%2332658e?style=for-the-badge&logo=postgresql&logoColor=white&color=%2332658e)](https://www.postgresql.org/download/)
[![Static Badge](https://img.shields.io/badge/Docker-%23586af8?style=for-the-badge&logo=Docker&color=%23586af8)](https://docs.docker.com/get-docker/desktop/)
</br>
<img src="https://img.shields.io/github/v/release/unb-mds/2026-2-UnB_Core?label=version">
[![GitHub issues](https://img.shields.io/github/issues/unb-mds/2026-2-UnB_Core)](https://github.com/unb-mds/2026-2-UnB_Core/issues)
[![GitHub contributors](https://img.shields.io/github/contributors/unb-mds/2026-2-UnB_Core)](https://img.shields.io/github/contributors/unb-mds/2026-2-UnB_Core)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/unb-mds/2026-2-UnB_Core)](https://img.shields.io/github/stars/unb-mds/2026-2-UnB_Core)
 
Plataforma acadêmica colaborativa da Universidade de Brasília (UnB), com conteúdos organizados por curso e disciplina e contribuições submetidas à moderação.
 
1. **Base de conhecimento acadêmica** com resumos, dicas, dificuldades, provas, implementações e links.
2. **Contribuições moderadas** enviadas por usuários autenticados e revisadas por moderadores ou administradores.
3. **Perfil do usuário**, onde cada pessoa edita o próprio nome, e-mail e senha.
##
<img width="1646" height="599" alt="image" src="https://github.com/user-attachments/assets/ea69e958-ca90-454b-bbb2-9ac69f06b856" />

<img width="1383" height="496" alt="image" src="https://github.com/user-attachments/assets/c9d45efb-11a3-4b14-bc86-4ad115111890" />


Projeto desenvolvido para a disciplina de **Métodos de Desenvolvimento de Software (MDS) - 2026/2**, Universidade de Brasília.

## Status do projeto

**Fase atual: desenvolvimento e integração.** A integração do Backend e Frontend já está completa, bastando apenas o seu aperfeiçoamento. O backend possui uma API funcional construída com FastAPI, incluindo autenticação de usuários, cadastro, login e acesso às disciplinas e cursos utilizando um crawler com o sistema do SIGAA. O projeto continua em evolução, com novas funcionalidades, testes e melhorias de documentação sendo desenvolvidos nas sprints.
 

## Integrantes

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/arthurhc3">
        <img style="border-radius: 50%;" src="https://github.com/arthurhc3.png" width="150px" alt="Arthur Vinicius Morais de Lima"/><br />
        <sub><b>Arthur Vinicius Morais de Lima</b></sub>
      </a>
      <br />
      <sub>Matrícula: 242015764</sub><br />
      <sub>Função: <i>Backend Dev</i></sub>
    </td>

   <td align="center">
      <a href="https://github.com/DanielAlmeidaFrota">
        <img style="border-radius: 50%;" src="https://github.com/DanielAlmeidaFrota.png" width="150px" alt="Daniel Almeida Frota"/><br />
        <sub><b>Daniel Almeida Frota</b></sub>
      </a>
      <br />
      <sub>Matrícula: 251041010</sub><br />
      <sub>Função: <i>Frontend Dev</i></sub>
    </td>
 
   <td align="center">
      <a href="https://github.com/Joao-vithor-1">
        <img style="border-radius: 50%;" src="https://github.com/Joao-vithor-1.png" width="150px" alt="João Vithor Camargo Emidio"/><br />
        <sub><b>João Vithor Camargo Emidio</b></sub>
      </a>
      <br />
      <sub>Matrícula: 251023264</sub><br />
      <sub>Função: <i>Backend Dev</i></sub>
    </td>
  </tr>
</table>


## Documentação

- [`docs/requisitos.md`](docs/requisitos.md) Visão geral, requisitos funcionais e não funcionais, entidades e critérios de sucesso.
- [`docs/sprint`](docs/Sprint) Documentação Geral das Sprints.
- `GitPage UNB Core:` https://unb-mds.github.io/2026-2-UnB_Core/
- `Board no Miro com Documentações Gerais:` https://miro.com/app/board/uXjVHkk8Wek=/?share_link_id=144842983750
- `Figma Storymap:` https://www.figma.com/board/qmgPv7RFMwdFjr0kqOzTag/Welcome-to-FigJam?node-id=1-2&t=QFJpQxSbXNEcukDx-1
- `Figma do Protótipo de Alta Fidelidade (Frontend):` https://www.figma.com/site/wV4UDTWGMPOiqpO7Ik9ErA/UnB_Core?node-id=23-665&t=vpy0So2nUZVnKKSz-1

## Stack
 
- **Back-end**: Python (FastAPI)
- **Front-end**: JavaScript (React)
- **Banco de dados**: PostgreSQL, com migrations Alembic
- **Dados acadêmicos**: cursos e disciplinas coletados do SIGAA público (escopo: campus do Gama, FCTE)
 
## Como rodar localmente

### Docker

Pré-requisitos:

- Docker Desktop instalado e em execução.
- PowerShell aberto na raiz do repositório.

Configure as variáveis na mesma janela do PowerShell. Os valores do
administrador são opcionais; quando informados, a conta é criada
automaticamente na inicialização do backend:

```powershell
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "password"
$env:POSTGRES_DB = "unb_core"
$env:JWT_SECRET_KEY = "troque-por-uma-chave-secreta-com-pelo-menos-32-caracteres"

$env:ADMIN_NAME = "Administrador"
$env:ADMIN_EMAIL = "admin@example.com"
$env:ADMIN_PASSWORD = "troque-esta-senha"

$env:VITE_API_URL = "http://localhost:8000/api/v1"
```

Inicie os serviços:

```powershell
docker compose up --build -d
```

Verifique o estado dos containers e os logs do backend:

```powershell
docker compose ps
docker compose logs backend
```

Quando as variáveis `ADMIN_*` estiverem configuradas, o log deve informar que
a conta administrativa foi configurada. O frontend estará disponível em
`http://localhost:5173` e a documentação da API em `http://localhost:8000/docs`.

Para parar os serviços sem apagar os dados:

```powershell
docker compose down
```

Para apagar também o banco de desenvolvimento e recriá-lo do zero:

```powershell
docker compose down -v
docker compose up --build -d
```

O comando `docker compose down -v` remove permanentemente o volume local do
PostgreSQL.


### Backend

Os comandos abaixo devem ser executados no terminal integrado do VS Code ou no
PowerShell, a partir da raiz do repositório:

```powershell

# Execute uma vez, caso o ambiente virtual ainda não exista
py -m venv .venv

# Ative o ambiente virtual nesta janela
.\.venv\Scripts\Activate.ps1

# Instale as dependências disponíveis no projeto
python -m pip install -r backend\requirements.txt
```

#### Banco de dados (PostgreSQL)

Instale o PostgreSQL (versão 14 ou superior) e crie um banco vazio para o
projeto. Exemplo com o `psql` do PostgreSQL 18 no Windows, criando o banco
`unbcore`:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres unbcore
```

Configure o endereço do banco e a chave dos tokens **na mesma janela do
PowerShell** em que a API vai rodar:

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://USUARIO:SENHA@localhost:5432/NOME_DO_BANCO"
$env:JWT_SECRET_KEY = "dev-only-change-this-secret-key-32-bytes-minimum"
```

Exemplo com o usuário padrão `postgres` e o banco `unbcore`:
`postgresql+psycopg2://postgres:SUA_SENHA@localhost:5432/unbcore`.

> O backend lê essas configurações apenas das variáveis de ambiente (o arquivo
> `.env` não é carregado). Se a `DATABASE_URL` não for definida, a API usa um
> SQLite local (`unb_core.db`) em vez do PostgreSQL.

O login vale 30 minutos. Depois disso o site pede para entrar de novo. Para
uma apresentação, aumente a duração antes de iniciar a API (o valor é em
minutos):

```powershell
$env:ACCESS_TOKEN_EXPIRE_MINUTES = "480"
```

Para não precisar repetir o comando a cada terminal novo, salve a variável no
seu usuário do Windows (vale para terminais abertos depois do comando):

```powershell
[Environment]::SetEnvironmentVariable("DATABASE_URL", "postgresql+psycopg2://postgres:SUA_SENHA@localhost:5432/unbcore", "User")
```

Antes de iniciar a API, aplique as migrations:

```powershell
.\.venv\Scripts\alembic.exe -c backend\alembic.ini upgrade head
```

#### Iniciar a API

```powershell
python -m uvicorn backend.app.main:app --reload
```

Na primeira execução com o banco vazio, a API coleta os cursos e as
disciplinas do SIGAA em segundo plano (precisa de internet e pode levar alguns
minutos). Em seguida, aplica a estrutura curricular de cada curso do Gama,
para que cada curso mostre só as próprias disciplinas. Nas execuções seguintes
a coleta não é repetida.

Se o seu banco já tinha disciplinas antes dessa mudança (todos os cursos do
Gama com as mesmas disciplinas), sincronize as estruturas curriculares uma vez,
com a `DATABASE_URL` configurada:

```powershell
python -c "import asyncio; from sqlmodel import Session; from backend.app.db import engine; from backend.app.crawler.crawlerCurriculo import coletar_e_sincronizar_curriculos; print(asyncio.run(coletar_e_sincronizar_curriculos(Session(engine))))"
```

Abra a documentação interativa do FastAPI no navegador:

```text
http://127.0.0.1:8000/docs
```

No Swagger UI:

1. Execute `POST /api/v1/auth/cadastro` para criar um usuário.
2. Execute `POST /api/v1/auth/login` com o mesmo e-mail e senha.
3. Copie o valor de `access_token` da resposta.
4. Clique em **Authorize**, informe `Bearer <access_token>` e confirme.
5. Execute `GET /api/v1/auth/me` para testar uma rota autenticada.

Para parar o servidor, pressione `Ctrl+C` no terminal.

#### Primeiro administrador

Pela API, só um administrador cria ou promove outros usuários. Para criar o
primeiro, cadastre a conta normalmente e promova-a direto no banco:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d unbcore -c "UPDATE usuario SET perfil = 'ADMINISTRADOR' WHERE email = 'seu-email@exemplo.com';"
```

O valor precisa estar em maiúsculas. Saia e entre de novo na aplicação para
que o novo perfil seja carregado. A partir daí, os outros moderadores e
administradores podem ser criados pela página **Usuários**.

#### Conteúdos de demonstração

Para preencher a base de conhecimento (por exemplo, numa apresentação), importe
os conteúdos de demonstração de `backend/app/seeds/conteudos_demonstracao.json`.
Com a `DATABASE_URL` do banco desejado configurada:

```powershell
# Mostra o que seria importado, sem gravar nada
.\.venv\Scripts\python.exe -m backend.app.scripts.importar_conteudos --simular

# Importa
.\.venv\Scripts\python.exe -m backend.app.scripts.importar_conteudos
```

- **O que é criado:** 33 conteúdos já publicados e 3 contribuições pendentes, para demonstrar a moderação.
- **Disciplinas:** cada uma é encontrada pelo código (ex.: FGA0003), então o mesmo arquivo funciona em qualquer banco.
- **Rodar de novo:** não duplica nada e nunca altera ou apaga o que já existe.
- **Autoria:** os textos foram escritos com apoio de IA e aparecem com o autor "Equipe UnB Core (demonstração)". Veja [`docs/ai-usage.md`](docs/ai-usage.md).

#### Problemas comuns

- **Front mostra "Não foi possível conectar à API"**: confira se a API está
  rodando em `http://127.0.0.1:8000` e abra
  `http://127.0.0.1:8000/api/v1/cursos` no navegador. Se aparecer
  `ERRO_INTERNO`, a API está no ar mas não consegue usar o banco.
- **`ERRO_INTERNO` em todas as rotas**: a `DATABASE_URL` está errada (banco
  inexistente, senha ausente ou incorreta) ou as migrations não foram
  aplicadas. Confira o valor com `echo $env:DATABASE_URL`, corrija, rode o
  `alembic ... upgrade head` e reinicie a API.
- **`relação "usuario" já existe` ao rodar as migrations**: o banco foi criado
  antes do Alembic. Use um banco vazio ou faça backup e remova as tabelas
  antigas antes de migrar.
 
### Frontend

O frontend requer Node.js 20.19 ou superior, ou Node.js 22.12 ou superior.
Verifique a versão instalada:

```powershell
node --version
```

Se necessário, atualize o Node.js no Windows:

```powershell
winget upgrade OpenJS.NodeJS
```

Feche e reabra o terminal após a atualização. Em seguida, em outro terminal,
instale as dependências e inicie o frontend:

```powershell
cd frontend
npm ci
npm run dev
```

Se ocorrer o erro `Cannot find native binding`, refaça a instalação das
dependências:

```powershell
cd frontend
Remove-Item node_modules -Recurse -Force
npm ci
npm run dev
```

Se o `npm ci` ou o `npm install` falhar com `ERESOLVE` / `unable to resolve
dependency tree` (conflito de peer dependencies), normalmente a pasta
`node_modules` ainda é de uma versão antiga do projeto (por exemplo, Vite 7.1.7,
que também gera os alertas de vulnerabilidade do `npm audit`). O projeto usa
Vite 8; atualize a branch, apague as dependências antigas e instale de novo:

```powershell
cd frontend
git pull
Remove-Item node_modules -Recurse -Force
npm ci
```

Se o erro continuar, instale ativando o modo legado de peer dependencies do npm:

```powershell
npm install --legacy-peer-deps
```

Use `npm audit` para conferir as vulnerabilidades. Na versão atual das
dependências o resultado esperado é `found 0 vulnerabilities`. Não rode
`npm audit fix --force`, pois ele pode trocar versões principais das bibliotecas
e quebrar o projeto para o restante da equipe.

Comandos de qualidade do frontend:

```powershell
npm run build
npm run lint
npm test
```

#### Testes do frontend

Os testes usam [Vitest](https://vitest.dev/) e [Testing Library](https://testing-library.com/docs/react-testing-library/intro/).
Cada teste desenha a tela num navegador simulado (jsdom), age como a pessoa usando
a página (clica, digita) e confere o que aparece. A API é simulada com `vi.mock`,
então os testes não precisam do backend nem do banco rodando.

```powershell
npm test                              # roda todos os testes uma vez
npx vitest                            # roda de novo a cada arquivo salvo
npx vitest run src/pages/LoginPage    # só os testes de uma tela
```

Os arquivos de teste ficam ao lado do código, com o nome `NomeDoArquivo.test.jsx`
(por exemplo, [ContribuicaoPage.test.jsx](frontend/src/pages/ContribuicaoPage.test.jsx)).
Procure os elementos pelo que a pessoa vê, como o texto do botão ou o rótulo do campo,
e não por classes CSS: assim o teste só quebra quando o comportamento muda.

### Backups do banco de dados

O serviço `db-backup` cria um backup completo do PostgreSQL ao iniciar e depois
a cada 24 horas, na pasta `backups/` da raiz do projeto. Os arquivos têm o
formato `unb_core-AAAAMMDD-HHMMSS.dump`. Backups com mais de 7 dias são apagados
automaticamente.

Confira se o backup está funcionando (o log deve mostrar `Backup completed`):

```powershell
docker compose logs db-backup
```

Para fazer um backup agora:

```powershell
docker compose up -d --force-recreate db-backup
```

Para listar os backups:

```powershell
Get-ChildItem .\backups\*.dump | Sort-Object LastWriteTime -Descending |
  Format-Table Name, Length, LastWriteTime
```

Para conferir se um arquivo não está corrompido (deve listar a estrutura do
banco, sem alterar nada):

```powershell
docker compose exec db-backup pg_restore --list /backups/unb_core-20261121-132627.dump
```

Se o log mostrar `Backup failed`, veja [Problemas com a senha](#problemas-com-a-senha-do-banco).
Enquanto o backup falhar, nenhum novo arquivo é criado, e depois de 7 dias os
backups antigos também são apagados. Copie a pasta `backups/` de vez em quando
para um local seguro (HD externo ou nuvem). Ela é ignorada pelo Git e não deve
ser enviada ao repositório.

### Restaurar o banco

A restauração é manual e substitui o conteúdo atual do banco `unb_core` pelo do
arquivo escolhido. Antes disso, o serviço salva o banco atual em
`backups/unb_core-before-restore-*.dump`.

```powershell
docker compose stop backend
$env:RESTORE_FILE = "unb_core-AAAAMMDD-HHMMSS.dump"
docker compose run --rm db-restore
Remove-Item Env:RESTORE_FILE
docker compose start backend
```

Troque o nome do arquivo por um que exista na pasta `backups/`. Se
`RESTORE_FILE` não for informado ou o arquivo não existir, a operação é
cancelada. A restauração só deu certo se a última linha for `Restore completed`
e **nenhum erro** aparecer antes dela.


## Contribuindo
 
Consulte o [guia de contribuição](https://github.com/unb-mds/2026-2-UnB_Core/blob/main/CONTRIBUTING.md) do grupo antes de abrir uma Pull Request. Issues e o quadro de tarefas do projeto refletem o progresso das sprints.
 
## Licença

Este projeto está licenciado sob os termos da licença MIT.
- [`LICENSE`](LICENSE) - Veja este arquivo para o texto completo.
