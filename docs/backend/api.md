# Backend: rotas da API

A API usa o prefixo `/api/v1`. As rotas abaixo são implementadas nos módulos
`backend/app/api/routers/` e registradas pelo agregador
`backend/app/api/router.py`.

Em desenvolvimento, a documentação interativa do FastAPI fica em
<http://127.0.0.1:8000/docs>. Na publicação, use
<https://two026-2-unb-core.onrender.com/docs>.

## Autenticação e permissões

Rotas protegidas recebem o token de acesso no cabeçalho:

```http
Authorization: Bearer <access_token>
```

- **Públicas:** consulta acadêmica, cadastro, login e pedido de recuperação de
  senha.
- **Usuário autenticado:** rotas `/auth/me` e `/contribuicoes`.
- **Moderador ou administrador:** rotas de moderação e gestão de contas
  disponíveis para a equipe. Moderadores só gerenciam contas de usuários
  comuns.
- **Somente administrador:** operações administrativas de usuários, como
  cadastro de contas da equipe, alteração de perfil e definição de senha
  temporária.

## Consulta acadêmica

Módulo: `backend/app/api/routers/academico.py`. Todas as rotas desta seção são
públicas e somente consultam cursos, disciplinas e conteúdos publicados.

| Método | Caminho | Descrição |
|---|---|---|
| `GET` | `/api/v1/cursos` | Lista os cursos ativos. Retorna `{ "itens": [...] }`. |
| `GET` | `/api/v1/cursos/{curso_id}/disciplinas` | Lista disciplinas ativas do curso. Retorna `404` se o curso não existir. |
| `GET` | `/api/v1/disciplinas?busca={termo}&limite=20` | Busca disciplinas por código ou nome. `busca` tem de 2 a 100 caracteres; `limite` aceita de 1 a 50. |
| `GET` | `/api/v1/disciplinas/{disciplina_id}/conteudos?tipo={tipo}` | Lista conteúdos publicados da disciplina; `tipo` é opcional. Retorna `404` se a disciplina não existir. |
| `GET` | `/api/v1/conteudos` | Lista conteúdos publicados com filtros e paginação. |
| `GET` | `/api/v1/conteudos/{conteudo_id}` | Retorna um conteúdo publicado. |

Em `/api/v1/conteudos`, os filtros opcionais são `tipo`, `curso_id` e
`disciplina_id`. `ordem` aceita `recentes` (padrão), `antigos` ou `titulo`;
`limite` tem padrão 6 e aceita de 1 a 50; `pagina` começa em 1. A resposta
contém `itens` e `total` de resultados correspondentes aos filtros.

Tipos de conteúdo aceitos: `resumo`, `dica`, `dificuldade`, `prova`,
`implementacao` e `link`.

## Autenticação e perfil

Módulo: `backend/app/api/routers/auth.py`.

| Método | Caminho | Acesso | Descrição |
|---|---|---|---|
| `POST` | `/api/v1/auth/cadastro` | Público | Cria uma conta; retorna `201`. |
| `POST` | `/api/v1/auth/login` | Público | Autentica e retorna token Bearer e dados públicos da conta. |
| `GET` | `/api/v1/auth/me` | Autenticado | Retorna o perfil da conta atual. |
| `PATCH` | `/api/v1/auth/me` | Autenticado | Atualiza nome, e-mail ou senha da conta atual. |
| `POST` | `/api/v1/auth/recuperar-senha` | Público | Registra um pedido de recuperação; retorna `202`. |

Campos principais:

- Cadastro: `nome` (1–120 caracteres), `email` e `senha` (8–128 caracteres).
- Login: `email` e `senha`.
- Atualização de perfil: campos opcionais `nome`, `email`, `senha_atual` e
  `nova_senha`. A senha atual é validada quando for necessário trocar a senha.
- Recuperação: `email` e `contato` opcional.

## Contribuições

Módulo: `backend/app/api/routers/contribuicoes.py`. Todas as rotas exigem uma
conta autenticada e operam sobre as contribuições da própria pessoa.

| Método | Caminho | Descrição |
|---|---|---|
| `POST` | `/api/v1/contribuicoes` | Envia contribuição para revisão; retorna `201`. |
| `GET` | `/api/v1/contribuicoes/minhas` | Lista as contribuições da pessoa autenticada. |
| `GET` | `/api/v1/contribuicoes/minhas/{id_contribuicao}` | Consulta uma contribuição própria. |
| `PATCH` | `/api/v1/contribuicoes/minhas/{id_contribuicao}` | Edita uma contribuição própria e a devolve ao estado pendente para revisão. |
| `DELETE` | `/api/v1/contribuicoes/minhas/{id_contribuicao}` | Exclui uma contribuição própria ainda não publicada; retorna `204`. |
| `POST` | `/api/v1/contribuicoes/minhas/{id_contribuicao}/pedido-exclusao` | Solicita a exclusão de contribuição já publicada. |
| `DELETE` | `/api/v1/contribuicoes/minhas/{id_contribuicao}/pedido-exclusao` | Cancela o pedido de exclusão. |

