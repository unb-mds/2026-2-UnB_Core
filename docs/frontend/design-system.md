# Design system do frontend

O design system é implementado principalmente pelos tokens CSS em
`frontend/src/index.css` e pelos estilos compartilhados em
`frontend/src/components/` e `frontend/src/components/layout/`. Componentes e
páginas usam essas variáveis para manter uma identidade visual consistente.

## Tipografia e layout

- **Texto:** IBM Plex Sans.
- **Títulos de destaque:** JetBrains Mono.
- **Largura máxima:** `--layout-max` de 1200 px.
- **Margens responsivas:** `--layout-gutter` alinha conteúdo, menu e rodapé.
- **Espaçamento:** escala de `--spacing-xs` a `--spacing-3xl`.
- **Formas e sombras:** tokens de raio (`--radius-sm`, `--radius-full`) e
  elevação (`--shadow-sm`, `--shadow-md`).

## Cores e temas

Os tokens definem cores de marca, texto, fundo, superfície, campos, bordas,
estados de erro, sucesso e alerta. O tema claro é o padrão; o tema escuro
substitui os valores das variáveis CSS usando `:root[data-theme="dark"]`.

O estado do tema é controlado em `frontend/src/state/theme.js`, salvo no
`localStorage` e aplicado pelo atributo `data-theme` no elemento `<html>`. Sem
preferência salva, o site segue `prefers-color-scheme`.

## Cores por tipo de conteúdo

Cada tipo possui tokens próprios para texto, fundo do badge e faixa de destaque
do cartão:

| Tipo | Tokens |
|---|---|
| Resumo | `--type-resumo-text`, `--type-resumo-bg`, `--type-resumo-line` |
| Dica | `--type-dica-text`, `--type-dica-bg`, `--type-dica-line` |
| Dificuldade | `--type-dificuldade-text`, `--type-dificuldade-bg`, `--type-dificuldade-line` |
| Prova | `--type-prova-text`, `--type-prova-bg`, `--type-prova-line` |
| Implementação | `--type-implementacao-text`, `--type-implementacao-bg`, `--type-implementacao-line` |
| Link | `--type-link-text`, `--type-link-bg`, `--type-link-line` |

As cores de tipo são distintas das cores de estado da contribuição. Assim,
cores de pendente, aprovada ou rejeitada não são confundidas com a categoria do
material.

## Componentes e estilos

- Estilos globais: `frontend/src/index.css`.
- Layout de páginas: `frontend/src/components/layout/layout.css`.
- Componentes compartilhados: `frontend/src/components/components.css` e
  arquivos CSS próximos aos componentes.
- Estilos específicos das telas: CSS dentro de `frontend/src/pages/`.
- Componentes visuais comuns incluem `Button`, `SearchInput`, `EmptyState`,
  badges de tipo e estado, navegação e mensagens de erro.

Ao adicionar ou ajustar uma interface, prefira os tokens e componentes
existentes antes de introduzir cores, medidas ou padrões locais novos.
