# Documento de Visão — UNB CORE

*Repositório: unb-mds/2026.2-UnB_Core*
*Disciplina: Métodos de Desenvolvimento de Software (MDS) — 2026/2, Universidade de Brasília*

---

## 1. Introdução

### 1.1 Propósito do documento

Esta introdução fornece uma visão geral de todo o Documento de Visão do projeto UnB Core. Estabelece o propósito do documento, delimita o escopo do sistema, lista as definições, acrônimos e abreviações necessários para a correta interpretação, apresenta as referências utilizadas e oferece uma visão geral da estrutura completa deste documento.

### 1.2 Definições, siglas e abreviações

| Termo | Definição |
|---|---|
| MVP | Minimum Viable Product - versão mínima funcional do produto |
| RF / RNF | Requisito Funcional / Requisito Não Funcional |
| Edital | Publicação oficial da UnB (bolsa, monitoria, auxílio, processo seletivo etc.) |
| Fonte institucional | Órgão ou canal oficial da UnB de onde uma publicação é originada (Reitoria, decanato, instituto) |
| Spec-kit | Ferramenta de desenvolvimento orientado a especificação (*spec-driven development*) usada para gerar `spec.md`, `plan.md` e `tasks.md` |
| Sprint | Ciclo de desenvolvimento da disciplina MDS, associado a um Milestone (M0, M1, M2...) |

### 1.3 Referências

- Repositório do projeto: `unb-mds/2026.2-UnB_Core`
- Tamburetei (OpenDevUFCG): referência de base de conhecimento colaborativa: `github.com/OpenDevUFCG/Tamburetei`
- `docs/requisitos.md`: especificação detalhada de requisitos
- `specs/001-unb-core/`: artefatos gerados via spec-kit (spec, plan, tasks, quickstart)
- Disciplina de Métodos de Desenvolvimento de Software - UnB

---

## 2. Posicionamento

### 2.1 Descrição do problema

1. **Conhecimento acadêmico disperso**: a cada semestre, novas turmas recomeçam do zero para descobrir como funcionam as disciplinas do curso, quais são as dificuldades mais comuns e onde encontrar materiais de apoio. Esse conhecimento raramente é sistematizado ou passado adiante de forma estruturada.
2. **Informação institucional fragmentada**: editais, bolsas, monitorias e avisos oficiais da UnB estão espalhados entre a Reitoria, decanatos, institutos e canais diversos (sites, SEI, murais, grupos informais), em formatos inconsistentes. Isso faz com que estudantes percam oportunidades relevantes simplesmente por não saberem que elas existem.

**Afetados**: estudantes de graduação da UnB, com impacto adicional em veteranos (que possuem conhecimento não compartilhado) e em coordenações de curso (que têm dificuldade de alcançar os alunos com informações relevantes).

**Impacto de não resolver**: perda recorrente de oportunidades acadêmicas e financeiras (bolsas, auxílios), curva de aprendizado repetida a cada semestre sem aproveitamento do conhecimento de turmas anteriores, e baixa visibilidade de comunicados institucionais importantes.

### 2.2 Declaração de posicionamento do produto

