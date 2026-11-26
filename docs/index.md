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

- [`docs/requisitos.md`](docs/requisitos.md) - visão geral, requisitos funcionais e não funcionais, entidades e critérios de sucesso.
- [`docs/backend`](docs/backend) - documentação das sprints do backend.
- [`docs/frontend`](docs/frontend) - documentação das sprints do frontend.
- [`docs/documento_de_visao.md`](docs/documento_de_visao.md) - documento de visão.
- [Backups e restauração](https://unb-mds.github.io/2026-2-UnB_Core/backups/) - procedimentos de backup e recuperação do banco.
- `Board no Miro com Documentações Gerais:` https://miro.com/app/board/uXjVHkk8Wek=/?share_link_id=144842983750
- `Figma Storymap:` https://www.figma.com/board/qmgPv7RFMwdFjr0kqOzTag/Welcome-to-FigJam?node-id=1-2&t=QFJpQxSbXNEcukDx-1
- `Figma do Protótipo de Alta Fidelidade (Frontend):` https://www.figma.com/site/wV4UDTWGMPOiqpO7Ik9ErA/UnB_Core?node-id=23-665&t=vpy0So2nUZVnKKSz-1

## Stack

- **Back-end**: Python (FastAPI)
- **Front-end**: JavaScript (React)
- **Banco de dados**: PostgreSQL, com migrations Alembic
- **Dados acadêmicos**: cursos e disciplinas coletados do SIGAA público (campus do Gama, FCTE)

## Como rodar

As instruções completas estão no GitHub Pages:

**[Como rodar o projeto](https://unb-mds.github.io/2026-2-UnB_Core/como-rodar/)**

## Contribuindo

Consulte o guia de contribuição do grupo (em construção) antes de abrir uma Pull Request. Issues e o quadro de tarefas do projeto refletem o progresso das sprints.

## Licença

Este projeto está licenciado sob os termos da licença MIT.

- [`LICENSE`](LICENSE) - texto completo da licença.
