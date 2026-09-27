# Design system — UNB CORE

## Direção conceitual

A identidade parte do trocadilho com o nome **CORE**: um azul profundo e um ciano de alta energia, na linha do que a Intel usa na linha Core Ultra, o qual transmite a sensação de "núcleo", potência e confiabilidade técnica. Para não cair no clichê genérico de "produto de IA" (fundo quase preto + acento neon em tudo), o azul profundo é usado como **cor de marca concentrada** no cabeçalho, cartão de destaque, navegação ativa, ícones e botões primários, enquanto o restante da interface (cards de conteúdo, corpo de texto) permanece em base clara, garantindo legibilidade para leitura longa de editais e resumos.

A tipografia usa uma monoespaçada (JetBrains Mono) como assinatura de identidade remete a terminal e spec sheet, reforçando o trocadilho com "Core" e conversando direto com o público de Engenharia de Software — mas **só em pontos de alto impacto**: logo, headline do hero e títulos de seção. Todo o resto usa uma humanista sem serifa (IBM Plex Sans), que segura bem a leitura de parágrafos longos em editais e resumos.

## Princípios de uso

1. **Azul em pontos de ação e estrutura, não em blocos grandes de fundo** — navegação, botões, ícones, bordas de destaque e um cartão de destaque pontual. Se toda a tela virar azul, ele deixa de ser acento e vira só "modo escuro" — o que tira a distinção que buscamos.
2. **Ciano é o tempero, não o prato principal** — reservado a poucos pontos de alta energia (CTA sobre fundo escuro, um detalhe de ícone), nunca como cor de texto corrido ou fundo grande.
3. **Cor com significado, não decoração** — `Âmbar` e as cores de status ficam reservadas ao estado da publicação, nunca usadas como enfeite solto.
4. **Mono é a exceção, não a regra** — reservada a logo, headline do hero e títulos de seção (no máximo 2-3 usos por tela). Título de card, tag, botão e metadado usam Plex Sans; espalhar a mono por tudo deixa a interface carregada e prejudica a leitura rápida.
5. **Sentence case sempre** — em rótulos, botões e tags, nunca caixa alta.
6. **Contraste testado** — ao aplicar `Azul core` ou `Azul core escuro` como fundo, use branco ou `Ciano ultra` como texto/ícone; ao usar `Base clara` como fundo, use `Grafite`.

---

## 1. Paleta de cores

### Cores base (Styles de cor no Figma)

| Nome no Figma | Hex | Uso |
|---|---|---|
| `Azul core escuro` | `#0B1638` | Fundo do cartão de destaque, cabeçalho escuro, gradiente (par com Azul core) |
| `Azul core` | `#1B3A8F` | Cor primária de marca — navegação ativa, botões primários, bordas de destaque, ícones, links |
| `Ciano ultra` | `#33D6F6` | Acento de alta energia — usar com moderação |
| `Âmbar` | `#EFB43A` | Reservado a status de alerta ("não verificado", prazos próximos) |
| `Base clara` | `#F4F5F7` | Fundo de página |
| `Grafite` | `#1B1F2A` | Texto principal |

### Escala neutra

| Nome | Hex | Uso |
|---|---|---|
| `Neutro 00` | `#FFFFFF` | Superfície de card |
| `Neutro 10` | `#F4F5F7` | Fundo de página |
| `Neutro 30` | `#E2E4EA` | Bordas sutis |
| `Neutro 50` | `#9AA0AE` | Texto secundário |
| `Neutro 70` | `#5A5F6E` | Texto terciário/placeholder |
| `Neutro 90` | `#1B1F2A` | Texto principal |

### Cores de status (Central de Editais)

| Status | Hex fundo | Hex texto |
|---|---|---|
| Ativo | `#EAF6E8` | `#1F7A3D` |
| Encerrado | `#F0F1F4` | `#5A5F6E` |
| Desatualizado / não verificado | `#FDF0DA` | `#8A5A12` |

> Verde fica reservado só ao status "ativo" — não usar como cor de marca, para não competir com o azul.

---

## 2. Tipografia

### Famílias (Google Fonts)

| Papel | Fonte | Pesos |
|---|---|---|
| Display de alto impacto (logo, headline do hero, título de seção) | **JetBrains Mono** | 500, 700 |
| Tudo o resto — UI, corpo, título de card, tags, navegação | **IBM Plex Sans** | 400, 500, 600, 700 |

### Escala tipográfica

| Estilo | Fonte | Tamanho | Line-height | Uso |
|---|---|---|---|---|
| Display | JetBrains Mono 700 | 30-34px | 1.25 | Headline do hero |
| Section title | JetBrains Mono 700 | 18-20px | 1.3 | Título de seção |
| Logo | JetBrains Mono 700 | 16px | 1.2 | `unb_core` na navbar |
| H1 | IBM Plex Sans 700 | 28px | 1.25 | Título de página (fora do hero) |
| H2 | IBM Plex Sans 600 | 20px | 1.3 | Subtítulo de página |
| H3 / título de card | IBM Plex Sans 600 | 14-16px | 1.35 | Título de card de edital/conteúdo |
| Body | IBM Plex Sans 400 | 14-15px | 1.6 | Texto padrão de leitura |
| UI Label | IBM Plex Sans 500-600 | 13-14px | 1.4 | Botões, navegação |
| Small / Caption / Tag | IBM Plex Sans 500 | 11-12px | 1.4 | Metadados, datas, tags |

Manter body text abaixo de ~72 caracteres por linha para leitura confortável de editais longos.

---

## 3. Espaçamento e grid

### Escala de espaçamento (múltiplos de 4px)

