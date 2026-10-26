# Implementation Plan: UNB CORE

**Branch**: `feature/corte-escopo-academico` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

## Summary

O UNB CORE será uma plataforma acadêmica colaborativa para consulta de conteúdos organizados por curso e disciplina. O MVP terá autenticação local, contribuições submetidas por usuários autenticados e moderação por moderadores e administradores. O módulo institucional de editais, fontes, denúncias e busca unificada foi removido do escopo.

## Technical Context

**Language/Version**: Python 3.12+ no backend; JavaScript moderno no frontend

**Primary Dependencies**: FastAPI, Pydantic, SQLModel, Uvicorn, React, Vite e cliente HTTP

**Storage**: SQLite no desenvolvimento e MVP; migração para PostgreSQL fica fora deste incremento

**Testing**: pytest e httpx para regras e API; Vitest, Testing Library e ESLint no frontend; testes de integração para os fluxos de autenticação, consulta, contribuição e moderação; testes de interface para os fluxos críticos

**Target Platform**: Navegadores desktop atuais e Chrome/Safari mobile atuais

**Project Type**: Aplicação web com frontend e backend separados

**Performance Goals**: Sem metas específicas de desempenho para o MVP acadêmico

**Constraints**: Consulta pública; escrita protegida por autenticação e perfil; contribuições sempre começam como pendentes; aprovação cria ou atualiza conteúdo; a matriz de validação cobre Chrome, Edge e Firefox desktop e Chrome Android e Safari iOS nas versões estáveis mais recentes

**Scale/Scope**: MVP acadêmico inicialmente focado em Engenharia de Software, com cursos, disciplinas, conteúdos, autenticação, contribuições, moderação e administração de usuários

## Constitution Check

A constituição do projeto ainda contém apenas placeholders e não define princípios ratificados. Não há gates normativos adicionais. O plano adota simplicidade, separação de responsabilidades, testes dos fluxos críticos e ausência de segredos versionados.

## Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── schemas/
│   │   └── routers/
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

specs/001-unb-core/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

**Structure Decision**: Aplicação separada em backend e frontend. O backend concentra modelos, regras, autenticação, autorização e contratos HTTP. O frontend concentra navegação, formulários, consulta acadêmica e estado de sessão. Os testes ficam separados por camada e os contratos da API ficam versionados em `specs/001-unb-core/contracts/`.

## Delivery Strategy

1. Preparar configuração, banco, erros e autenticação.
2. Entregar consulta pública de cursos, disciplinas e conteúdos.
3. Entregar envio e acompanhamento de contribuições.
4. Entregar moderação e publicação derivada das contribuições.
5. Entregar administração de usuários e integração frontend/backend.
6. Validar o quickstart, os fluxos críticos e a documentação.

## Complexity Tracking

Não há violações da constituição ratificada nem complexidade adicional a justificar.
