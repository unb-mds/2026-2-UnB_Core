# UNB CORE
 
Plataforma acadêmica colaborativa da Universidade de Brasília (UnB), com conteúdos organizados por curso e disciplina e contribuições submetidas à moderação.
 
1. **Base de conhecimento acadêmica** com resumos, dicas, dificuldades, provas, implementações e links.
2. **Contribuições moderadas** enviadas por usuários autenticados e revisadas por moderadores ou administradores.
3. **Perfil do usuário**, onde cada pessoa edita o próprio nome, e-mail e senha.

Projeto desenvolvido para a disciplina de **Métodos de Desenvolvimento de Software (MDS) - 2026/2**, Universidade de Brasília.

## Status do projeto

**Fase atual: desenvolvimento e integração.** O backend possui uma API funcional construída com FastAPI, incluindo autenticação de usuários, cadastro, login e acesso a rotas protegidas. O projeto continua em evolução, com novas funcionalidades, testes, integração com o frontend e melhorias de documentação sendo desenvolvidos nas sprints.
 

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
- [`docs/backend`](docs/backend) Documentação das Sprints do Backend.
- [`docs/frontend`](docs/frontend) Documentação das Sprints do Frontend.
- [`docs/documento_de_visao.md`](docs/documento_de_visao.md) Documento de Visão.
- `Board no Miro com Documentações Gerais:` https://miro.com/app/board/uXjVHkk8Wek=/?share_link_id=144842983750
- `Figma Storymap:` https://www.figma.com/board/qmgPv7RFMwdFjr0kqOzTag/Welcome-to-FigJam?node-id=1-2&t=QFJpQxSbXNEcukDx-1
- `Figma do Protótipo de Alta Fidelidade (Frontend):` https://www.figma.com/site/wV4UDTWGMPOiqpO7Ik9ErA/UnB_Core?node-id=23-665&t=vpy0So2nUZVnKKSz-1

## Stack
 
- **Back-end**: Python (FastAPI)
- **Front-end**: JavaScript (React)
- **Banco de dados**: PostgreSQL, com migrations Alembic
- **Dados acadêmicos**: cursos e disciplinas coletados do SIGAA público (escopo: campus do Gama, FCTE)
 
## Como rodar localmente

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

## Contribuindo
 
Consulte o guia de contribuição do grupo (em construção) antes de abrir uma Pull Request. Issues e o quadro de tarefas do projeto refletem o progresso das sprints.
 
## Licença

Este projeto está licenciado sob os termos da licença MIT.
- [`LICENSE`](LICENSE) Veja este arquivo para o texto completo.
