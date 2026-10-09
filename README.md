# UNB CORE
 
Plataforma que centraliza informações acadêmicas e institucionais da Universidade de Brasília (UnB), combinando duas frentes:
 
1. **Base de conhecimento colaborativa** resumos, dicas, dificuldades comuns e materiais organizados por curso e disciplina.
2. **Central de editais e avisos** publicações oficiais da UnB reunidas em um só lugar, com transparência sobre origem e data de atualização.
Projeto desenvolvido para a disciplina de **Métodos de Desenvolvimento de Software (MDS) - 2026/2**, Universidade de Brasília.

## Status do projeto

**Fase atual: documentação e planejamento.** Ainda não há implementação. O repositório contém a especificação de requisitos, a organização do backend (spec-kit) e os documentos de sprint.
 

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
      <a href="https://github.com/Brenohrr">
        <img style="border-radius: 50%;" src="https://github.com/Brenohrr.png" width="150px" alt="Breno Henrique da Rocha Rodrigues"/><br />
        <sub><b>Breno Henrique da Rocha Rodrigues</b></sub>
      </a>
      <br />
      <sub>Matrícula: 222006599</sub><br />
      <sub>Função: <i>Backend Dev</i></sub>
    </td>
    
</tr>
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

## Stack planejada
 
- **Back-end**: Python (FastAPI)
- **Front-end**: JavaScript (React)
- **Banco de dados**: SQLite 
 
## Como rodar localmente

### Backend

Os comandos abaixo devem ser executados no terminal integrado do VS Code ou no
PowerShell, a partir da raiz do repositório:

```powershell
cd C:\Users\Pichau\PycharmProjects\G1-2026-2

# Execute uma vez, caso o ambiente virtual ainda não exista
py -m venv .venv

# Ative o ambiente virtual nesta janela
.\.venv\Scripts\Activate.ps1

# Instale as dependências disponíveis no projeto
python -m pip install -r backend\requirements.txt
```

Usando PostgreSQL. Configure as variáveis obrigatórias na mesma janela do PowerShell:

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://USUARIO:SENHA@localhost:5432/NOME_DO_BANCO"
$env:JWT_SECRET_KEY = "dev-only-change-this-secret"
```





```powershell
python -m uvicorn backend.app.api.schema:app --reload
```

Abra a documentação interativa do FastAPI no navegador:

```text
http://127.0.0.1:8000/docs
```

No Swagger UI:

1. Execute `POST /usuario/cadastro` para criar um usuário.
2. Execute `POST /usuario/login` com o mesmo e-mail e senha.
3. Copie o valor de `access_token` da resposta.
4. Clique em **Authorize**, informe `Bearer <access_token>` e confirme.
5. Execute `GET /usuario/me` para testar uma rota autenticada.

O usuário precisa estar ativo para acessar `/usuario/me`. No cadastro atual,
envie `"ativo": true` no corpo da requisição. Para parar o servidor, pressione
`Ctrl+C` no terminal.
 
## Contribuindo
 
Consulte o guia de contribuição do grupo (em construção) antes de abrir uma Pull Request. Issues e o quadro de tarefas do projeto refletem o progresso das sprints.
 
## Licença

Este projeto está licenciado sob os termos da licença MIT.
- [`LICENSE`](LICENSE) Veja este arquivo para o texto completo.
