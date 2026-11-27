# Frontend: aplicação e arquitetura

O frontend é uma aplicação React criada com Vite. O ponto de entrada
`frontend/src/main.jsx` inicializa o tema e monta `App`; as telas, componentes,
estado de sessão e chamadas HTTP ficam separados por responsabilidade em
`frontend/src/`.

## Telas e rotas

A navegação é implementada em `frontend/src/App.jsx` usando a History API do
navegador (`pushState` e `popstate`), sem uma biblioteca externa de roteamento.

| Caminho | Tela | Finalidade |
|---|---|---|
| `/` | `HomePage` | Apresenta a base, busca disciplinas e mostra conteúdos recentes. |
| `/base-de-conhecimentos` | `ConhecimentoPage` | Pesquisa e filtra conteúdos publicados. |
| `/conteudos/{id}` | `ConteudoPage` | Exibe os detalhes de um conteúdo. |
| `/cadastro` | `CadastroPage` | Cria uma conta. |
| `/login` | `LoginPage` | Autentica e permite solicitar recuperação de senha. |
| `/contribuicao` | `ContribuicaoPage` | Envia uma contribuição para revisão. |
| `/guia-de-contribuicao` | `GuiaContribuicaoPage` | Explica orientações para contribuir. |
| `/minhas-contribuicoes` | `MinhasContribuicoesPage` | Lista os envios da conta atual. |
| `/minhas-contribuicoes/{id}` | `MinhaContribuicaoPage` | Consulta, edita ou solicita a exclusão de um envio próprio. |
| `/moderacao` | `ModeracaoPage` | Lista contribuições para revisão. |
| `/moderacao/contribuicoes/{id}` | `ModeracaoContribuicaoPage` | Consulta e decide uma contribuição na moderação. |
| `/perfil` | `PerfilPage` | Edita o perfil da pessoa autenticada. |
| `/admin/usuarios` | `AdminUsuariosPage` | Gerencia contas conforme o perfil autorizado. |

O fallback de rota desconhecida abre a base de conhecimentos. A página inicial
pode passar a disciplina selecionada para a base pela propriedade `state` do
histórico do navegador.

## Estrutura do código

- `src/pages/`: telas compostas por fluxo ou rota.
- `src/components/`: elementos reaproveitáveis, agrupados por área (`auth`,
  `conteudos`, `contribuicoes`, `layout`, `moderacao` e `ui`).
- `src/services/api.js`: cliente HTTP e tratamento padronizado de respostas.
- `src/services/cursos.js`: normaliza a lista de cursos recebida pela interface.
- `src/state/auth.js`: estado compartilhado de autenticação.
- `src/state/theme.js`: estado e inicialização de tema claro/escuro.
- `src/index.css` e CSS por componente ou página: tokens globais e estilos
  específicos.

`PageLayout` compartilha cabeçalho, rodapé, largura de conteúdo e estrutura das
páginas internas. A home usa o cabeçalho e o rodapé diretamente por ter
composição visual própria.

## Integração com a API

O cliente HTTP usa `VITE_API_URL` como endereço base e, se a variável não
existir, usa `http://127.0.0.1:8000/api/v1`. As funções `api.get`, `api.post`,
`api.patch` e `api.delete` enviam e recebem JSON; quando existe token, o cliente
adiciona `Authorization: Bearer <token>`.

Exemplo de configuração local no PowerShell:

```powershell
$env:VITE_API_URL = "http://127.0.0.1:8000/api/v1"
```

Uma resposta HTTP de erro vira `ApiError`, com mensagem, código, status e
identificador quando disponíveis. Se uma requisição falha por falta de
conexão, o cliente reporta que não foi possível conectar. Requisições
canceladas por troca de tela não são tratadas como falha de conexão.

Quando a API responde `401` para uma requisição que enviou token, o cliente
limpa a sessão, emite o evento de sessão expirada e as telas atualizam o estado
de autenticação. O cliente também mantém `AbortController` em consultas de
telas que podem ser desmontadas ou atualizadas antes da resposta.

As rotas, permissões e respostas da API estão em [Rotas do backend](../backend/api.md).

## Sessão e tema

- A sessão recebida no login é armazenada em `localStorage` sob a chave
  `unb-core-session`.
- Na inicialização, o estado de autenticação verifica o campo `exp` do JWT e
  descarta tokens expirados. A API continua sendo a autoridade final para
  autenticar cada requisição.
- O estado de sessão é compartilhado entre componentes por
  `useSyncExternalStore`.
- O tema escolhido é guardado em `localStorage` sob `unb-core-tema`. Se não
  houver escolha salva, a interface segue a preferência do sistema operacional.
- O tema ativo fica no atributo `data-theme` do elemento `<html>`; os estilos
  leem os tokens CSS correspondentes.

## Componentes compartilhados

- `SiteHeader`, `Navigation` e `SiteFooter`: estrutura de navegação do site.
- `PageLayout`: estrutura comum às telas internas.
- `DisciplinaBusca`: busca de disciplina por nome ou código.
- `ConteudoCard`, `ConteudoDetalhe`, `ConteudoCorpo` e `TipoBadge`: apresentação
  de materiais acadêmicos.
- `Button`, `SearchInput`, `EmptyState`, `StatusBadge` e `ErrorMessage`:
  elementos de interface compartilhados. `ErrorMessage` usa `role="alert"` para
  expor erros às tecnologias assistivas.
- `DecisaoModal` e `JustificativaInput`: controles do fluxo de moderação.

Detalhes de cores, tipografia, tema e outros tokens estão em
[Design system](design-system.md). Para instalar e executar o frontend, veja
[Como rodar o projeto](../como-rodar.md).