`4 · 8 · 12 · 16 · 24 · 32 · 48 · 64`

### Grid de layout

- **Desktop**: 12 colunas, margem lateral 64px, gutter 24px, largura máxima de conteúdo 1200px.
- **Mobile**: 4 colunas, margem lateral 16px, gutter 16px.
- **Alinhamento**: predominantemente à esquerda — evitar centralizar blocos de texto longo.

### Raio de borda

| Token | Valor | Uso |
|---|---|---|
| `radius-sm` | 4-6px | Inputs, cards, botões |
| `radius-pill` | 999px | Tags, badges de status, chips de categoria |

Não misture os dois tamanhos de raio no mesmo tipo de elemento.

---

## 4. Componentes-base

| Componente | Notas |
|---|---|
| Botão primário | Fundo `Azul core`, texto branco, `radius-sm`, label IBM Plex Sans 600 13-14px |
| Botão secundário | Borda `Azul core` 1px, fundo transparente, texto `Azul core` |
| Tag de status | Pill (`radius-pill`), cores de status, texto IBM Plex Sans 500 11-12px, sentence case |
| Tag de categoria | Pill fundo `#EAF0FD`, texto `Azul core` |
| Card de edital / conteúdo acadêmico | `radius-sm`, borda 0.5px `Neutro 30`, borda esquerda de 3px na cor do status ou `Azul core`, padding 16px, título em IBM Plex Sans 600 |
| Cartão de destaque | Gradiente `Azul core` → `Azul core escuro`, texto branco, título em JetBrains Mono 700, CTA em `Ciano ultra` |
| Avatar / ícone de usuário | Fundo `Azul core`, ícone em `Ciano ultra` |
| Input de busca | Altura 44px, `radius-pill`, borda `Neutro 30`, foco com anel `Ciano ultra` |
| Navbar | Fundo branco, logo em JetBrains Mono, item ativo em `Azul core` com sublinhado de 2px |

---

## 5. Variáveis CSS (implementação)

> Sempre use `var(--nome-da-variavel)` em vez de valores fixos.

```css
/* ---------- Cores ---------- */
:root {
  --color-primary:       #1B3A8F;  /* azul core — botões, links, navegação ativa */
  --color-primary-dark:  #0B1638;  /* azul core escuro — cartão de destaque, gradiente */
  --color-accent:        #33D6F6;  /* ciano ultra — usar com moderação */

  --color-warning:       #EFB43A;  /* status "não verificado" */
  --color-success:       #1F7A3D;  /* status "ativo" */
  --color-success-bg:    #EAF6E8;

  --color-bg:            #F4F5F7;  /* fundo padrão */
  --color-bg-soft:       #EAF0FD;  /* fundo alternativo — tags de categoria */
  --color-text:          #1B1F2A;
  --color-text-muted:    #5A5F6E;
  --color-border:        #E2E4EA;
}
```

```css
/* ---------- Espaçamentos ---------- */
:root {
  --spacing-xs:   0.25rem;  /*  4px */
  --spacing-sm:   0.5rem;   /*  8px */
  --spacing-md:   1rem;     /* 16px */
  --spacing-lg:   1.5rem;   /* 24px */
  --spacing-xl:   2rem;     /* 32px */
  --spacing-2xl:  3rem;     /* 48px */
  --spacing-3xl:  4rem;     /* 64px */
}
```

```css
/* ---------- Bordas e raios ---------- */
:root {
  --radius-sm:    6px;      /* cards, botões, inputs */
  --radius-full:  9999px;   /* pills — tags, badges de status */
}
/* Não criar radius-md/lg: o sistema usa só 2 níveis, de propósito. */
```

```css
/* ---------- Sombras ---------- */
:root {
  --shadow-sm: 0 1px 2px rgba(11, 22, 56, 0.06);    /* cards, navbar */
  --shadow-md: 0 4px 12px rgba(27, 58, 143, 0.18);  /* botão primário, hover */
}
```

```css
/* ---------- Transições ---------- */
:root {
  --transition-fast:  150ms ease;  /* hovers rápidos */
  --transition-base:  300ms ease;  /* transições padrão */
}
```

### Classes de layout

```css
.container   /* largura máxima 1200px, centralizada, padding lateral 64px desktop / 16px mobile */
```

### Classes de tipografia

```css
.font-display     /* JetBrains Mono 700 — só headline, título de seção e logo */
.font-body        /* IBM Plex Sans — padrão para o resto */
.section-title    /* fonte display, alinhado à esquerda — não centralizar */
.text-highlight   /* texto em var(--color-primary) */
.text-muted       /* texto em var(--color-text-muted) */
```

### Classes de botões

```css
.btn           /* base: padding, var(--radius-sm), font IBM Plex Sans 600, var(--transition-fast) */
.btn-primary   /* fundo var(--color-primary), texto branco, var(--shadow-md) no hover */
.btn-outline   /* transparente, borda 1px var(--color-primary), texto var(--color-primary) */
.btn-accent    /* fundo var(--color-accent), texto var(--color-primary-dark) — CTA sobre fundo escuro */
```

### Classe de animação

```css
.reveal   /* elemento começa invisível, desliza para cima ao entrar na tela */
```

### Convenções de código

- Sempre `var(--nome-da-variavel)`, nunca valores fixos.
- IDs só para elementos únicos: `#navbar`, `#footer`, `#hero`.
- Classes para tudo reutilizável.
- Comentário de seção no topo de cada bloco: `/* ---------- Nome ---------- */`
- Breakpoints: Tablet `max-width: 1024px` · Mobile `max-width: 768px` · Mobile pequeno `max-width: 480px`
