# Implementation Plan: UNB CORE

**Branch**: `001-unb-core` | **Date**: 2026-09-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-unb-core/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

O UNB CORE será uma aplicação web acadêmica com a Base de Conhecimento colaborativa como foco principal e uma Central de Editais complementar. A Release 2 terá uma API FastAPI em Python, uma interface React e persistência em PostgreSQL com SQLModel. Contribuições exigirão autenticação e permanecerão pendentes até a moderação; editais serão cadastrados manualmente por administradores e sempre manterão a `url_oficial`.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12+ no backend; JavaScript moderno no frontend

**Primary Dependencies**: FastAPI, Pydantic, SQLModel, Uvicorn, React e um cliente HTTP para a interface

**Storage**: PostgreSQL como banco da Release 2; SQLite pode ser usado apenas em testes locais isolados

**Testing**: pytest para regras e API; testes de integração para fluxos principais; testes de interface ficam limitados aos fluxos críticos do MVP

**Target Platform**: Navegadores desktop e mobile atuais; servidor local ou ambiente web simples para a API

**Project Type**: Aplicação web com frontend e backend separados

**Performance Goals**: Não há metas específicas de desempenho no escopo acadêmico do MVP

**Constraints**: Leitura pública sem autenticação; escrita protegida por autenticação e perfil; editais somente para cadastro manual e consulta; `url_oficial` obrigatória; contribuições sempre passam por moderação

**Scale/Scope**: Release 2 focada inicialmente em Engenharia de Software, com consulta acadêmica, autenticação, contribuições, moderação e uma consulta básica de editais

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Não há gates específicos a aplicar: a constituição ainda contém apenas placeholders e não define princípios ratificados. O plano seguirá simplicidade, separação de responsabilidades e testes das regras críticas.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
backend/
├── app/
│   ├── api/
│   ├── domain/
│   ├── services/
│   ├── settings/
│   └── main.py
└── tests/
  ├── contract/
  ├── integration/
  └── unit/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── state/
└── tests/
  ├── integration/
  └── unit/

docs/
├── backend_sprint_0.md
└── requisitos.md
```

**Structure Decision**: Aplicação web separada em `backend/` e `frontend/`, com regras e persistência organizadas no backend e páginas/componentes organizados no frontend. Os testes ficam próximos de cada parte e os contratos da feature ficam em `specs/001-unb-core/contracts/`.

## Complexity Tracking

Não há violações da constituição ratificada nem complexidade adicional a justificar.
