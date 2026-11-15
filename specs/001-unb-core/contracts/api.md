# API Contract: UNB CORE

Base path: `/api/v1`  
Formato: JSON  
Datas: ISO 8601

## Autenticação

### `POST /auth/cadastro`

Cria a própria conta com nome, e-mail único e senha.

### `POST /auth/login`

Autentica o usuário e retorna um token de acesso. Senhas não aparecem em respostas ou erros.

### `GET /auth/me`

Retorna os dados públicos do usuário autenticado.

## Cursos, disciplinas e conteúdos

### `GET /cursos`

Lista cursos para consulta pública. Resposta no formato `{ "itens": [...] }`, com `id`, `nome`, `sigla` e `grau`.

O MVP atende somente o campus do Gama: o cliente exibe apenas os cursos com `sigla` igual a `FCTE`.

### `GET /cursos/{curso_id}/disciplinas`

Lista disciplinas ativas de um curso.

### `GET /disciplinas/{disciplina_id}/conteudos`

Lista conteúdos publicados de uma disciplina. Pode receber `tipo` como filtro.

Tipos aceitos: `resumo`, `dica`, `dificuldade`, `prova`, `implementacao` e `link`.

O `curso_id` é definido pela navegação anterior em `GET /cursos/{curso_id}/disciplinas`; a API deve rejeitar a consulta se a disciplina não pertencer ao curso selecionado no fluxo do cliente.

### `GET /conteudos/{conteudo_id}`

Retorna os detalhes de um conteúdo publicado, incluindo disciplina, tipo, autoria ou origem e data de atualização.

## Contribuições

### `POST /contribuicoes`

Cria uma contribuição para o usuário autenticado. O estado inicial é sempre `pendente`.

Corpo:

```json
{
  "disciplina_id": 1,
  "conteudo_id": null,
  "tipo": "resumo",
  "titulo": "Resumo da unidade 1",
  "corpo_ou_url": "Texto enviado pelo estudante",
  "origem": "Anotações próprias"
}
```

`autor_id` e `estado` são definidos pelo servidor.

### `GET /contribuicoes/minhas`

Lista as contribuições do usuário autenticado com estado e justificativa de moderação (`justificativa_moderacao`). A resposta é uma lista JSON, sem o envelope `itens`.

### `PATCH /contribuicoes/minhas/{id_contribuicao}`

Edita uma contribuição do usuário autenticado. Todos os campos são opcionais; somente os campos enviados são alterados.

Corpo:

```json
{
  "tipo": "resumo",
  "titulo": "Resumo da unidade 1 (revisado)",
  "corpo_ou_url": "Texto revisado pelo estudante",
  "origem": "Anotações próprias"
}
```

Após a edição, o estado volta para `pendente`. Retorna `404` se a contribuição não existir e `422` se ela pertencer a outro usuário.

## Moderação

### `GET /moderacao/contribuicoes`

Lista contribuições pendentes ou em revisão. Requer perfil `moderador` ou `administrador`.

### `POST /moderacao/contribuicoes/{id}/decisao`

Registra uma decisão de moderação. Requer perfil `moderador` ou `administrador`.

Corpo:

```json
{
  "decisao": "aprovar",
  "justificativa": "Conteúdo revisado e adequado."
}
```

Decisões aceitas: `aprovar`, `ajustes`, `rejeitar`, `arquivar`.

Transições aceitas:

- `pendente` -> `aprovada`, `ajustes`, `rejeitada` ou `arquivada`;
- `ajustes` -> `pendente`.

As demais transições devem ser rejeitadas sem alterar a contribuição.

Ao aprovar:

- sem `conteudo_id`: cria um conteúdo publicado;
- com `conteudo_id`: atualiza o conteúdo correspondente.

## Administração de usuários

### `GET /usuarios`

Lista usuários para administração. Requer perfil `administrador`.

### `POST /usuarios`

Cria um usuário com perfil `usuario`, `moderador` ou `administrador`. Requer perfil `administrador`.

### `PATCH /usuarios/{id}`

Atualiza perfil ou estado ativo de um usuário. Requer perfil `administrador`.

O administrador não pode desativar a própria conta nem alterar o próprio perfil para outro diferente de `administrador`; nesses casos a API retorna `422` com o código `VALIDACAO`.

## Erros

Formato comum:

```json
{
  "erro": {
    "codigo": "PERMISSAO_NEGADA",
    "mensagem": "Voce nao possui permissao para executar esta acao.",
    "id": "string"
  }
}
```

Códigos mínimos: `VALIDACAO`, `NAO_ENCONTRADO`, `NAO_AUTENTICADO`, `PERMISSAO_NEGADA` e `ERRO_INTERNO`.
