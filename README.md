# UNB CORE

[![Static Badge](https://img.shields.io/badge/Python-Black?style=for-the-badge&logo=Python&label=3.11%2B&color=%23ffe45d)](https://www.python.org/downloads/release/python-31318/)
[![Static Badge](https://img.shields.io/badge/React-Black?style=for-the-badge&logo=react&color=black)](https://react.dev/)
[![Static Badge](https://img.shields.io/badge/PostgreSQL-%2332658e?style=for-the-badge&logo=postgresql&logoColor=white&color=%2332658e)](https://www.postgresql.org/download/)
[![Static Badge](https://img.shields.io/badge/Docker-%23586af8?style=for-the-badge&logo=Docker&color=%23586af8)](https://docs.docker.com/get-docker/desktop/)
</br>
[<img src="https://img.shields.io/github/v/release/unb-mds/2026-2-UnB_Core?label=version">](https://github.com/unb-mds/2026-2-UnB_Core/releases)
[![GitHub issues](https://img.shields.io/github/issues/unb-mds/2026-2-UnB_Core)](https://github.com/unb-mds/2026-2-UnB_Core/issues)
[![GitHub contributors](https://img.shields.io/github/contributors/unb-mds/2026-2-UnB_Core)](https://img.shields.io/github/contributors/unb-mds/2026-2-UnB_Core)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/unb-mds/2026-2-UnB_Core)](https://img.shields.io/github/stars/unb-mds/2026-2-UnB_Core)
 
Plataforma acadêmica colaborativa da Universidade de Brasília (UnB), com conteúdos organizados por curso e disciplina e contribuições submetidas à moderação.

- **Acesse o site:** https://unb-core.vercel.app
- **Documentação da API:** https://two026-2-unb-core.onrender.com/docs

> A API está no plano gratuito do Render e dorme depois de 15 minutos sem acesso. No primeiro acesso, o site pode levar cerca de 1 minuto para carregar os dados.
 
1. **Base de conhecimento acadêmica** com resumos, dicas, dificuldades, implementações e links, com filtros por curso, disciplina e tipo de conteúdo.
2. **Contribuições moderadas** enviadas por usuários autenticados e revisadas por moderadores ou administradores, que aprovam, pedem ajustes ou rejeitam. O autor acompanha cada envio, edita e pode pedir a exclusão.
3. **Gestão de usuários** para a equipe, com perfis de usuário, moderador e administrador, e recuperação de senha pela tela de login.
4. **Perfil do usuário**, onde cada pessoa edita o próprio nome, e-mail e senha.
##
<img width="1646" height="599" alt="image" src="https://github.com/user-attachments/assets/ea69e958-ca90-454b-bbb2-9ac69f06b856" />

<img width="1383" height="496" alt="image" src="https://github.com/user-attachments/assets/c9d45efb-11a3-4b14-bc86-4ad115111890" />


Projeto desenvolvido para a disciplina de **Métodos de Desenvolvimento de Software (MDS) - 2026/2**, Universidade de Brasília.

## Status do projeto

**Fase atual: publicado para a apresentação de 25/11/2026.** O site está no ar em https://unb-core.vercel.app, com o front no Vercel, a API no Render e o banco no Neon (veja o [guia de publicação](https://unb-mds.github.io/2026-2-UnB_Core/publicacao/)).

- **Backend:** API em FastAPI com autenticação, cadastro, perfil, contribuições, moderação, gestão de usuários e recuperação de senha. Os cursos e as disciplinas de graduação da UnB vêm de um crawler do SIGAA público.
- **Frontend:** React com tema claro e escuro, cores e ícones por tipo de conteúdo e páginas próprias para cada conteúdo e contribuição.
- **Testes:** testes de unidade e de integração do backend (pytest) e testes de componentes do frontend (Vitest e Testing Library).
 

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
- [`docs/documento_de_visao.md`](docs/documento_de_visao.md) Contexto original, evolução do escopo e MVP atual.
- [`specs/001-unb-core`](specs/001-unb-core) Especificação, plano, modelo de dados, contratos da API e tarefas.
- [`docs/ai-usage.md`](docs/ai-usage.md) Declaração do uso de inteligência artificial no projeto.
- [`docs/Sprint`](docs/Sprint) Documentação Geral das Sprints.
- [Como rodar localmente](https://unb-mds.github.io/2026-2-UnB_Core/como-rodar/) - instruções completas para Docker, execução manual, testes e backups.
- Qualidade: [testes do frontend](https://unb-mds.github.io/2026-2-UnB_Core/frontend/testes/), [testes do backend](https://unb-mds.github.io/2026-2-UnB_Core/como-rodar/#testes), [teste de mutação](https://unb-mds.github.io/2026-2-UnB_Core/frontend/testes/#teste-de-mutacao) e [teste de sabotagem](https://unb-mds.github.io/2026-2-UnB_Core/como-rodar/#teste-de-sabotagem).
- [Guia de publicação](https://unb-mds.github.io/2026-2-UnB_Core/publicacao/) - configuração do Neon, Render e Vercel.
- `GitPage UNB Core:` https://unb-mds.github.io/2026-2-UnB_Core/
- `Board no Miro com Documentações Gerais:` https://miro.com/app/board/uXjVHkk8Wek=/?share_link_id=144842983750
- `Figma Storymap:` https://www.figma.com/board/qmgPv7RFMwdFjr0kqOzTag/Welcome-to-FigJam?node-id=1-2&t=QFJpQxSbXNEcukDx-1
- `Figma do Protótipo de Alta Fidelidade (Frontend):` https://www.figma.com/site/wV4UDTWGMPOiqpO7Ik9ErA/UnB_Core?node-id=23-665&t=vpy0So2nUZVnKKSz-1

## Stack
 
- **Back-end**: Python (FastAPI)
- **Front-end**: JavaScript (React)
- **Banco de dados**: PostgreSQL, com migrations Alembic
- **Dados acadêmicos**: cursos e disciplinas de graduação da UnB, coletados do SIGAA público
- **Testes**: pytest (backend), Vitest e Testing Library (frontend)
- **Publicação**: Vercel (site), Render (API) e Neon (banco)
 
## Como rodar localmente

Para instruções detalhadas de execução e solução de problemas, consulte o
[guia de execução local no GitHub Pages](https://unb-mds.github.io/2026-2-UnB_Core/como-rodar/).

### Docker

Pré-requisitos:

- Docker Desktop instalado e em execução.
- PowerShell aberto na raiz do repositório.
- Porta 5432 livre. Se o PostgreSQL também estiver instalado no Windows, ele já
  usa essa porta e o banco do Docker não sobe: pare o serviço do PostgreSQL
  (`Stop-Service postgresql-x64-18`, como administrador) ou rode o projeto sem
  Docker, pelas seções [Backend](#backend) e [Frontend](#frontend).

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



## Contribuindo
 
Consulte o [Guia de Contribuição](https://github.com/unb-mds/2026-2-UnB_Core/blob/main/CONTRIBUTING.md) do grupo antes de abrir uma Pull Request. Issues e o quadro de tarefas do projeto refletem o progresso das sprints.
 
## Licença

Este projeto está licenciado sob os termos da licença MIT.
- [`LICENSE`](LICENSE) - Veja este arquivo para o texto completo.
