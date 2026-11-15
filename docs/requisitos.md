# Documento de Requisitos do Produto

## UNB CORE

**Projeto:** Métodos de Desenvolvimento de Software 2026/2  
**Curso:** Engenharia de Software - 2026.2  
**Equipe:** G1

## 1. Visão geral

O UNB CORE é uma plataforma acadêmica colaborativa da Universidade de Brasília (UnB). O sistema reúne, na **Base de Conhecimento**, resumos, dicas, dificuldades comuns, provas, implementações e links úteis organizados por curso e disciplina.

Os conteúdos são enviados pelos próprios estudantes como **contribuições** e só são publicados depois da revisão de um moderador ou administrador.

O objetivo é reduzir a dispersão do conhecimento acadêmico e facilitar que estudantes aprendam com quem já cursou as disciplinas. O MVP atende somente os cursos do **campus do Gama**, que pertencem à unidade **FCTE - Faculdade de Ciências e Tecnologias em Engenharia**.

A plataforma não substitui os canais oficiais da UnB. Em caso de divergência sobre cursos ou disciplinas, a informação oficial do SIGAA prevalece.

## 2. Público-alvo

- Estudantes de graduação dos cursos da FCTE (campus do Gama).
- Veteranos interessados em compartilhar conhecimento.
- Moderadores e administradores responsáveis pela qualidade dos conteúdos.

## 3. Escopo do produto

### 3.1 Incluído no escopo

- Consulta pública de conteúdos acadêmicos publicados.
- Organização por curso, disciplina e tipo de conteúdo.
- Cursos e disciplinas da FCTE (campus do Gama), carregados a partir das páginas públicas do SIGAA.
- Cadastro de conta e login local.
- Envio, acompanhamento e edição de contribuições pelo autor.
- Revisão e moderação das contribuições antes da publicação.
- Guia de primeira contribuição.
- Gestão de usuários e perfis por administradores.

### 3.2 Fora do escopo

