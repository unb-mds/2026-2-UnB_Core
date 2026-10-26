# Issues de Implementação: UNB CORE — MVP acadêmico

**Fonte:** [plan.md](plan.md) e [tasks.md](tasks.md)
**Branch de trabalho:** `feature/corte-escopo-academico`
**Issue principal:** `unb-mds/G1-2026-2#126`

Este arquivo organiza as fases do novo escopo. A criação e o acompanhamento das issues do GitHub devem referenciar esta divisão e os IDs de `tasks.md`.

## Fases propostas

| Fase | Objetivo | Tasks |
|---|---|---|
| Setup | Estrutura, dependências e documentação inicial | T001-T004 |
| Foundation | Banco, modelos, schemas, erros e autorização | T005-T011 |
| Consulta acadêmica | Cursos, disciplinas e conteúdos públicos | T012-T019 |
| Contribuições | Cadastro, login, envio e acompanhamento | T020-T029 |
| Moderação | Decisões e publicação derivada | T030-T036 |
| Administração | Gestão de usuários e perfis | T037-T040 |
| Qualidade | Testes, limpeza, documentação e validação | T041-T047 |

## Dependências

```text
Setup -> Foundation
Foundation -> Consulta acadêmica
Foundation -> Contribuições
Consulta acadêmica + Contribuições -> Moderação
Contribuições -> Administração
Todas as fases funcionais -> Qualidade
```

## Escopo removido

Não criar novas tarefas ou issues para:

- editais e publicações institucionais;
- fontes institucionais;
- categorias institucionais;
- denúncias;
- busca unificada entre módulos;
- coleta automática de informações institucionais.
