# Feature Specification: UNB CORE

**Feature Branch**: `001-unb-core`

**Created**: 2026-09-09

**Status**: Draft

**Input**: User description: "Criar uma plataforma acadêmica colaborativa para estudantes da UnB, reunindo conteúdos organizados por curso e disciplina e um fluxo de contribuições moderadas."

## Clarifications

### Session 2026-09-09

- Q: Quem deve poder enviar contribuições acadêmicas para revisão? → A: Somente usuários previamente cadastrados como colaboradores.
- Q: Como um usuário deve se tornar um colaborador cadastrado? → A: Qualquer usuário autenticado é automaticamente colaborador.
- Q: Como um estudante deve criar uma conta para acessar as funções autenticadas? → A: O estudante cria a própria conta.
- Q: O corte de escopo deve remover o módulo institucional do MVP? → A: Sim, remover todo o módulo institucional, incluindo editais, fontes, categorias institucionais, denúncias relacionadas e busca unificada.
- Q: Quem deve poder moderar contribuições acadêmicas no MVP reduzido? → A: Moderadores e administradores.
- Q: Quais tipos de conteúdo devem permanecer no MVP da Base de Conhecimento? → A: Resumo, dica, dificuldade, prova, implementação e link.
- Q: O que deve acontecer quando uma contribuição for aprovada? → A: Criar novo conteúdo ou atualizar o existente conforme `conteudo_id`.
- Q: Como os perfis de moderador e administrador serão criados no MVP? → A: Poderão ser pré-cadastrados no banco e também criados por uma tela administrativa.

## User Scenarios & Testing

### User Story 1 - Consultar conteúdos de uma disciplina (Priority: P1)

Como estudante, quero consultar resumos, dicas, dificuldades, provas, implementações e links organizados por curso e disciplina, para apoiar meus estudos.

**Why this priority**: A Base de Conhecimento é o segundo pilar principal do produto e concentra o conhecimento colaborativo do grupo.

**Independent Test**: Pode ser testada selecionando um curso, uma disciplina e um tipo, e verificando se os conteúdos publicados aparecem com autoria ou origem e data de atualização.

**Acceptance Scenarios**:

1. **Given** que existem conteúdos publicados, **When** o estudante seleciona um curso e uma disciplina, **Then** ele visualiza os conteúdos disponíveis para aquela disciplina.
2. **Given** que existem diferentes tipos de conteúdo, **When** o estudante escolhe um tipo, **Then** a lista é filtrada pelo tipo selecionado.
3. **Given** que um conteúdo foi publicado, **When** o estudante abre seus detalhes, **Then** ele visualiza a disciplina, o tipo, a autoria ou origem e a data de atualização.
4. **Given** que não existem conteúdos para o filtro selecionado, **When** o estudante realiza a consulta, **Then** o sistema informa que não há resultados e apresenta a possibilidade de contribuir.

---

### User Story 2 - Enviar e acompanhar uma contribuição (Priority: P2)

Como usuário autenticado, quero enviar uma contribuição associada a um curso, disciplina e tipo, para compartilhar conhecimento com outros estudantes sem publicação imediata.

**Why this priority**: A colaboração amplia o valor da plataforma, mas depende da existência de uma base consultável e de um processo de revisão.

**Independent Test**: Pode ser testada preenchendo uma contribuição válida, enviando-a e verificando que ela fica pendente e pode ser acompanhada pelo autor.

**Acceptance Scenarios**:

1. **Given** que o usuário está autenticado e possui as informações obrigatórias, **When** ele envia uma contribuição, **Then** a contribuição é registrada como pendente.
2. **Given** que a contribuição está pendente, **When** o colaborador consulta seu envio, **Then** ele visualiza o estado atual da contribuição.
3. **Given** que a contribuição precisa de ajustes, **When** um moderador devolve o envio com uma justificativa, **Then** o colaborador visualiza a orientação para correção.
4. **Given** que faltam informações obrigatórias, **When** o colaborador tenta enviar o formulário, **Then** o sistema informa os campos que precisam ser preenchidos.
5. **Given** que o usuário não está autenticado, **When** ele tenta enviar uma contribuição, **Then** o sistema impede o envio e informa que é necessário entrar em uma conta.
6. **Given** que o estudante ainda não possui uma conta, **When** ele realiza o cadastro, **Then** sua conta é criada e ele pode acessar as funções permitidas a usuários autenticados.

---

### User Story 3 - Moderar conteúdos (Priority: P2)

Como moderador ou administrador, quero revisar contribuições acadêmicas, para preservar a qualidade e a confiabilidade da Base de Conhecimento.

**Why this priority**: A moderação é necessária para que os conteúdos compartilhados não sejam publicados sem revisão.

**Independent Test**: Pode ser testada com perfis autorizados e não autorizados, verificando decisões de moderação, justificativas e bloqueio de operações indevidas.

**Acceptance Scenarios**:

1. **Given** que existe uma contribuição pendente, **When** um moderador aprova, rejeita, arquiva ou solicita ajustes, **Then** o estado da contribuição é atualizado conforme a decisão.
2. **Given** que uma decisão exige explicação, **When** o moderador registra a decisão, **Then** a justificativa fica vinculada à contribuição.
3. **Given** que um usuário comum tenta acessar uma operação de moderação, **When** ele realiza a tentativa, **Then** o acesso é negado.
4. **Given** que um moderador consulta uma contribuição, **When** ele realiza uma decisão permitida, **Then** somente o registro correspondente é alterado.

### Edge Cases

