# Data Model: UNB CORE

## Usuário

Representa uma pessoa que consulta conteúdos ou envia contribuições.

- `id`: identificador único.
- `nome`: nome exibido.
- `email`: endereço único usado no acesso.
- `senha_hash`: senha armazenada de forma protegida; nunca deve ser retornada.
- `perfil`: `usuario`, `moderador` ou `administrador`.
- `ativo`: indica se a conta pode acessar funções autenticadas.
- `criado_em`, `atualizado_em`: datas de controle.

Regras:

- O e-mail deve ser único.
- Qualquer usuário ativo e autenticado pode enviar contribuições.
- Moderadores e administradores podem decidir sobre contribuições.
- Apenas administradores podem criar usuários com perfil administrativo.
- Usuários administrativos podem ser preparados por seed ou cadastro inicial no banco.

## Curso

Agrupa disciplinas e organiza a consulta da Base de Conhecimento.

- `id`: identificador único.
- `nome`: nome do curso.
- `sigla`: sigla do curso.
- `ativo`: indica disponibilidade para consulta.

## Disciplina

Unidade curricular pertencente a um curso.

- `id`: identificador único.
- `curso_id`: referência ao curso.
- `codigo`: código da disciplina.
- `nome`: nome da disciplina.
- `periodo`: período ou semestre relacionado, quando aplicável.
- `ativo`: indica disponibilidade para consulta.

Relacionamento: um curso possui muitas disciplinas; cada disciplina pertence a um curso.

## Conteúdo acadêmico

Material publicado na Base de Conhecimento.

- `id`: identificador único.
- `disciplina_id`: disciplina relacionada.
- `tipo`: `resumo`, `dica`, `dificuldade`, `prova`, `implementacao` ou `link`.
- `titulo`: título do conteúdo.
- `corpo_ou_url`: texto ou endereço do material.
- `autor_id`: usuário responsável pela publicação.
- `origem`: fonte ou explicação de autoria, quando informada.
- `estado`: `publicado` ou `arquivado`.
- `criado_em`, `atualizado_em`: datas de controle.

Regras:

- Apenas conteúdos publicados aparecem na consulta pública.
- Usuários não podem publicar ou alterar conteúdos diretamente.
- A publicação ou atualização ocorre por aprovação de uma contribuição.

## Contribuição

Proposta de criação ou alteração de conteúdo acadêmico.

- `id`: identificador único.
- `autor_id`: usuário autenticado que enviou a proposta.
- `conteudo_id`: conteúdo relacionado quando a proposta for uma alteração; nulo quando for criação.
- `disciplina_id`: disciplina da proposta.
- `tipo`: tipo de conteúdo proposto.
- `titulo`: título proposto.
- `corpo_ou_url`: texto ou endereço proposto.
- `origem`: fonte ou explicação de autoria, quando informada.
- `estado`: `pendente`, `ajustes`, `rejeitada`, `aprovada` ou `arquivada`.
- `justificativa_moderacao`: justificativa opcional da decisão.
- `criado_em`, `atualizado_em`: datas de controle.

Transições:

```text
pendente -> aprovada
pendente -> ajustes
pendente -> rejeitada
pendente -> arquivada
ajustes -> pendente
```

Uma contribuição aprovada sem `conteudo_id` cria um conteúdo publicado. Uma contribuição aprovada com `conteudo_id` atualiza o conteúdo correspondente.

## Relacionamentos principais

- `Curso 1:N Disciplina`.
- `Disciplina 1:N Conteúdo acadêmico`.
- `Usuário 1:N Conteúdo acadêmico`.
- `Usuário 1:N Contribuição`.
- `Disciplina 1:N Contribuição`.
- `Conteúdo acadêmico 1:N Contribuição` quando a contribuição representa alteração.
