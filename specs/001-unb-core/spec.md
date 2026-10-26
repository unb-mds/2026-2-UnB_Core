# Feature Specification: UNB CORE

**Feature Branch**: `001-unb-core`

**Created**: 2026-09-09

**Status**: Revisado para a Release 2

**Input**: User description: "Criar uma plataforma acadêmica e institucional para estudantes da UnB, reunindo uma base de conhecimento colaborativa e uma central de editais e avisos oficiais."

## Clarifications

### Session 2026-09-09

- Q: Quem deve poder enviar contribuições acadêmicas para revisão? → A: Somente usuários previamente cadastrados como colaboradores.
- Q: Como um usuário deve se tornar um colaborador cadastrado? → A: Qualquer usuário autenticado é automaticamente colaborador.
- Q: Quem deve poder cadastrar editais na Release 2? → A: Somente administradores podem cadastrar manualmente editais.
- Q: Como um estudante deve criar uma conta para acessar as funções autenticadas? → A: O estudante cria a própria conta.
- Q: Como as publicações institucionais devem ser inseridas no MVP? → A: Administradores cadastram manualmente editais resumidos, sempre mantendo a `url_oficial` para consulta da fonte original.

## User Scenarios & Testing

### User Story 1 - Consultar editais (Priority: P2)

Como estudante da UnB, quero encontrar editais cadastrados manualmente em um só lugar, para consultar um resumo e acessar a fonte oficial da informação.

**Why this priority**: O módulo institucional preserva o diferencial do produto, mas tem escopo complementar ao Tamburetei na Release 2.

**Independent Test**: Pode ser testada cadastrando editais de exemplo, filtrando por categoria ou unidade e verificando se o resumo e a `url_oficial` são exibidos.

**Acceptance Scenarios**:

1. **Given** que existem editais cadastrados, **When** o estudante acessa a Central de Editais, **Then** ele visualiza uma lista organizada.
2. **Given** que um edital possui `url_oficial`, **When** o estudante abre seus detalhes, **Then** ele visualiza o resumo, a unidade responsável, o estado quando disponível e o link oficial.
3. **Given** que o edital pode estar desatualizado, **When** o estudante consulta seus detalhes, **Then** o sistema informa que a fonte oficial prevalece.

---

### User Story 2 - Consultar conteúdos de uma disciplina (Priority: P1)

Como estudante, quero consultar resumos, dicas, dificuldades, provas, implementações e links organizados por curso e disciplina, para apoiar meus estudos.

**Why this priority**: A Base de Conhecimento é o segundo pilar principal do produto e concentra o conhecimento colaborativo do grupo.

**Independent Test**: Pode ser testada selecionando um curso, uma disciplina e uma categoria, e verificando se os conteúdos publicados aparecem com autoria ou origem e data de atualização.

**Acceptance Scenarios**:

1. **Given** que existem conteúdos publicados, **When** o estudante seleciona um curso e uma disciplina, **Then** ele visualiza os conteúdos disponíveis para aquela disciplina.
2. **Given** que existem diferentes tipos de conteúdo, **When** o estudante escolhe uma categoria, **Then** a lista é filtrada pelo tipo selecionado.
3. **Given** que um conteúdo foi publicado, **When** o estudante abre seus detalhes, **Then** ele visualiza a disciplina, o tipo, a autoria ou origem e a data de atualização.
4. **Given** que não existem conteúdos para o filtro selecionado, **When** o estudante realiza a consulta, **Then** o sistema informa que não há resultados e apresenta a possibilidade de contribuir.

---

### User Story 3 - Enviar e acompanhar uma contribuição (Priority: P2)

Como usuário autenticado, quero enviar uma contribuição associada a um curso, disciplina e categoria, para compartilhar conhecimento com outros estudantes sem publicação imediata.

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

### User Story 4 - Moderar conteúdos e administrar informações (Priority: P2)