> Para estudantes de graduação da UnB, que precisam de um lugar único e confiável para encontrar conhecimento acadêmico compartilhado e oportunidades institucionais (editais, bolsas, avisos), o UNB CORE é uma plataforma web de centralização de informação acadêmica e institucional que reúne base de conhecimento colaborativa e central de editais em um único ponto de acesso, com transparência sobre a origem e atualização de cada informação. Diferente de soluções isoladas e não-oficiais (grupos de WhatsApp, páginas de curso avulsas, sites institucionais fragmentados, o UNB CORE **combina curadoria colaborativa com rastreabilidade de fonte oficial, deixando explícito quando uma informação não pode ser confirmada, em vez de presumir que permanece válida.

---

## 3. Descrição dos Stakeholders e Usuários

### 3.1 Resumo dos principais stakeholders

| Stakeholder | Interesse no projeto |
|---|---|
| Estudantes de graduação (usuário final) | Encontrar conteúdo de disciplinas e oportunidades institucionais com confiança |
| Veteranos/colaboradores | Compartilhar conhecimento acumulado de forma estruturada |
| Moderadores/administradores | Garantir qualidade e confiabilidade do conteúdo publicado |
| Equipe de desenvolvimento (grupo MDS) | Entregar um MVP funcional dentro do cronograma da disciplina |
| Professores/avaliadores da disciplina MDS | Avaliar aderência a boas práticas de engenharia de software |

### 3.2 Perfis de usuários (personas)

**Persona 1: Calouro em dúvida**
Aluno do 1º ou 2º semestre de Engenharia de Software, ainda sem rede de contato com veteranos, buscando entender como são as disciplinas e quais dificuldades esperar. Usa o sistema principalmente em modo consulta, sem necessidade de conta.

**Persona 2: Veterano colaborador**
Aluno avançado no curso, motivado a repassar conhecimento (resumos, dicas, dificuldades comuns) para turmas futuras. Precisa de um fluxo simples de contribuição e visibilidade sobre o status de revisão do que envia.

**Persona 3: Estudante caçador de oportunidades**
Aluno em qualquer fase do curso interessado em bolsas, monitorias e auxílios, mas sem tempo de acompanhar manualmente vários canais institucionais. Valoriza filtros por categoria/prazo e clareza sobre se a informação ainda está ativa.

**Persona 4: Moderador/administrador**
Membro da equipe ou colaborador de confiança responsável por revisar contribuições acadêmicas e cadastrar editais a partir das fontes oficiais no MVP.

### 3.3 Ambiente do usuário

Acesso primariamente via navegador web (desktop e mobile), em ambiente acadêmico (laboratórios, redes da própria universidade) ou doméstico. Não se assume necessidade de aplicativo nativo no MVP. Usuários podem ter conectividade instável em determinados pontos do campus.

### 3.4 Necessidades dos stakeholders/usuários

- Encontrar rapidamente material de uma disciplina específica.
- Saber se uma oportunidade (edital) ainda está ativa, sem precisar visitar múltiplas fontes.
- Contribuir com conhecimento sem barreira técnica alta.
- Confiar na informação apresentada, com rastreabilidade até a fonte oficial.
- Como moderador, revisar contribuições com contexto suficiente para decidir rapidamente.

---

## 4. Visão Geral do Produto

### 4.1 Perspectiva do produto

O UNB CORE é um produto novo e independente. Não substitui nem se integra formalmente aos sistemas oficiais da UnB (SIGAA, SEI, sites institucionais) no MVP, funcionando como uma camada de agregação e curadoria por cima dessas fontes. Internamente, é composto por dois módulos que compartilham uma mesma aplicação: Base de Conhecimento e Central de Editais.

### 4.2 Resumo de funcionalidades/recursos

- Navegação e busca unificada entre base de conhecimento e central de editais.
- Contribuição de conteúdo acadêmico com fluxo de revisão/moderação.
- Cadastro manual de publicações institucionais por administradores, com dados de fonte e verificação.
- Diferenciação clara de status (ativo, encerrado, desatualizado, não verificado).
- Autenticação opcional para preferências e notificações.

### 4.3 Premissas e dependências

- Assume-se que há disponibilidade de ao menos um moderador ativo para revisar contribuições e cadastrar editais durante o MVP.
- Depende da existência de fontes oficiais acessíveis publicamente (sites de decanatos, Reitoria) para cadastro manual.
- Assume-se turma piloto de Engenharia de Software como escopo acadêmico inicial, com possibilidade de expansão posterior.
- Depende de definição futura de hospedagem e persistência (PostgreSQL em produção, SQLite em desenvolvimento).

---

## 5. Recursos do Produto (Features)

Lista priorizada (P1 = essencial ao MVP, P2 = desejável, P3 = trabalho futuro):

| Prioridade | Recurso |
|---|---|
| P1 | Consulta pública de conteúdo acadêmico por curso/disciplina |
| P1 | Consulta pública de editais/avisos com filtros por categoria e prazo |
| P1 | Busca unificada entre os dois pilares |
| P1 | Cadastro manual de publicações institucionais por administrador, com fonte e data de verificação |
| P1 | Envio de contribuição acadêmica com fluxo de revisão (pendente para aprovado/ajustes/rejeitado) |
| P1 | Diferenciação de status de publicação (ativa/encerrada/desatualizada/não verificada) |
| P2 | Autenticação opcional e preferências de curso/categoria |
| P2 | Notificações sobre publicações compatíveis com preferências do usuário |
| P2 | Guia de primeira contribuição para reduzir barreira de entrada |
| P3 | Coleta automatizada (scraping/RSS) de fontes institucionais |
| P3 | Política de uso para compartilhamento de provas antigas |

---

## 6. Restrições

- **Prazo**: cronograma limitado ao semestre letivo da disciplina MDS (2026/2), com entregas por sprint/milestone (M0–M4 e seguintes).
- **Equipe**: grupo estudantil com disponibilidade parcial, conciliando o projeto com outras disciplinas.
- **Orçamento**: zero ou próximo de zero — priorização de ferramentas com camada gratuita (hospedagem, banco de dados).
- **Técnica**: stack definida como Python (back-end) e JavaScript (front-end); ausência de infraestrutura dedicada para automação de coleta de dados no MVP.
- **Legal/institucional**: compartilhamento de "provas antigas" que se repetem entre semestres apresenta risco de conflito com professores — por isso fica fora do escopo do MVP, tratado apenas como trabalho futuro condicionado a uma política de uso definida.
- **Confiabilidade da fonte**: o sistema depende de cadastro manual no MVP, portanto a cobertura de editais está limitada à capacidade operacional da equipe de moderação, não sendo exaustiva.

---

## 7. Faixas de Qualidade (Quality Ranges)

| Atributo | Meta |
|---|---|
| Desempenho | Páginas públicas carregando em até 3 segundos em condições normais de uso |
| Segurança | Comunicação via HTTPS; dados de autenticação/sessão nunca expostos em logs ou mensagens de erro |
| Controle de acesso | No mínimo 4 perfis distintos (usuário, colaborador, moderador, administrador), com permissões diferenciadas |
| Privacidade | Coleta mínima de dados pessoais, com possibilidade de solicitação de exclusão pelo usuário |
| Confiabilidade da informação | Toda publicação institucional deve exibir a data da última verificação conhecida |
| Usabilidade | Usuário comum deve localizar um item de interesse (busca ou filtro) em até 2 minutos |

---

## 8. Precedência e Priorização

1. **Confiabilidade e transparência da informação institucional:** (status correto, fonte visível, data de verificação). É o requisito que sustenta a confiança no produto e não pode ser comprometido em nenhuma fase.
2. **Consulta pública funcional:** dos dois pilares (leitura sem autenticação). Entrega valor mesmo sem nenhum recurso avançado.
3. **Fluxo de contribuição e moderação:** segundo em prioridade, pois depende do primeiro estar estável para não introduzir conteúdo não confiável.
4. **Autenticação e notificações personalizadas:** melhoram a experiência, mas o produto é útil mesmo sem elas.
5. **Automação de coleta de editais** deliberadamente adiada para depois da validação do fluxo manual, por risco técnico e de manutenção.

---

## 9. Outros Requisitos do Produto

- **Padrões aplicáveis**: recomenda-se seguir boas práticas de acessibilidade web (WCAG) como meta de qualidade, ainda que não seja critério obrigatório de aceite no MVP.
- **Requisitos de sistema**: aplicação web responsiva, compatível com navegadores desktop e mobile atuais; back-end em Python 3, front-end em JavaScript; banco de dados relacional (SQLite em desenvolvimento, PostgreSQL em produção).
- **Requisitos de desempenho**: ver seção 7 (Faixas de Qualidade).
- **Requisitos de manutenibilidade**: código organizado por responsabilidades, com testes automatizados cobrindo regras críticas (moderação, estados de publicação), seguindo o fluxo de desenvolvimento orientado a especificação (spec-kit) já adotado pelo grupo.

---

