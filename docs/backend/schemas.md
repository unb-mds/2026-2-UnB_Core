# Schemas da API

Os schemas ficam em `backend/app/api/schemas/`. São modelos Pydantic usados
para validar os dados recebidos e definir os campos serializados nas respostas.
Não são tabelas do banco; os modelos SQLModel estão em
`backend/app/domain/models.py`. Consulte também as [rotas da API](api.md).

## Acadêmico — `schemas/academico.py`

| Schema | Campos |
|---|---|
| `CursoPublico` | `id`, `nome`, `sigla`, `grau` |
| `DisciplinaPublica` | `id`, `curso_id` (lista de IDs), `codigo`, `nome`, `periodo` opcional |
| `ConteudoPublico` | `id`, `disciplina_id`, `tipo`, `titulo`, `corpo_ou_url`, `autor_id`, `origem` opcional, `atualizado_em`; também pode trazer `disciplina_codigo`, `disciplina_nome` e `autor_nome`. |
| `ListaResposta[T]` | `itens`: lista de resultados. |
| `ListaPaginada[T]` | `itens`: resultados da página; `total`: quantidade que atende aos filtros. |

`DisciplinaPublica.curso_id` é uma lista porque uma disciplina pode pertencer a
mais de um curso. A relação é explicada no [modelo de dados](banco-de-dados.md).

## Autenticação — `schemas/auth.py`

| Schema | Campos e validações |
|---|---|
| `CadastroRequest` | `nome` (1–120 caracteres), `email` válido e `senha` (8–128 caracteres). |
| `LoginRequest` | `email` válido e `senha` (1–128 caracteres). |
| `PerfilAtualizacao` | Campos opcionais `nome`, `email`, `senha_atual` e `nova_senha`; nova senha de 8–128 caracteres. |
| `PedidoRecuperacaoSenha` | `email` válido e `contato` opcional (até 300 caracteres). |
| `UsuarioPublico` | `id`, `nome`, `email`, `perfil` e `ativo`; não expõe hash ou senha. |
| `TokenResponse` | `access_token`, `token_type`, `usuario` público e `trocar_senha`. |
| `RespostaRecuperacaoSenha` | `mensagem` de confirmação do pedido. |

## Contribuições — `schemas/contribuicao.py`

| Schema | Campos e validações |
|---|---|
| `ContribuicaoCriacao` | `disciplina_id`, `tipo`, `titulo` (1–200 caracteres), `corpo_ou_url`; `conteudo_id` e `origem` são opcionais. |
| `ContribuicaoUpdate` | Campos opcionais `tipo`, `titulo`, `corpo_ou_url` e `origem`; somente os campos enviados são atualizados. |
| `PedidoExclusao` | `motivo` de 5–500 caracteres. |
| `ContribuicaoPublica` | IDs da contribuição, autor, disciplina e conteúdo opcional; dados propostos, estado, justificativa de moderação, datas e metadados do pedido de exclusão. Pode incluir código e nome da disciplina. |

`tipo` aceita `resumo`, `dica`, `dificuldade`, `prova`, `implementacao` ou
`link`. O estado pode ser `pendente`, `ajustes`, `rejeitada`, `aprovada` ou
`arquivada`.

## Moderação — `schemas/moderacao.py`

| Schema | Campos e validações |
|---|---|
| `DecisaoRequest` | `decisao` (`aprovar`, `ajustes`, `rejeitar` ou `arquivar`) e `justificativa` opcional, até 2000 caracteres. O serviço exige justificativa para `ajustes`. |
| `FiltroModeracao` | `revisar`, `exclusao` ou `todas`. |
| `RecusaExclusao` | `justificativa` de 5–2000 caracteres. |
| `ContribuicaoModeracao` | Dados da contribuição, estado, justificativa, datas, pedido de exclusão e nomes do autor e da disciplina. |

## Usuários — `schemas/usuarios.py`

| Schema | Campos e validações |
|---|---|
| `UsuarioAdminCriacao` | `nome` (1–120 caracteres), `email`, `senha` (8–128 caracteres) e `perfil` opcional, padrão `usuario`. |
| `UsuarioAdminAtualizacao` | `perfil` e `ativo`, ambos opcionais; a operação exige ao menos um deles. |
| `SituacaoUsuario` | `ativo` (booleano). |
| `SenhaTemporaria` | `nova_senha` de 8–128 caracteres. |
| `UsuarioAdminPublico` | ID, nome, e-mail, perfil, estado ativo e datas; não inclui senha. |
| `UsuarioGestao` | ID, nome, e-mail, perfil, estado, data de criação, total de contribuições e dados de recuperação. E-mail e dados de recuperação são ocultados para moderadores. |

## Uso nas rotas

Cada rota declara seu schema de entrada como parâmetro e sua resposta com
`response_model`. O FastAPI valida o corpo da requisição antes de executar a
operação e serializa a resposta no formato definido. O tratamento padronizado
de erros de validação está descrito no final da página de [rotas da API](api.md).