- Uma contribuição pode não possuir fonte, conter material ofensivo ou utilizar material potencialmente protegido.
- Uma consulta pode não retornar resultados.
- Um usuário pode tentar acessar uma função sem a permissão necessária.

## Requirements

### Functional Requirements

- **FR-001**: O sistema MUST permitir navegar por curso, disciplina e tipo de conteúdo, considerando os tipos resumo, dica, dificuldade, prova, implementação e link.
- **FR-002**: O sistema MUST permitir pesquisar e filtrar conteúdos acadêmicos por curso, disciplina e tipo.
- **FR-003**: O sistema MUST permitir que somente usuários autenticados enviem contribuições associadas a curso, disciplina e tipo de conteúdo.
- **FR-004**: O sistema MUST manter novas contribuições pendentes até a revisão de um moderador autorizado.
- **FR-005**: O sistema MUST permitir que moderadores e administradores aprovem, rejeitem, arquivem ou devolvam contribuições para ajustes.
- **FR-006**: O sistema MUST preservar a justificativa das decisões de moderação quando ela for registrada.
- **FR-007**: Ao aprovar uma contribuição sem `conteudo_id`, o sistema MUST criar um novo conteúdo publicado; ao aprovar uma contribuição com `conteudo_id`, MUST atualizar o conteúdo correspondente.
- **FR-008**: O sistema MUST disponibilizar, antes do primeiro envio, orientações visíveis sobre qualidade, escopo permitido, autoria e fontes, e MUST permitir que o usuário as consulte novamente durante o preenchimento.
- **FR-009**: A consulta básica de conteúdos MUST estar disponível sem autenticação.
- **FR-010**: O sistema MUST impedir que usuários sem autorização publiquem ou alterem diretamente conteúdos moderados.
- **FR-011**: O sistema MUST apresentar mensagens compreensíveis para estados vazios, erros de acesso e envios incompletos.
- **FR-012**: O sistema MUST preservar o vínculo de cada conteúdo com o colaborador responsável e sua origem quando informada.
- **FR-013**: O sistema MUST permitir que estudantes criem a própria conta para acessar as funções autenticadas.
- **FR-014**: O sistema MUST exigir curso, disciplina, tipo e conteúdo ou URL para enviar uma contribuição; `conteudo_id` será informado somente quando a contribuição alterar conteúdo existente.
- **FR-015**: O sistema MUST rejeitar o envio de contribuição incompleto antes de criar um registro parcial, informando os campos ausentes.
- **FR-016**: O sistema MUST oferecer nomes acessíveis, foco visível e navegação por teclado nos fluxos principais de consulta, busca, contribuição e moderação.
- **FR-017**: O MVP MUST ser validado na versão estável mais recente de Chrome, Edge e Firefox em desktop e na versão estável mais recente de Chrome para Android e Safari para iOS disponível no ciclo de validação, sem exigir suporte a versões antigas específicas.
- **FR-018**: O sistema MUST exigir nome, e-mail e senha para criar uma conta, e-mail único para cada conta.
- **FR-019**: O sistema MUST impedir que senhas apareçam em respostas da API, mensagens de erro ou registros de operação.
- **FR-020**: O sistema MUST apresentar nas mensagens de erro a causa do problema e, quando aplicável, a orientação para corrigi-lo ou tentar novamente.
- **FR-021**: O sistema MUST permitir que administradores criem usuários com perfil de moderador ou administrador por uma tela administrativa, mantendo também a possibilidade de pré-cadastro por banco ou seed de desenvolvimento.

### Key Entities

- **Usuário**: pessoa que consulta informações ou, quando autenticada, pode salvar preferências e enviar contribuições; funções de moderação e administração dependem de autorização específica.
- **Curso**: agrupamento de disciplinas e referência para organização dos interesses acadêmicos.
- **Disciplina**: unidade curricular pertencente a um curso.
- **Conteúdo acadêmico**: material publicado na Base de Conhecimento, como resumo, dica, dificuldade, prova, implementação ou link.
- **Contribuição**: proposta de criação ou alteração de conteúdo acadêmico que passa por estados de revisão.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Em uma demonstração, um estudante consegue localizar conteúdos de uma disciplina selecionando curso, disciplina e tipo.
- **SC-002**: 100% das contribuições enviadas durante os testes permanecem pendentes até uma decisão de moderação.
- **SC-003**: 100% das decisões de moderação realizadas durante os testes resultam no estado correspondente, preservam a justificativa quando informada e refletem aprovações no conteúdo publicado.
- **SC-004**: Usuários sem permissão não conseguem executar operações de moderação durante os testes.
- **SC-005**: Os fluxos principais de consulta, busca e envio de contribuição podem ser realizados por teclado.

## Assumptions

- O foco inicial da Base de Conhecimento será Engenharia de Software.
- A consulta pública não exige autenticação.
- A publicação de contribuições depende de revisão humana.
- Cadastro de conta, verificação de e-mail e recuperação de senha ficam fora do escopo inicial.
- O sistema será desenvolvido como projeto acadêmico de escopo reduzido, sem metas de desempenho, capacidade ou infraestrutura avançada.
- Autenticação e hospedagem serão detalhadas durante o planejamento técnico, sem alterar os fluxos principais desta especificação.
- Qualquer usuário autenticado será considerado colaborador e poderá enviar contribuições para revisão.
- Moderadores e administradores poderão revisar contribuições; usuários comuns não poderão executar decisões de moderação.
- Perfis de moderador e administrador poderão ser preparados por seed ou banco e criados posteriormente por administradores autorizados.
- Estudantes poderão criar a própria conta sem aprovação prévia de um administrador.
