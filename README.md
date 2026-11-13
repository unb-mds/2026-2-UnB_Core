# UNB CORE
 
Plataforma acadêmica colaborativa da Universidade de Brasília (UnB), com conteúdos organizados por curso e disciplina e contribuições submetidas à moderação.
 
1. **Base de conhecimento acadêmica** com resumos, dicas, dificuldades, provas, implementações e links.
2. **Contribuições moderadas** enviadas por usuários autenticados e revisadas por moderadores ou administradores.
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
- **Banco de dados**: SQLite no desenvolvimento e no MVP
 
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

Configure uma chave local para os tokens na mesma janela do PowerShell:

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://USUARIO:SENHA@localhost:5432/NOME_DO_BANCO"
$env:JWT_SECRET_KEY = "dev-only-change-this-secret-key-32-bytes-minimum"
```

Antes de iniciar a API, aplique as migrations:

```powershell
.\.venv\Scripts\alembic.exe -c backend\alembic.ini upgrade head
```

Inicie a API:





```powershell
python -m uvicorn backend.app.main:app --reload
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

O usuário precisa estar ativo para acessar `/api/v1/auth/me`. No cadastro atual,
envie `"ativo": true` no corpo da requisição. Para parar o servidor, pressione
`Ctrl+C` no terminal.
 
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
