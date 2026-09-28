---
description: "Tasks de implementação do UNB CORE"
---

# Tasks: UNB CORE

**Input**: Design documents from `/specs/001-unb-core/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Organization**: As tarefas estão agrupadas por história de usuário para permitir implementação incremental e validação independente.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar a estrutura mínima do backend e frontend.

- [ ] T001 Criar a estrutura de diretórios `backend/app/api`, `backend/app/services`, `backend/app/settings`, `backend/tests/contract`, `backend/tests/integration`, `backend/tests/unit`, `frontend/src/components`, `frontend/src/pages`, `frontend/src/services`, `frontend/src/state`, `frontend/tests/integration` e `frontend/tests/unit`.
- [ ] T002 Criar `backend/requirements.txt` com Python, FastAPI, Uvicorn, SQLModel, Pydantic, pytest e httpx.
- [ ] T003 [P] Criar `frontend/package.json` com React, ferramenta de desenvolvimento e cliente HTTP.
- [ ] T004 [P] Criar `backend/app/main.py` com a aplicação FastAPI e o ponto de entrada documentado no `specs/001-unb-core/quickstart.md`.
- [ ] T005 [P] Atualizar `README.md` com os comandos básicos de configuração e execução do backend e frontend.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implementar os componentes compartilhados que bloqueiam as histórias de usuário.

**Checkpoint**: A fundação estará pronta quando a API iniciar com SQLite, os modelos puderem ser persistidos, erros tiverem formato comum e as permissões puderem ser aplicadas às rotas protegidas.

- [ ] T006 Criar `backend/app/settings/config.py` para configuração do ambiente, URL do banco SQLite e chave de sessão/token sem valores sensíveis versionados.
- [ ] T007 Criar `backend/app/settings/database.py` com engine SQLite, criação de tabelas e dependência de sessão SQLModel.
- [ ] T008 [P] Normalizar os modelos compartilhados em `backend/app/domain/model_usuario.py`, `backend/app/domain/model_disciplina.py` e `backend/app/domain/model_SubmissaoBase.py`, corrigindo tipos, imports e estados definidos em `specs/001-unb-core/data-model.md`.
- [ ] T009 [P] Criar ou ajustar `backend/app/domain/model_curso.py` e os modelos de fonte, publicação e denúncia em `backend/app/domain/model_fonte.py`, `backend/app/domain/model_publicacao.py` e `backend/app/domain/model_denuncia.py`.
- [ ] T010 Ajustar `backend/app/domain/model_Contribuicao.py` e `backend/app/domain/model_ConteudoAcademico.py` para representar criação quando `conteudo_id` estiver ausente e alteração quando estiver presente.
- [ ] T011 Criar `backend/app/api/errors.py` com o formato de erro comum, códigos de validação, autenticação, permissão, não encontrado e fonte indisponível.
- [ ] T012 Criar `backend/app/services/auth_service.py` com cadastro, login, hash de senha e emissão/validação de sessão ou token, sem retornar senha.
- [ ] T013 Criar `backend/app/api/dependencies.py` com identificação do usuário atual e verificadores de perfil `moderador` e `administrador`.
- [ ] T014 Criar `backend/app/api/router.py` para registrar as rotas sob `/api/v1` e conectar o router à aplicação em `backend/app/main.py`.
- [X] T015 [P] Criar `frontend/src/services/api.js` com cliente HTTP, tratamento do formato de erro e armazenamento da sessão de acesso.
- [X] T016 [P] Criar `frontend/src/state/auth.js` e componentes base em `frontend/src/components/` para estado de autenticação, mensagens de erro e foco visível.

---

## Phase 3: User Story 1 - Consultar editais e avisos oficiais (Priority: P1) MVP

**Goal**: Permitir que qualquer estudante consulte publicações institucionais cadastradas manualmente e veja sua origem e estado de verificação.

**Independent Test**: Com uma publicação cadastrada, consultar a lista pública, aplicar filtros e abrir detalhes sem autenticação; a origem, estado, prazo e data de verificação devem estar disponíveis.

- [ ] T017 [P] [US1] Criar `backend/app/services/publicacao_service.py` para listar, filtrar e detalhar publicações por termo, categoria, unidade, curso, estado e prazo conforme `specs/001-unb-core/contracts/api.md`.
- [ ] T018 [P] [US1] Criar schemas de entrada e saída em `backend/app/api/schemas/publicacao.py`, exigindo título, resumo, categoria, unidade responsável e fonte oficial para escrita administrativa.
- [ ] T019 [US1] Implementar `GET /api/v1/publicacoes` e `GET /api/v1/publicacoes/{id}` em `backend/app/api/publicacoes.py`, com consulta pública e aviso de prevalência da fonte oficial.
- [ ] T020 [US1] Implementar `GET /api/v1/search` em `backend/app/api/search.py`, separando resultados acadêmicos e institucionais.
- [X] T021 [US1] Implementar a página `frontend/src/pages/PublicacoesPage.jsx` com filtros, estado vazio e mensagens para publicação não verificada ou sem prazo.
- [X] T022 [US1] Implementar `frontend/src/pages/PublicacaoDetalhePage.jsx` e componentes de origem, estado, datas e link oficial em `frontend/src/components/publicacoes/`.
- [X] T023 [US1] Integrar navegação principal entre os dois espaços em `frontend/src/App.jsx` e `frontend/src/components/Navigation.jsx`.

**Checkpoint**: A consulta institucional pública e a busca unificada devem funcionar sem login.

---

## Phase 4: User Story 2 - Consultar conteúdos de uma disciplina (Priority: P1)

**Goal**: Permitir que estudantes encontrem conteúdos acadêmicos publicados por curso, disciplina e tipo.

**Independent Test**: Com curso, disciplina e conteúdo publicados, consultar a Base de Conhecimento, filtrar por tipo e abrir os dados de autoria/origem e atualização sem autenticação.

- [ ] T024 [P] [US2] Criar `backend/app/services/curso_service.py` e `backend/app/services/conteudo_service.py` para cursos, disciplinas e conteúdos publicados.
- [ ] T025 [P] [US2] Criar schemas acadêmicos em `backend/app/api/schemas/academico.py` com tipos permitidos e respostas sem dados de autenticação.
- [ ] T026 [US2] Implementar `GET /api/v1/cursos/{curso_id}/disciplinas` em `backend/app/api/disciplinas.py`.
- [ ] T027 [US2] Implementar `GET /api/v1/disciplinas/{disciplina_id}/conteudos` em `backend/app/api/conteudos.py`, incluindo filtro opcional por tipo.
- [ ] T028 [US2] Integrar conteúdos acadêmicos ao resultado separado de `GET /api/v1/search` em `backend/app/api/search.py`.
- [X] T029 [US2] Implementar `frontend/src/pages/ConhecimentoPage.jsx` com seleção de curso, disciplina e tipo, estado vazio e possibilidade de contribuição.
- [X] T030 [US2] Criar `frontend/src/components/conteudos/ConteudoCard.jsx` e `frontend/src/components/conteudos/ConteudoDetalhe.jsx` com autoria/origem e data de atualização.

**Checkpoint**: A Base de Conhecimento deve ser consultável independentemente da implementação das contribuições.

---

## Phase 5: User Story 3 - Enviar e acompanhar uma contribuição (Priority: P2)

**Goal**: Permitir cadastro, autenticação e envio de contribuições com estado pendente.

**Independent Test**: Criar uma conta, entrar, enviar uma contribuição válida, consultar seu estado e receber mensagens para campos ausentes ou acesso não autenticado.

- [X] T031 [P] [US3] Criar `frontend/src/pages/CadastroPage.jsx` e `frontend/src/pages/LoginPage.jsx` para cadastro com nome, e-mail único e senha.
- [ ] T032 [P] [US3] Criar schemas de autenticação em `backend/app/api/schemas/auth.py` e rotas `POST /api/v1/auth/cadastro` e `POST /api/v1/auth/login` em `backend/app/api/auth.py`.
- [ ] T033 [US3] Criar `backend/app/services/contribuicao_service.py` para validar campos obrigatórios e iniciar contribuições no estado `pendente`.
- [ ] T034 [P] [US3] Criar schemas em `backend/app/api/schemas/contribuicao.py` para diferenciar criação sem `conteudo_id` e alteração com `conteudo_id`.
- [ ] T035 [US3] Implementar `POST /api/v1/contribuicoes` e `GET /api/v1/contribuicoes/minhas` em `backend/app/api/contribuicoes.py`, exigindo usuário autenticado.
- [X] T036 [US3] Implementar `frontend/src/pages/ContribuicaoPage.jsx` com formulário, validação de campos, estado pendente e mensagem de erro orientativa.
- [X] T037 [US3] Implementar `frontend/src/pages/MinhasContribuicoesPage.jsx` para acompanhar estado e justificativa de moderação.

**Checkpoint**: Um usuário autenticado deve conseguir criar e acompanhar contribuição; usuário anônimo deve ser bloqueado.

---

## Phase 6: User Story 4 - Moderar conteúdos e administrar informações (Priority: P2)

**Goal**: Permitir moderação de contribuições e denúncias e administração de publicações, fontes, categorias e disciplinas.

**Independent Test**: Usar perfis moderador, administrador e usuário comum para validar decisões permitidas, bloqueios e cadastro manual de publicação.

- [ ] T038 [P] [US4] Criar `backend/app/services/moderacao_service.py` com transições `pendente -> aprovada/ajustes/rejeitada/arquivada`, justificativa e criação/atualização de conteúdo.
- [ ] T039 [P] [US4] Criar `backend/app/services/denuncia_service.py` com estados de denúncia e associação ao usuário autenticado.
- [ ] T040 [US4] Implementar `POST /api/v1/moderacao/contribuicoes/{id}/decisao` em `backend/app/api/moderacao.py`, restrito a moderador ou administrador.
- [ ] T041 [US4] Implementar `POST /api/v1/publicacoes`, `PATCH /api/v1/publicacoes/{id}`, `GET/POST /api/v1/fontes`, `GET/POST /api/v1/categorias` e `POST/PATCH /api/v1/disciplinas` em `backend/app/api/administracao.py`, restritos a administrador.
- [ ] T042 [US4] Implementar `POST /api/v1/publicacoes/{id}/denuncias`, `GET /api/v1/denuncias` e `PATCH /api/v1/denuncias/{id}` em `backend/app/api/denuncias.py`, aplicando as permissões definidas.
- [ ] T043 [US4] Criar páginas administrativas e de moderação em `frontend/src/pages/AdminPage.jsx` e `frontend/src/pages/ModeracaoPage.jsx`.
- [ ] T044 [US4] Criar componentes de decisão, justificativa e estados em `frontend/src/components/moderacao/` e `frontend/src/components/admin/`.
- [ ] T045 [US4] Integrar formulário de denúncia autenticada em `frontend/src/components/publicacoes/DenunciaForm.jsx`.

**Checkpoint**: Moderadores conseguem analisar contribuições e denúncias; administradores conseguem gerenciar dados institucionais; usuários comuns não executam essas ações.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Consolidar documentação, acessibilidade e validação do MVP.

- [ ] T046 [P] Aplicar nomes acessíveis, foco visível e navegação por teclado nos componentes de `frontend/src/components/` e páginas de `frontend/src/pages/`.
- [ ] T047 [P] Padronizar mensagens de erro com causa e orientação em `backend/app/api/errors.py` e `frontend/src/services/api.js`.
- [ ] T048 [P] Atualizar `specs/001-unb-core/quickstart.md` com os comandos e cenários realmente disponíveis após a implementação.
- [ ] T049 Revisar `docs/requisitos.md` e `README.md` para manter as decisões do MVP, permissões e limites de escopo documentados.
- [ ] T050 Executar os cenários de `specs/001-unb-core/quickstart.md` e registrar pendências de validação em `docs/`.
- [ ] T051 [US3] Criar `frontend/src/pages/GuiaContribuicaoPage.jsx` com orientações sobre qualidade, escopo permitido, autoria e fontes para a primeira contribuição (FR-011).
- [ ] T052 [US1] Adicionar em `backend/app/domain/model_publicacao.py`, `backend/app/api/schemas/publicacao.py` e `frontend/src/components/publicacoes/` o indicador de documento não pesquisável e a orientação para consulta no link oficial (FR-023).
- [ ] T053 [P] Validar em `docs/compatibilidade.md` os navegadores desktop atuais e Chrome/Safari mobile previstos para o MVP, registrando o escopo de compatibilidade (FR-027).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 - Setup**: não depende de outras fases.
- **Phase 2 - Foundational**: depende do Setup e bloqueia as histórias de usuário.
- **Phase 3 - US1**: depende da fundação; é o primeiro incremento do MVP.
- **Phase 4 - US2**: depende da fundação; pode ser desenvolvida em paralelo com US1 depois que a API compartilhada existir.
- **Phase 5 - US3**: depende da fundação e das entidades acadêmicas; pode começar após os modelos base, mas sua integração com a contribuição da US2 deve ocorrer antes do checkpoint.
- **Phase 6 - US4**: depende da autenticação da US3, dos modelos de publicação da US1 e do fluxo de contribuição da US3.
- **Phase 7 - Polish**: depende das histórias que forem incluídas na entrega.

### User Story Dependencies

- **US1 (P1)**: depende somente da Phase 2; entrega a consulta institucional pública.
- **US2 (P1)**: depende somente da Phase 2; entrega a consulta acadêmica pública.
- **US3 (P2)**: depende da Phase 2 e dos modelos acadêmicos; usa o curso e a disciplina da US2.
- **US4 (P2)**: depende de US1 para publicações e de US3 para autenticação/contribuições; também usa entidades compartilhadas.

### Parallel Opportunities

- **Setup**: T003, T004 e T005 podem ser executadas em paralelo após T001/T002 quando necessário.
- **Fundação**: T008, T009, T015 e T016 podem ser executadas em paralelo; T012/T013 dependem da configuração base.
- **US1 e US2**: após a fundação, os serviços e páginas de consulta podem ser desenvolvidos em paralelo por pessoas diferentes.
- **US3**: T031, T032 e T034 podem avançar em paralelo; T035 e T036 dependem dos schemas e do serviço.
- **US4**: T038 e T039 podem avançar em paralelo; T043 e T044 podem avançar em paralelo após os contratos das rotas.
- **Tasks adicionadas**: T051 pode avançar após a estrutura inicial do frontend; T052 depende dos modelos e schemas de US1; T053 pode avançar em paralelo com o polimento.

## Requirement Traceability

Cada requisito funcional e critério de sucesso possui pelo menos uma task relacionada. As tasks T051-T053 cobrem os requisitos que anteriormente não tinham implementação explícita.

| Requirement key | Task IDs |
|---|---|
| FR-001 | T023 |
| FR-002 | T024, T026, T029 |
| FR-003 | T017, T019, T021 |
| FR-004 | T020, T028 |
| FR-005 | T017, T019, T022 |
| FR-006 | T039, T042 |
| FR-007 | T012, T032, T035 |
| FR-008 | T033, T035, T038 |
| FR-009 | T038, T040 |
| FR-010 | T038, T040, T044 |
| FR-011 | T051 |
| FR-012 | T019, T027, T029 |
| FR-013 | T013, T040, T041, T042 |
| FR-014 | T011, T047 |
| FR-015 | T017, T022, T038 |
| FR-016 | T041 |
| FR-017 | T012, T032 |
| FR-018 | T041 |
| FR-019 | T018, T041 |
| FR-020 | T034, T035 |
| FR-021 | T017, T020 |
| FR-022 | T018, T021, T022 |
| FR-023 | T052 |
| FR-024 | T038, T039, T040, T041, T042 |
| FR-025 | T018, T033, T036, T047 |
| FR-026 | T016, T046 |
| FR-027 | T053 |
| FR-028 | T012, T031, T032 |
| FR-029 | T039, T042 |
| FR-030 | T012, T047 |
| FR-031 | T011, T047 |
| SC-001 | T017, T019, T021, T022, T050 |
| SC-002 | T024, T026, T027, T029, T030, T050 |
| SC-003 | T033, T035, T050 |
| SC-004 | T038, T040, T044, T050 |
| SC-005 | T013, T040, T041, T042, T050 |
| SC-006 | T017, T021, T022, T050 |
| SC-007 | T016, T046, T050 |

## Implementation Strategy

### MVP First

1. Concluir Phase 1 e Phase 2.
2. Implementar US1 para consulta institucional pública.
3. Implementar US2 para consulta acadêmica pública.
4. Parar no checkpoint e validar os dois fluxos públicos pelo `quickstart.md`.

### Incremental Delivery

1. Setup e fundação.
2. US1: Central de Editais e Avisos.
3. US2: Base de Conhecimento.
4. US3: cadastro, login e contribuições.
5. US4: moderação, denúncias e administração.
6. Polish e atualização da documentação.

### Notes

- Cada tarefa possui checkbox, ID sequencial e caminho de arquivo.
- O marcador `[P]` indica tarefas que podem ocorrer em paralelo sem depender de uma alteração incompleta em outro arquivo.
- As tarefas de teste automatizado não foram incluídas como TDD porque esse fluxo não foi solicitado explicitamente; a validação do MVP está descrita em `specs/001-unb-core/quickstart.md`.