Como moderador ou administrador, quero revisar contribuições acadêmicas e cadastrar editais básicos, para preservar a qualidade do conteúdo e direcionar usuários às fontes oficiais.

**Why this priority**: A moderação é necessária para que conteúdos compartilhados não sejam publicados sem revisão; os editais da Release 2 serão apenas registros manuais de consulta.

**Independent Test**: Pode ser testada com perfis autorizados e não autorizados, verificando decisões de moderação, justificativas e bloqueio de operações indevidas.

**Acceptance Scenarios**:

1. **Given** que existe uma contribuição pendente, **When** um moderador aprova, rejeita, arquiva ou solicita ajustes, **Then** o estado da contribuição é atualizado conforme a decisão.
2. **Given** que uma decisão exige explicação, **When** o moderador registra a decisão, **Then** a justificativa fica vinculada à contribuição.
3. **Given** que um usuário comum tenta acessar uma operação de moderação, **When** ele realiza a tentativa, **Then** o acesso é negado.
4. **Given** que um usuário não é administrador, **When** ele tenta cadastrar um edital, **Then** o acesso é negado.
5. **Given** que um administrador consulta uma fonte oficial, **When** ele cadastra um edital, **Then** o registro mantém o resumo e a `url_oficial`.
6. **Given** que um moderador consulta uma contribuição, **When** ele realiza uma decisão permitida, **Then** somente o registro correspondente é alterado.

### Edge Cases

- Um edital pode não informar prazo.
- A fonte oficial pode conter informações mais atuais que o resumo armazenado.
- Uma contribuição pode não possuir fonte, conter material ofensivo ou utilizar material potencialmente protegido.
- Uma busca pode não retornar resultados.
- Um usuário pode tentar acessar uma função sem a permissão necessária.

## Requirements

### Functional Requirements

- **FR-001**: O sistema MUST apresentar acesso separado para a Base de Conhecimento e para a Central de Editais.
- **FR-002**: O sistema MUST permitir navegar por curso, disciplina e tipo de conteúdo.
- **FR-003**: O sistema MUST permitir consultar editais por categoria e unidade responsável, quando esses dados estiverem disponíveis.
- **FR-004**: O sistema MUST permitir pesquisar conteúdos da Base de Conhecimento; a busca institucional integrada fica fora da Release 2.
- **FR-005**: O sistema MUST exibir o resumo, a unidade responsável, o estado quando disponível e a `url_oficial` de cada edital.
- **FR-006**: O sistema MUST permitir que somente usuários autenticados enviem contribuições acadêmicas.
- **FR-007**: O sistema MUST manter novas contribuições pendentes até a revisão de um moderador autorizado.
- **FR-008**: O sistema MUST permitir que moderadores aprovem, rejeitem, arquivem ou devolvam contribuições para ajustes.
- **FR-009**: O sistema MUST preservar a justificativa das decisões de moderação quando ela for registrada.
- **FR-010**: O sistema MUST disponibilizar orientações sobre qualidade, escopo permitido, autoria e fontes para a primeira contribuição.
- **FR-011**: A consulta básica de conteúdos e editais MUST estar disponível sem autenticação.
- **FR-012**: O sistema MUST impedir que usuários sem autorização publiquem ou alterem diretamente conteúdos moderados.
- **FR-013**: O sistema MUST apresentar mensagens compreensíveis para estados vazios, erros de acesso e envios incompletos.
- **FR-014**: O sistema MUST preservar o vínculo de cada informação acadêmica com o colaborador responsável e cada edital com sua `url_oficial`.
- **FR-015**: O sistema MUST permitir que somente administradores cadastrem manualmente editais.
- **FR-016**: O sistema MUST permitir que estudantes criem a própria conta para acessar as funções autenticadas.
- **FR-017**: O sistema MUST exigir título, resumo, categoria, unidade responsável e `url_oficial` para cadastrar um edital.
- **FR-018**: O sistema MUST exigir curso, disciplina, tipo e conteúdo ou URL para enviar uma contribuição; `conteudo_id` será informado somente quando a contribuição alterar conteúdo existente.
- **FR-019**: O sistema MUST permitir busca de editais por título ou resumo e filtros por categoria, unidade e estado quando disponíveis.
- **FR-020**: O sistema MUST rejeitar o cadastro de edital ou contribuição incompleto antes de criar um registro parcial, informando os campos ausentes.
- **FR-021**: O sistema MUST oferecer nomes acessíveis, foco visível e navegação por teclado nos fluxos principais de consulta, busca, contribuição e moderação.
- **FR-022**: O MVP deve considerar os principais navegadores desktop atuais e as versões móveis atuais de Chrome e Safari, sem exigir suporte a versões antigas específicas.
- **FR-023**: O sistema MUST exigir nome, e-mail e senha para criar uma conta, com e-mail único para cada conta.
- **FR-024**: O sistema MUST impedir que senhas apareçam em respostas da API, mensagens de erro ou registros de operação.
- **FR-025**: O sistema MUST apresentar nas mensagens de erro a causa do problema e, quando aplicável, a orientação para corrigi-lo ou tentar novamente.

