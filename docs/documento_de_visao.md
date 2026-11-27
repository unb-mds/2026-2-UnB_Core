# Documento de Visão — UNB CORE

**Projeto:** Métodos de Desenvolvimento de Software (MDS) — 2026/2  
**Equipe:** G1  
**Última atualização:** 26/11/2026

## Visão do produto

O UNB CORE é uma plataforma para aproximar estudantes da Universidade de
Brasília do conhecimento produzido por quem já cursou as disciplinas. A
proposta é organizar materiais acadêmicos por curso e disciplina e permitir
que estudantes compartilhem contribuições revisadas pela comunidade.

## Objetivo original

A visão inicial era reunir, em um mesmo produto, duas frentes:

1. **Base de Conhecimento acadêmica (Tamburetei)** — a parte atualmente
   implementada pelo projeto: consultar materiais por curso,
   disciplina e tipo de conteúdo, além de enviar contribuições para revisão.
2. **Integração com editais e avisos oficiais** — reunir informações
   institucionais consultadas em fontes da UnB, com filtros e acesso às
   publicações oficiais.

A integração com editais foi considerada uma ampliação possível caso houvesse
tempo e capacidade para desenvolvê-la. A intenção era complementar a experiência
acadêmica, não substituir os canais oficiais da Universidade.

## Evolução e redução de escopo

Durante o desenvolvimento, metade do grupo trancou, reduzindo a capacidade
disponível para implementar e validar o produto. Para manter uma entrega
funcional e coerente com o tempo e a equipe restantes, o grupo reduziu o escopo
do projeto e priorizou a Base de Conhecimento acadêmica.

Esse corte foi uma decisão de priorização do MVP: a integração com editais,
avisos, fontes institucionais e busca unificada ficou fora da entrega atual. O
histórico de requisitos registra a retirada do módulo institucional em
26/10/2026.

## MVP atual

O MVP concentra-se nos fluxos acadêmicos:

- consultar conteúdos publicados, organizados e filtrados por curso,
  disciplina e tipo;
- obter a lista de cursos de graduação e suas disciplinas a partir das páginas
  públicas do SIGAA;
- criar conta, entrar no sistema e gerenciar o próprio perfil;
- enviar, acompanhar, editar e solicitar a exclusão de contribuições;
- submeter contribuições à revisão antes de publicá-las;
- permitir que moderadores e administradores aprovem, rejeitem, arquivem,
  solicitem ajustes ou tratem pedidos de exclusão;
- administrar contas e atender pedidos de recuperação de senha.

A Base de Conhecimento é pública para consulta. Ações de contribuição,
moderação e administração dependem de autenticação e das permissões da conta.

## Público e benefício

O público principal são estudantes de graduação da UnB. Veteranos podem
compartilhar materiais e experiências; moderadores e administradores ajudam a
manter a qualidade das publicações e a operação das contas.

O benefício esperado é reduzir a dispersão de materiais acadêmicos e facilitar
que estudantes encontrem informações úteis para suas disciplinas em um só
lugar, com autoria e revisão.

## Fora do MVP e possibilidade futura

Não fazem parte da entrega atual:

- central de editais e publicações institucionais;
- coleta automática de avisos e informações institucionais;
- cadastro de fontes e categorias institucionais;
- denúncias institucionais e busca unificada entre módulos.

Esses itens podem ser reavaliados em uma etapa futura se houver equipe,
capacidade e tempo. 

## Estado da solução

O MVP está publicado: o frontend está no Vercel, a API no Render e o banco de
dados no Neon. O produto atual inclui a Base de Conhecimento acadêmica e seu
fluxo de contribuições moderadas; não inclui a integração com editais.

Para detalhes funcionais, consulte o [Documento de Requisitos](requisitos.md).
Instruções práticas estão nos guias [Como rodar o projeto](como-rodar.md) e
[Publicação no Vercel, Render e Neon](publicacao.md).