Itens removidos no corte de escopo de 26/10/2026 (issue #126, branch `feature/corte-escopo-academico`):

- Central de Editais, editais e publicações institucionais.
- Fontes institucionais e categorias institucionais.
- Denúncias e relatos sobre conteúdos.
- Busca unificada entre módulos.
- Coleta automática de informações institucionais (editais, comunicados).

Itens que nunca fizeram parte do escopo:

- Cursos de outros campi da UnB (Darcy Ribeiro, Ceilândia, Planaltina).
- Substituir os sistemas oficiais da UnB.
- Verificação de e-mail, recuperação de senha e login institucional da UnB.
- Tutoria individual, chat ou correção automática de exercícios.
- Publicar contribuições sem revisão humana.
- Criar uma rede social geral entre estudantes.

## 4. Requisitos funcionais

### RF-001 - Organização acadêmica

O sistema deve permitir navegar por curso, disciplina e tipo de conteúdo. Os tipos de conteúdo são: resumo, dica, dificuldade, prova, implementação e link.

### RF-002 - Escopo de campus

O sistema deve listar somente os cursos da FCTE (campus do Gama). Cursos com o mesmo nome oferecidos em outros campi não devem aparecer.

### RF-003 - Filtros da Base de Conhecimento

O sistema deve permitir filtrar os conteúdos publicados por curso, disciplina e tipo de conteúdo. Quando não houver resultados, o sistema deve informar isso e oferecer a opção de contribuir.

### RF-004 - Consulta de conteúdo

O sistema deve exibir, para cada conteúdo publicado, a disciplina, o tipo, a autoria ou origem e a data de atualização.

### RF-005 - Acesso público

A consulta de cursos, disciplinas e conteúdos publicados deve estar disponível sem autenticação.

### RF-006 - Cadastro de conta

O sistema deve permitir que estudantes criem a própria conta com nome, e-mail e senha, sem aprovação prévia. Cada e-mail só pode ser usado em uma conta.

### RF-007 - Envio de contribuições

Somente usuários autenticados podem enviar contribuições. O envio deve exigir curso, disciplina, tipo, título e conteúdo ou URL. O vínculo com um conteúdo existente (`conteudo_id`) é informado somente quando a contribuição altera um conteúdo já publicado.

### RF-008 - Acompanhamento de contribuições

O autor deve poder consultar a lista das próprias contribuições, com o estado atual, as datas de envio e de atualização e a justificativa da moderação, quando houver.

### RF-009 - Edição de contribuições

O autor deve poder editar o tipo, o título, o conteúdo ou URL e a fonte das próprias contribuições. Após a edição, a contribuição volta para o estado pendente e passa por nova revisão. Um usuário não pode editar contribuições de outra pessoa.

### RF-010 - Revisão obrigatória

Contribuições novas ou editadas devem permanecer pendentes até a decisão de um moderador ou administrador.

### RF-011 - Moderação

Moderadores e administradores devem poder aprovar, rejeitar, arquivar ou devolver contribuições para ajustes. A justificativa da decisão deve ser preservada quando informada.

### RF-012 - Publicação derivada

Ao aprovar uma contribuição sem `conteudo_id`, o sistema deve criar um novo conteúdo publicado. Ao aprovar uma contribuição com `conteudo_id`, o sistema deve atualizar o conteúdo correspondente.

### RF-013 - Guia de contribuição

O sistema deve disponibilizar, antes do primeiro envio, orientações sobre qualidade, escopo permitido, autoria e fontes. O usuário deve poder consultar essas orientações novamente durante o preenchimento.

### RF-014 - Gestão de usuários

Administradores devem poder listar usuários, criar contas com perfil de moderador ou administrador, alterar perfis e ativar ou desativar contas. Perfis administrativos também podem ser pré-cadastrados por seed de desenvolvimento.

### RF-015 - Proteção contra autobloqueio

Um administrador não pode desativar a própria conta nem remover o próprio perfil de administrador, para não perder o acesso necessário para desfazer a alteração.

### RF-016 - Permissões

O sistema deve impedir que usuários sem autorização publiquem ou alterem diretamente conteúdos, executem decisões de moderação ou acessem funções administrativas.

### RF-017 - Rastreabilidade

O sistema deve preservar o vínculo de cada conteúdo com o colaborador responsável e com a origem informada.

### RF-018 - Validação de dados

O sistema deve rejeitar envios incompletos antes de criar registros parciais e informar quais campos estão ausentes.

### RF-019 - Mensagens de estado

O sistema deve apresentar mensagens que informem a causa do problema e, quando aplicável, orientem como corrigi-lo ou tentar novamente. Isso vale para estados vazios, erros de acesso, falhas de conexão e envios incompletos.

## 5. Requisitos não funcionais

### RNF-001 - Segurança de acesso

O sistema deve diferenciar os perfis de usuário, moderador e administrador. Qualquer usuário autenticado pode contribuir. Operações de moderação e administração não autorizadas devem ser negadas.

### RNF-002 - Privacidade

O sistema deve coletar somente os dados necessários para conta, autoria e moderação. Senhas não podem aparecer em respostas da API, mensagens de erro ou registros de operação.

### RNF-003 - Acessibilidade

Os fluxos principais de consulta, contribuição e moderação devem oferecer nomes acessíveis, foco visível e navegação por teclado.

### RNF-004 - Compatibilidade

O MVP deve funcionar na versão estável mais recente de Chrome, Edge e Firefox em desktop e de Chrome para Android e Safari para iOS. O layout deve se adaptar a telas pequenas, sem textos saindo dos componentes.

### RNF-005 - Confiabilidade da informação

Cursos e disciplinas devem ter origem nas páginas públicas do SIGAA. Conteúdos acadêmicos só são publicados após revisão humana.

### RNF-006 - Manutenibilidade

O código deve ser organizado por responsabilidades e possuir testes automatizados para as regras mais importantes do sistema.

### RNF-007 - Documentação

O repositório deve conter instruções básicas de configuração, execução e contribuição do projeto.

Não fazem parte deste projeto metas de desempenho, capacidade, escalabilidade ou infraestrutura avançada.

## 6. Cenários de uso prioritários

### Cenário 1: Consultar uma disciplina

1. O estudante acessa a Base de Conhecimento.
2. Seleciona um curso da FCTE e uma disciplina.
3. Escolhe um tipo de conteúdo.
4. Consulta resumos, dicas, provas ou dificuldades comuns.
5. Encontra a opção de contribuir caso o conteúdo ainda não exista.

### Cenário 2: Enviar uma contribuição

1. O estudante cria uma conta ou entra na conta existente.
2. Consulta o guia de primeira contribuição.
3. Preenche o formulário com curso, disciplina, tipo, título, conteúdo e fonte.
4. Envia a contribuição, que fica pendente de revisão.

### Cenário 3: Acompanhar e ajustar uma contribuição

1. O autor acessa "Minhas contribuições".
2. Consulta o estado de cada envio e a orientação da moderação, quando houver.
3. Edita a contribuição para atender às orientações.
4. A contribuição volta para pendente e passa por nova revisão.

### Cenário 4: Moderar uma contribuição

1. O moderador acessa a fila de contribuições pendentes.
2. Analisa o conteúdo e a fonte.
3. Aprova, rejeita, arquiva ou solicita ajustes, registrando uma justificativa.
4. Na aprovação, o conteúdo é publicado ou atualizado na Base de Conhecimento.

## 7. Casos de exceção

- Formulário enviado sem informações obrigatórias.
- Consulta sem resultados.
- Contribuição com material sem fonte, ofensivo ou potencialmente protegido.
- Usuário tentando acessar uma função sem permissão.
- Usuário tentando editar a contribuição de outra pessoa.
- Administrador tentando desativar a própria conta ou remover o próprio perfil.
- Cadastro de conta com e-mail já utilizado.
- API ou SIGAA temporariamente indisponíveis.

## 8. Entidades principais

### Usuário

Pessoa que consulta informações e pode criar uma conta. Possui um perfil: usuário, moderador ou administrador. Usuários autenticados podem enviar contribuições; moderadores e administradores possuem permissões adicionais. Uma conta pode estar ativa ou desativada.

### Curso

Curso de graduação da FCTE (campus do Gama), com nome, sigla da unidade e grau (bacharelado ou licenciatura). Agrupa disciplinas.

### Disciplina

Unidade curricular que pertence a um curso e organiza os conteúdos acadêmicos.

### Conteúdo acadêmico

Material publicado na Base de Conhecimento: resumo, dica, dificuldade, prova, implementação ou link. Pode estar publicado ou arquivado.

### Contribuição

Proposta de criação ou alteração de conteúdo acadêmico enviada por um usuário. Passa pelos estados pendente, ajustes, aprovada, rejeitada e arquivada.

## 9. Arquitetura e tecnologias definidas

A solução é uma aplicação web simples, adequada ao escopo do projeto da disciplina.

- **Front-end:** React com Vite, HTML, CSS e JavaScript.
- **Back-end:** Python com FastAPI.
- **Banco de dados:** PostgreSQL, com SQLModel para os modelos e Alembic para as migrations.
- **Autenticação:** cadastro e login locais com token JWT, sem integração com o login institucional da UnB.
- **Dados acadêmicos:** cursos e disciplinas coletados das páginas públicas do SIGAA na primeira inicialização da API.
- **Execução:** ambiente local ou Docker Compose (banco, backend e frontend).
- **Organização:** separação entre interface, regras do sistema, persistência de dados e testes.

## 10. Critérios de validação

- Usuários conseguem consultar cursos, disciplinas e conteúdos publicados sem autenticação.
- Somente cursos da FCTE aparecem nos filtros.
- Contribuições novas e editadas permanecem pendentes até uma decisão de moderação.
- O autor consegue ver o estado e editar as próprias contribuições, mas não as de outros usuários.
- Cada decisão de moderação altera o estado esperado da contribuição e preserva a justificativa informada.
- Aprovações criam ou atualizam o conteúdo publicado correspondente.
- Usuários comuns não acessam operações de moderação ou administração.
- Um administrador não consegue desativar a própria conta.
- O sistema apresenta a causa e uma orientação quando ocorre uma falha.
- Os fluxos principais podem ser realizados por teclado.

## 11. Correspondência com a especificação

| Requisito | `specs/001-unb-core/spec.md` |
|---|---|
| RF-001, RF-003 | FR-001, FR-002 |
| RF-004, RF-017 | FR-012 |
| RF-005 | FR-009 |
| RF-006 | FR-013, FR-018 |
| RF-007, RF-018 | FR-003, FR-014, FR-015 |
| RF-010 | FR-004 |
| RF-011 | FR-005, FR-006 |
| RF-012 | FR-007 |
| RF-013 | FR-008 |
| RF-014 | FR-021 |
| RF-016 | FR-010 |
| RF-019 | FR-011, FR-020 |
| RNF-002 | FR-019 |
| RNF-003 | FR-016 |
| RNF-004 | FR-017 |
| RF-002 | FR-022 |
| RF-008 | FR-023 |
| RF-009 | FR-024 |
| RF-015 | FR-025 |

## 12. Histórico de alterações

| Data | Alteração |
|---|---|
| 26/10/2026 | Corte de escopo: remoção da Central de Editais, das publicações institucionais, das fontes, das denúncias e da busca unificada. |
| 15/11/2026 | Refatoração do documento para o escopo acadêmico. Inclusão do recorte do campus do Gama (FCTE), da edição de contribuições e da proteção contra autobloqueio do administrador. |

## 13. Observação final

O UNB CORE deve priorizar clareza, precisão e transparência. Quando uma informação não puder ser confirmada, o sistema deve mostrar essa limitação claramente em vez de presumir que o conteúdo continua válido.
