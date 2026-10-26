# API Contract: UNB CORE

Base path: `/api/v1`  
Formato: JSON  
Datas: ISO 8601

## Publicações institucionais

### `GET /publicacoes`

Lista publicações para consulta pública.

Query parameters opcionais: `termo`, `categoria`, `unidade` e `estado`.

Resposta `200`:

```json
{
  "itens": [
    {
      "id": 1,
      "titulo": "Edital de exemplo",
      "resumo": "Resumo da publicação",
      "categoria": "edital",
      "unidade_responsavel": "Unidade da UnB",
      "url_oficial": "https://exemplo.unb.br/edital",
      "estado": "ativa",
      "prazo_fim": "2026-12-20T23:59:00Z"
    }
  ]
}
```

### `GET /publicacoes/{id}`

Retorna detalhes, `url_oficial`, estado quando disponível e aviso de que a fonte oficial prevalece em caso de divergência.

### `POST /publicacoes`

Cria um edital manualmente. Requer perfil `administrador` e `url_oficial`.

## Base acadêmica

### `GET /cursos/{curso_id}/disciplinas`

Lista disciplinas ativas de um curso.

### `GET /disciplinas/{disciplina_id}/conteudos`

Lista conteúdos publicados de uma disciplina. Pode receber `tipo` como filtro.

### `GET /search`

Busca conteúdos acadêmicos publicados. A integração com editais fica fora da Release 2:

```json
{
  "conteudos_academicos": []
}
```

## Autenticação

### `POST /auth/cadastro`

Cria a própria conta do estudante com nome, e-mail único e senha.

### `POST /auth/login`

Autentica o usuário e retorna a sessão ou token de acesso. Senhas não aparecem em respostas ou erros.

## Contribuições

### `POST /contribuicoes`

Cria uma contribuição para o usuário autenticado. O estado inicial é sempre `pendente`.

### `GET /contribuicoes/minhas`

Lista as contribuições do usuário autenticado com estado e justificativa de moderação, quando houver.

Uma contribuição sem `conteudo_id` representa criação de conteúdo; com `conteudo_id`, representa alteração.

### `POST /moderacao/contribuicoes/{id}/decisao`

Registra uma decisão de moderador. Corpo esperado:

```json
{
  "decisao": "aprovar",
  "justificativa": "Conteúdo revisado e adequado."
}
```

Decisões aceitas: `aprovar`, `ajustes`, `rejeitar`, `arquivar`.

## Relatos acadêmicos

Relatos sobre conteúdos acadêmicos não fazem parte das rotas institucionais de editais.
Quando implementados, exigirão autenticação, tipo e descrição e serão restritos à análise
de moderadores e administradores.

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