Campos principais para enviar uma contribuição: `disciplina_id`, `tipo`,
`titulo`, `corpo_ou_url`, `conteudo_id` opcional e `origem` opcional. O pedido
de exclusão recebe `motivo` com 5 a 500 caracteres. Contribuições já publicadas
devem passar pela solicitação de exclusão para revisão da equipe.

## Moderação

Módulo: `backend/app/api/routers/moderacao.py`. Todas as rotas exigem perfil de
moderador ou administrador.

| Método | Caminho | Descrição |
|---|---|---|
| `GET` | `/api/v1/moderacao/contribuicoes?filtro=revisar` | Lista contribuições para revisão. `filtro` aceita `revisar` (padrão), `exclusao` ou `todas`. |
| `GET` | `/api/v1/moderacao/contribuicoes/{contribuicao_id}` | Consulta uma contribuição para moderação. |
| `POST` | `/api/v1/moderacao/contribuicoes/{contribuicao_id}/decisao` | Aprova, solicita ajustes, rejeita ou arquiva uma contribuição. |
| `DELETE` | `/api/v1/moderacao/contribuicoes/{contribuicao_id}` | Exclui a contribuição e, se existir, o conteúdo publicado associado; retorna `204`. |
| `POST` | `/api/v1/moderacao/contribuicoes/{contribuicao_id}/recusar-exclusao` | Recusa o pedido de exclusão e mantém o conteúdo publicado. |

O corpo da decisão contém `decisao` (`aprovar`, `ajustes`, `rejeitar` ou
`arquivar`) e `justificativa` opcional. Ao solicitar ajustes, a justificativa é
obrigatória. Para recusar um pedido de exclusão, `justificativa` é obrigatória
e deve ter de 5 a 2000 caracteres.

## Usuários

Módulo: `backend/app/api/routers/usuarios.py`.

| Método | Caminho | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/usuarios` | Administrador | Lista contas para administração. |
| `POST` | `/api/v1/usuarios` | Administrador | Cria uma conta; retorna `201`. |
| `PATCH` | `/api/v1/usuarios/{usuario_id}` | Administrador | Altera perfil e/ou situação ativa da conta. |
| `GET` | `/api/v1/usuarios/gestao` | Moderador ou administrador | Busca contas para gestão, com filtros opcionais. |
| `PATCH` | `/api/v1/usuarios/{usuario_id}/situacao` | Moderador ou administrador | Ativa ou desativa uma conta. |
| `DELETE` | `/api/v1/usuarios/{usuario_id}` | Moderador ou administrador | Exclui a conta; conteúdos publicados permanecem com autoria removida. Retorna `204`. |
| `POST` | `/api/v1/usuarios/{usuario_id}/senha-temporaria` | Administrador | Define uma nova senha temporária. |

Na gestão de contas, os filtros opcionais são `busca`, `perfil` (`usuario`,
`moderador`, `administrador` ou `equipe`), `ativo` e `recuperacao`. Moderadores
veem e gerenciam apenas contas comuns; o e-mail só é incluído na resposta para
administradores. Senhas nunca são retornadas pela API.

## Schemas e modelo de dados

Os schemas de entrada e saída estão documentados em [Schemas da API](schemas.md).
As tabelas e suas relações estão em [Modelo de dados e relações](banco-de-dados.md).

## Lançamento e tratamento de erros no FastAPI

Erros de domínio são lançados pelos serviços usando as exceções definidas em
`backend/app/api/errors.py`. Por exemplo:

```python
from backend.app.api.errors import NaoEncontrado

raise NaoEncontrado("O curso não foi encontrado.")
```

O módulo define `ErroValidacao`, `NaoEncontrado`, `NaoAutenticado`,
`PermissaoNegada` e `FonteIndisponivel`, com seus códigos e status HTTP. O
FastAPI registra os handlers por meio de `configurar_tratamento_de_erros` em
`backend/app/main.py`. Esses handlers também normalizam `RequestValidationError`
e `HTTPException`.

As respostas seguem este formato:

```json
{
  "erro": {
    "codigo": "NAO_ENCONTRADO",
    "mensagem": "O curso não foi encontrado.",
    "id": "identificador-único"
  }
}
```

O identificador também é retornado no cabeçalho `X-Error-ID`. Códigos e status
principais:

| Código | HTTP | Uso |
|---|---:|---|
| `VALIDACAO` | 422 | Dados inválidos ou regra de negócio não atendida. |
| `NAO_ENCONTRADO` | 404 | Recurso inexistente. |
| `NAO_AUTENTICADO` | 401 | Token ausente, inválido ou conta inativa. |
| `PERMISSAO_NEGADA` | 403 | Perfil sem permissão para a operação. |
| `FONTE_INDISPONIVEL` | 503 | Fonte externa temporariamente indisponível. |
| `ERRO_INTERNO` | 500 | Erro inesperado no servidor. |

Erros de validação de entrada retornam mensagem genérica e não ecoam valores
recebidos, protegendo dados como senhas. Exceções inesperadas são registradas
com o identificador e o tipo da exceção, sem incluir sua mensagem na resposta
ao cliente; o cliente recebe uma mensagem genérica de erro interno.