### Key Entities

- **Usuário**: pessoa que consulta informações ou, quando autenticada, pode salvar preferências e enviar contribuições; funções de moderação e administração dependem de autorização específica.
- **Curso**: agrupamento de disciplinas e referência para organização dos interesses acadêmicos.
- **Disciplina**: unidade curricular pertencente a um curso.
- **Conteúdo acadêmico**: material publicado na Base de Conhecimento, como resumo, dica, dificuldade, prova, implementação ou link.
- **Contribuição**: proposta de criação ou alteração de conteúdo acadêmico que passa por estados de revisão.
- **Publicação institucional**: edital cadastrado manualmente com título, resumo, categoria, unidade responsável, estado quando disponível e `url_oficial`.
- **Relato acadêmico**: relato autenticado de problema relacionado a um conteúdo acadêmico, encaminhado para análise.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Em uma demonstração, um estudante consegue encontrar um edital usando lista ou filtros básicos e acessar sua fonte oficial.
- **SC-002**: Em uma demonstração, um estudante consegue localizar conteúdos de uma disciplina selecionando curso, disciplina e categoria.
- **SC-003**: 100% das contribuições enviadas durante os testes permanecem pendentes até uma decisão de moderação.
- **SC-004**: 100% das decisões de moderação realizadas durante os testes resultam no estado correspondente e preservam a justificativa quando informada.
- **SC-005**: Usuários sem permissão não conseguem executar operações de moderação ou administração durante os testes.
- **SC-006**: Os editais exibem a `url_oficial` e informam que a fonte oficial prevalece em caso de divergência.
- **SC-007**: Os fluxos principais de consulta, busca e envio de contribuição podem ser realizados por teclado.

## Assumptions

- O foco inicial da Base de Conhecimento será Engenharia de Software.
- A consulta pública não exige autenticação.
- A publicação de contribuições depende de revisão humana.
- A Central de Editais manterá a `url_oficial` para consulta da fonte original da UnB.
- Relatos acadêmicos exigem autenticação no MVP; cadastro de conta, verificação de e-mail e recuperação de senha ficam fora do escopo inicial.
- O sistema será desenvolvido como projeto acadêmico de escopo reduzido, sem metas de desempenho, capacidade ou infraestrutura avançada.
- Hospedagem será detalhada durante o planejamento técnico, sem alterar os fluxos principais desta especificação.
- Qualquer usuário autenticado será considerado colaborador e poderá enviar contribuições para revisão.
- Somente administradores poderão cadastrar manualmente editais.
- Estudantes poderão criar a própria conta sem aprovação prévia de um administrador.
- No MVP, as publicações institucionais serão cadastradas manualmente por administradores a partir das fontes oficiais.
