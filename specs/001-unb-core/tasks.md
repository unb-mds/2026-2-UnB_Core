---
description: "Tarefas de implementação do MVP acadêmico do UNB CORE"
---

# Tasks: UNB CORE — MVP acadêmico

**Input**: Design documents from `/specs/001-unb-core/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup

- [ ] T001 Criar a estrutura de testes em `backend/tests/{unit,integration,contract}` e `frontend/tests/{unit,integration}`.
- [ ] T002 [P] Consolidar `backend/requirements.txt` com FastAPI, Uvicorn, SQLModel, PyJWT, passlib, bcrypt, pytest e httpx.
- [ ] T003 [P] Criar ou corrigir `frontend/package.json` e scripts `dev`, `build`, `lint` e `test`.
- [ ] T004 [P] Atualizar `README.md` para descrever somente o MVP acadêmico e seus comandos de execução.

## Phase 2: Foundational

- [ ] T005 Implementar `backend/app/settings/config.py` com `DATABASE_URL`, `JWT_SECRET_KEY` e configurações sem segredos versionados.
- [ ] T006 Implementar `backend/app/db.py` com engine SQLite, criação de tabelas e dependência de sessão.
- [ ] T007 [P] Normalizar os modelos em `backend/app/domain/` para `Usuario`, `Curso`, `Disciplina`, `ConteudoAcademico` e `Contribuicao` conforme `data-model.md`.
- [ ] T008 [P] Criar schemas de entrada e saída em `backend/app/api/schemas/` sem expor senha, `autor_id` ou estado controlado pelo servidor.
- [ ] T009 Implementar `backend/app/api/errors.py` e padronizar respostas de validação, autenticação, permissão e recurso não encontrado.
- [ ] T010 Implementar `backend/app/api/dependencies.py` com usuário atual e verificadores de perfil moderador e administrador.
- [ ] T011 Implementar `backend/app/api/router.py` e registrar todos os routers sob `/api/v1` em `backend/app/main.py`.

## Phase 3: User Story 1 — Consultar conteúdos acadêmicos (P1)

**Goal**: Permitir consulta pública por curso, disciplina e tipo, exibindo somente conteúdos publicados.

**Independent Test**: Com curso, disciplina e conteúdo publicados, selecionar os filtros sem login e confirmar os detalhes de autoria/origem e atualização.

- [ ] T012 [P] [US1] Criar `backend/tests/integration/test_consulta_academica.py` cobrindo cursos, disciplinas, conteúdos publicados, filtro por tipo e estado vazio.
- [ ] T013 [P] [US1] Implementar `backend/app/services/curso_service.py` para listar cursos e disciplinas ativos.
- [ ] T014 [US1] Implementar `backend/app/services/conteudo_service.py` para listar e detalhar conteúdos publicados por disciplina e tipo.
- [ ] T015 [US1] Implementar `GET /api/v1/cursos` e `GET /api/v1/cursos/{curso_id}/disciplinas` em `backend/app/api/routers/academico.py`.
- [ ] T016 [US1] Implementar `GET /api/v1/disciplinas/{disciplina_id}/conteudos` e `GET /api/v1/conteudos/{conteudo_id}` em `backend/app/api/routers/academico.py`.
- [ ] T017 [P] [US1] Remover mocks de cursos e integrar `frontend/src/pages/ConhecimentoPage.jsx` aos endpoints acadêmicos.
- [ ] T018 [P] [US1] Ajustar `frontend/src/components/conteudos/ConteudoCard.jsx` e `ConteudoDetalhe.jsx` aos campos do contrato acadêmico.
- [ ] T019 [US1] Criar `frontend/tests/integration/knowledge.test.jsx` para consulta, filtro, carregamento, erro e estado vazio.

## Phase 4: User Story 2 — Enviar e acompanhar contribuições (P2)

**Goal**: Permitir que usuários autenticados enviem propostas pendentes e consultem seu estado.

**Independent Test**: Criar uma conta, fazer login, enviar uma contribuição válida, consultar a lista pessoal e confirmar `pendente`; rejeitar envio sem autenticação ou campos obrigatórios.

- [ ] T020 [P] [US2] Criar `backend/tests/integration/test_auth.py` para cadastro, login, sessão e senha ausente das respostas.
- [ ] T021 [P] [US2] Criar `backend/tests/integration/test_contribuicoes.py` para criação pendente, listagem própria, validação e autenticação.
- [ ] T022 [US2] Implementar `backend/app/services/auth_service.py` com cadastro, hash, verificação de senha e emissão de token.
- [ ] T023 [US2] Implementar `backend/app/api/routers/auth.py` com `POST /api/v1/auth/cadastro`, `POST /api/v1/auth/login` e `GET /api/v1/auth/me`.
- [ ] T024 [US2] Implementar `backend/app/services/contribuicao_service.py` para validar criação/alteração e iniciar toda contribuição como `pendente`.
- [ ] T025 [US2] Implementar `POST /api/v1/contribuicoes` e `GET /api/v1/contribuicoes/minhas` em `backend/app/api/routers/contribuicoes.py`.
- [ ] T026 [US2] Ajustar `frontend/src/services/api.js` e `frontend/src/state/auth.js` ao contrato de autenticação versionado.
- [ ] T027 [US2] Ajustar `frontend/src/pages/CadastroPage.jsx`, `LoginPage.jsx` e `ContribuicaoPage.jsx` aos payloads de autenticação e contribuição.
- [ ] T028 [P] [US2] Ajustar `frontend/src/pages/MinhasContribuicoesPage.jsx` para carregar estados e justificativas reais.
- [ ] T029 [US2] Criar `frontend/tests/integration/auth-contribution.test.jsx` para cadastro, login, envio autenticado e bloqueio sem sessão.

## Phase 5: User Story 3 — Moderar conteúdos (P2)

**Goal**: Permitir decisões de moderadores e administradores, refletindo aprovações no conteúdo publicado.

**Independent Test**: Criar contribuição pendente, decidir como moderador, confirmar estado, justificativa e criação/atualização do conteúdo; negar operação para usuário comum.

- [ ] T030 [P] [US3] Criar `backend/tests/integration/test_moderacao.py` para decisões, transições, permissões e efeitos sobre conteúdo.
- [ ] T031 [US3] Implementar `backend/app/services/moderacao_service.py` com transições válidas e justificativas.
- [ ] T032 [US3] Implementar aprovação criando ou atualizando conteúdo em `backend/app/services/conteudo_service.py`.
- [ ] T033 [US3] Implementar `GET /api/v1/moderacao/contribuicoes` e `POST /api/v1/moderacao/contribuicoes/{id}/decisao` em `backend/app/api/routers/moderacao.py`.
- [ ] T034 [P] [US3] Criar `frontend/src/pages/ModeracaoPage.jsx` e componentes em `frontend/src/components/moderacao/` para listar e decidir contribuições.
- [ ] T035 [US3] Proteger a navegação de moderação em `frontend/src/components/Navigation.jsx` e tratar respostas 403/401.
- [ ] T036 [US3] Criar `frontend/tests/integration/moderacao.test.jsx` para permissões, decisão e atualização da lista.

## Phase 6: Administração de usuários

- [ ] T037 [P] Criar `backend/tests/integration/test_usuarios_admin.py` para criação, alteração de perfil e bloqueio de não administradores.
- [ ] T038 Implementar `GET /api/v1/usuarios`, `POST /api/v1/usuarios` e `PATCH /api/v1/usuarios/{id}` em `backend/app/api/routers/usuarios.py`, restritos a administradores.
- [ ] T039 Implementar seed opcional de usuário administrativo em `backend/scripts/seed_admin.py` sem senha versionada.
- [ ] T040 [P] Criar `frontend/src/pages/AdminUsuariosPage.jsx` para cadastro e atualização de usuários moderadores e administradores.

## Phase 7: Polish and Cross-Cutting Concerns

- [ ] T041 Executar `python -m pytest` e corrigir falhas nos testes backend.
- [ ] T042 Executar build, lint e testes do frontend e corrigir falhas de integração.
- [ ] T043 [P] Atualizar `docs/requisitos.md`, `docs/documento_de_visao.md` e documentos de sprint para remover referências ao módulo institucional.
- [ ] T044 [P] Revisar `specs/001-unb-core/` contra a implementação e atualizar `quickstart.md` com comandos realmente executáveis.
- [ ] T045 Remover rotas, modelos, serviços e componentes de editais, publicações institucionais, fontes, denúncias e busca unificada que não sejam mais utilizados.
- [ ] T046 Atualizar `.gitignore` para ignorar `__pycache__/`, `*.pyc`, bancos SQLite locais e arquivos de ambiente.
- [ ] T047 Executar a validação completa dos cenários de `quickstart.md` e registrar o resultado na issue #126.

## Dependencies and Execution Order

```text
Phase 1 -> Phase 2
Phase 2 -> US1
Phase 2 -> US2
US1 + US2 -> US3
US2 -> Administração de usuários
US1 + US2 + US3 + Administração -> Polish
```

US1 pode avançar em paralelo com US2 depois da Phase 2. US3 depende da autenticação, dos modelos acadêmicos e do fluxo de contribuições.

## Parallel Execution Examples

```text
US1: T012, T013, T017 e T018 podem começar em paralelo após T007 e T008.
US2: T020, T021, T022 e T026 podem começar em paralelo após T007-T010.
US3: T030 e T034 podem começar em paralelo após os contratos de contribuição e autenticação.
Administração: T037 e T040 podem começar em paralelo após T010 e T011.
```

## Implementation Strategy

1. Entregar primeiro a consulta acadêmica pública.
2. Integrar autenticação e contribuições.
3. Implementar moderação com efeitos transacionais sobre conteúdos.
4. Adicionar administração de usuários.
5. Remover código institucional e executar a validação completa.
