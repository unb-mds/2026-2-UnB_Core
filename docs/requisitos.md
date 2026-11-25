# Documento de Requisitos do Produto

## UNB CORE

**Projeto:** Métodos de Desenvolvimento de Software 2026/2  
**Curso:** Engenharia de Software - 2026.2  
**Equipe:** G1  
**Última atualização:** 25/11/2026

## 1. Visão geral

O UNB CORE é uma plataforma acadêmica colaborativa da Universidade de Brasília (UnB). O sistema reúne, na **Base de Conhecimento**, resumos, dicas, dificuldades comuns, implementações e links úteis organizados por curso e disciplina.

Os conteúdos são enviados pelos próprios estudantes como **contribuições** e só são publicados depois da revisão de um moderador ou administrador.

O objetivo é reduzir a dispersão do conhecimento acadêmico e facilitar que estudantes aprendam com quem já cursou as disciplinas. O MVP atende os **cursos de graduação da UnB** disponíveis nas páginas públicas do SIGAA. O projeto começou restrito ao campus do Gama (FCTE) e foi ampliado em 21/11/2026.

A plataforma não substitui os canais oficiais da UnB. Em caso de divergência sobre cursos ou disciplinas, a informação oficial do SIGAA prevalece.

O site está publicado em https://unb-core.vercel.app.

## 2. Público-alvo

- Estudantes de graduação da UnB.
- Veteranos interessados em compartilhar conhecimento.
- Moderadores e administradores responsáveis pela qualidade dos conteúdos e pela gestão das contas.

## 3. Escopo do produto

### 3.1 Incluído no escopo

- Consulta pública de conteúdos acadêmicos publicados, com página própria para cada conteúdo.
- Organização e filtros por curso, disciplina e tipo de conteúdo.
- Cursos e disciplinas de graduação da UnB, carregados a partir das páginas públicas do SIGAA.
- Cadastro de conta, login local e edição dos próprios dados (Meu perfil).
- Recuperação de senha atendida por um administrador, com senha temporária.
- Envio, acompanhamento, edição e exclusão de contribuições pelo autor.
- Revisão e moderação das contribuições antes da publicação, incluindo pedidos de exclusão.
- Guia de primeira contribuição.
- Gestão de contas por administradores (todas as contas) e por moderadores (usuários comuns), incluindo a exclusão de contas.

### 3.2 Fora do escopo

Itens removidos no corte de escopo de 26/10/2026 (issue #126, branch `feature/corte-escopo-academico`):

- Central de Editais, editais e publicações institucionais.
- Fontes institucionais e categorias institucionais.
- Denúncias e relatos sobre conteúdos (as telas restantes foram removidas em 24/11/2026, PR #177).
- Busca unificada entre módulos.
- Coleta automática de informações institucionais (editais, comunicados).

Itens que nunca fizeram parte do escopo:

- Cursos de pós-graduação e de extensão.
- Substituir os sistemas oficiais da UnB.
- Verificação de e-mail, envio de e-mails (inclusive de recuperação de senha) e login institucional da UnB.
- Tutoria individual, chat ou correção automática de exercícios.
- Publicar contribuições sem revisão humana.
- Criar uma rede social geral entre estudantes.

## 4. Requisitos funcionais

### RF-001 - Organização acadêmica

O sistema deve permitir navegar por curso, disciplina e tipo de conteúdo. Os tipos que podem ser enviados são resumo, dica, dificuldade, implementação e link. O tipo prova existe no modelo de dados, mas o envio de provas não é aceito no momento (ver a seção 11).

### RF-002 - Cursos atendidos

O sistema deve listar os cursos de graduação da UnB disponíveis nas páginas públicas do SIGAA, cada um com as disciplinas da sua estrutura curricular. Cursos com o mesmo nome e graus diferentes (bacharelado e licenciatura) devem aparecer separados.

### RF-003 - Filtros da Base de Conhecimento

O sistema deve mostrar todos os conteúdos publicados sem exigir a escolha de curso ou disciplina, e permitir filtrá-los por curso, disciplina e tipo e ordená-los do mais recente ao mais antigo ou o contrário. Quando não houver resultados, o sistema deve informar isso e oferecer a opção de contribuir.

### RF-004 - Consulta de conteúdo

O sistema deve exibir, para cada conteúdo publicado, a disciplina, o tipo, a autoria ou origem e a data de atualização. Cada conteúdo deve ter um endereço próprio, que pode ser aberto e recarregado diretamente.

### RF-005 - Acesso público

A consulta de cursos, disciplinas e conteúdos publicados deve estar disponível sem autenticação.

### RF-006 - Cadastro de conta

O sistema deve permitir que estudantes criem a própria conta com nome, e-mail e senha de pelo menos 8 caracteres, sem aprovação prévia. Cada e-mail só pode ser usado em uma conta.

### RF-007 - Envio de contribuições

Somente usuários autenticados podem enviar contribuições. O envio deve exigir disciplina, tipo, título e conteúdo ou URL. O curso é opcional e serve só para filtrar a busca de disciplinas. O vínculo com um conteúdo existente (`conteudo_id`) é informado somente quando a contribuição altera um conteúdo já publicado.

### RF-008 - Acompanhamento de contribuições

O autor deve poder consultar a lista das próprias contribuições, com o estado atual, as datas de envio e de atualização e a justificativa da moderação, quando houver.

### RF-009 - Edição de contribuições

O autor deve poder editar o tipo, o título, o conteúdo ou URL e a fonte das próprias contribuições. Após a edição, a contribuição volta para o estado pendente e passa por nova revisão. Um usuário não pode editar contribuições de outra pessoa.

### RF-010 - Revisão obrigatória

Contribuições novas ou editadas devem permanecer pendentes até a decisão de um moderador ou administrador.

### RF-011 - Moderação

Moderadores e administradores devem poder aprovar, rejeitar, arquivar ou devolver contribuições para ajustes, a partir de uma lista com as abas "Para revisar", "Pedidos de exclusão" e "Todas" e de uma página de detalhe para cada contribuição. A justificativa é obrigatória ao solicitar ajustes; a tela de moderação também a exige ao rejeitar. A justificativa informada deve ser preservada e mostrada ao autor.

### RF-012 - Publicação derivada

Ao aprovar uma contribuição sem `conteudo_id`, o sistema deve criar um novo conteúdo publicado. Ao aprovar uma contribuição com `conteudo_id`, o sistema deve atualizar o conteúdo correspondente, sem criar uma cópia.

### RF-013 - Guia de contribuição

O sistema deve disponibilizar, antes do primeiro envio, orientações sobre qualidade, escopo permitido, autoria e fontes. O usuário deve poder consultar essas orientações novamente durante o preenchimento.

### RF-014 - Gestão de usuários

Administradores devem poder listar e filtrar todas as contas, criar contas com perfil de moderador ou administrador, alterar perfis, ativar ou desativar contas, definir uma senha temporária e excluir contas. Moderadores devem poder listar, desativar, reativar e excluir somente contas de usuários comuns, sem ver o e-mail. Ninguém vê a senha de outra pessoa. Ao excluir uma conta, o sistema apaga a conta e as contribuições dela e mantém os conteúdos publicados com o autor "Usuário removido". Perfis administrativos também podem ser pré-cadastrados por seed de desenvolvimento.

### RF-015 - Proteção contra autobloqueio

Um administrador não pode desativar a própria conta nem remover o próprio perfil de administrador. Ninguém pode excluir a própria conta, e o último administrador ativo não pode ser excluído.

### RF-016 - Permissões

O sistema deve impedir que usuários sem autorização publiquem ou alterem diretamente conteúdos, executem decisões de moderação ou acessem funções administrativas.

### RF-017 - Rastreabilidade

O sistema deve preservar o vínculo de cada conteúdo com o colaborador responsável e com a origem informada.

### RF-018 - Validação de dados

O sistema deve rejeitar envios incompletos antes de criar registros parciais e informar quais campos estão ausentes.

### RF-019 - Mensagens de estado

O sistema deve apresentar mensagens que informem a causa do problema e, quando aplicável, orientem como corrigi-lo ou tentar novamente. Isso vale para estados vazios, erros de acesso, falhas de conexão e envios incompletos.

### RF-020 - Exclusão de contribuições

O autor deve poder excluir uma contribuição própria ainda não publicada. Para uma contribuição já publicada, ele deve poder pedir a exclusão à moderação, com um motivo, e cancelar o pedido. Moderadores e administradores devem poder excluir a contribuição e o conteúdo publicado, depois de uma confirmação, ou recusar o pedido com uma justificativa que o autor vê.

### RF-021 - Perfil do usuário

Cada pessoa deve poder editar o próprio nome, e-mail e senha na página Meu perfil. Para alterar o e-mail ou a senha, o sistema deve exigir a senha atual.

### RF-022 - Recuperação de senha

O sistema deve permitir pedir uma senha nova pela tela de login, informando o e-mail da conta e, se a pessoa quiser, um contato. A resposta deve ser a mesma para e-mail cadastrado ou não, para não revelar quem tem conta. Contas desativadas não geram pedido. Administradores devem ver os pedidos e atendê-los definindo uma senha temporária, entregue por fora do site. Quem entra com a senha temporária deve ser levado a Meu perfil, com um aviso para escolher uma senha nova.

### RF-023 - Expiração da sessão

O login deve expirar depois de um tempo configurável (30 minutos por padrão, pela variável `ACCESS_TOKEN_EXPIRE_MINUTES`). Ao abrir o site com um login vencido, o sistema deve descartar a sessão. Quando a API recusar o login durante o uso, o sistema deve encerrar a sessão em todas as telas e avisar na tela de login que é preciso entrar de novo.

## 5. Requisitos não funcionais

### RNF-001 - Segurança de acesso

O sistema deve diferenciar os perfis de usuário, moderador e administrador. Qualquer usuário autenticado pode contribuir. Operações de moderação e administração não autorizadas devem ser negadas. Tokens de login assinados com outra chave, sem assinatura ou vencidos devem ser recusados.

### RNF-002 - Privacidade

O sistema deve coletar somente os dados necessários para conta, autoria e moderação. Senhas não podem aparecer em respostas da API, mensagens de erro ou registros de operação. Na gestão de usuários, o e-mail das contas só aparece para administradores.

### RNF-003 - Acessibilidade

Os fluxos principais de consulta, contribuição e moderação devem oferecer nomes acessíveis, foco visível e navegação por teclado. O texto deve ter contraste de pelo menos 4,5:1 (WCAG AA) nos temas claro e escuro, e a cor nunca pode ser a única forma de identificar uma informação.

### RNF-004 - Compatibilidade

O MVP deve funcionar na versão estável mais recente de Chrome, Edge e Firefox em desktop e de Chrome para Android e Safari para iOS. O layout deve se adaptar a telas pequenas, sem textos saindo dos componentes.

### RNF-005 - Confiabilidade da informação

Cursos e disciplinas devem ter origem nas páginas públicas do SIGAA. Conteúdos acadêmicos só são publicados após revisão humana.

### RNF-006 - Manutenibilidade e qualidade dos testes

O código deve ser organizado por responsabilidades e possuir testes automatizados para as regras mais importantes do sistema. Em 100% dos módulos críticos, a suíte de testes deve quebrar quando um defeito proposital é introduzido (teste de sabotagem), e o escore de mutação dos módulos críticos do frontend deve ser de pelo menos 50%.

### RNF-007 - Documentação

O repositório deve conter instruções básicas de configuração, execução, publicação e contribuição do projeto.

Não fazem parte deste projeto metas de desempenho, capacidade, escalabilidade ou infraestrutura avançada.

## 6. Cenários de uso prioritários

### Cenário 1: Consultar uma disciplina

1. O estudante acessa a Base de Conhecimento e vê os conteúdos publicados.
2. Filtra por curso, disciplina ou tipo de conteúdo, se quiser.
3. Abre um conteúdo para ler a versão completa.
4. Encontra a opção de contribuir caso o conteúdo ainda não exista.

### Cenário 2: Enviar uma contribuição

1. O estudante cria uma conta ou entra na conta existente.
2. Consulta o guia de primeira contribuição.
3. Preenche o formulário com disciplina, tipo, título, conteúdo e fonte.
4. Envia a contribuição, que fica pendente de revisão.

### Cenário 3: Acompanhar e ajustar uma contribuição

1. O autor acessa "Minhas contribuições".
2. Consulta o estado de cada envio e a orientação da moderação, quando houver.
3. Edita a contribuição para atender às orientações, ou a exclui.
4. A contribuição editada volta para pendente e passa por nova revisão.

### Cenário 4: Moderar uma contribuição

1. O moderador acessa a aba "Para revisar" da moderação.
2. Abre a contribuição e analisa o conteúdo e a fonte.
3. Aprova, rejeita, arquiva ou solicita ajustes, registrando uma justificativa.
4. Na aprovação, o conteúdo é publicado ou atualizado na Base de Conhecimento.

### Cenário 5: Recuperar o acesso

1. A pessoa esquece a senha e pede uma senha nova na tela de login, informando um contato.
2. Um administrador vê o pedido na aba "Pedidos de senha" da tela Usuários.
3. O administrador define uma senha temporária e a entrega pelo contato informado.
4. A pessoa entra com a senha temporária e escolhe uma senha nova em Meu perfil.

## 7. Casos de exceção

- Formulário enviado sem informações obrigatórias.
- Consulta sem resultados.
- Contribuição com material sem fonte, ofensivo ou potencialmente protegido.
- Usuário tentando acessar uma função sem permissão.
- Usuário tentando editar a contribuição de outra pessoa.
- Moderador tentando gerir a conta de um moderador ou administrador.
- Administrador tentando desativar a própria conta, remover o próprio perfil ou excluir a própria conta.
- Cadastro de conta com e-mail já utilizado.
- Pedido de senha nova para um e-mail não cadastrado ou de uma conta desativada.
- Login vencido durante o uso do site.
- API ou SIGAA temporariamente indisponíveis.

## 8. Entidades principais

### Usuário

Pessoa que consulta informações e pode criar uma conta. Possui um perfil: usuário, moderador ou administrador. Usuários autenticados podem enviar contribuições; moderadores e administradores possuem permissões adicionais. Uma conta pode estar ativa ou desativada. Guarda o pedido de senha nova (data e contato) e se a pessoa precisa trocar a senha temporária.

### Curso

Curso de graduação da UnB, com nome, sigla da unidade e grau (bacharelado ou licenciatura). Agrupa disciplinas.

### Disciplina

Unidade curricular que organiza os conteúdos acadêmicos. Pode pertencer a mais de um curso, conforme as estruturas curriculares.

### Conteúdo acadêmico

Material publicado na Base de Conhecimento: resumo, dica, dificuldade, prova, implementação ou link. Pode estar publicado ou arquivado.

### Contribuição

Proposta de criação ou alteração de conteúdo acadêmico enviada por um usuário. Passa pelos estados pendente, ajustes, aprovada, rejeitada e arquivada. Guarda o pedido de exclusão do autor (data e motivo), quando houver.

## 9. Arquitetura e tecnologias definidas

A solução é uma aplicação web simples, adequada ao escopo do projeto da disciplina.

- **Front-end:** React com Vite, HTML, CSS e JavaScript.
- **Back-end:** Python com FastAPI.
- **Banco de dados:** PostgreSQL, com SQLModel para os modelos e Alembic para as migrations.
- **Autenticação:** cadastro e login locais com token JWT, sem integração com o login institucional da UnB.
- **Dados acadêmicos:** cursos e disciplinas coletados das páginas públicas do SIGAA na primeira inicialização da API.
- **Execução:** ambiente local ou Docker Compose (banco, backend e frontend).
- **Publicação:** Vercel (site), Render (API) e Neon (banco).
- **Testes:** pytest no backend; Vitest e Testing Library no frontend; Stryker para o teste de mutação; `scripts/teste_sabotagem.py` para o teste de sabotagem.
- **Organização:** separação entre interface, regras do sistema, persistência de dados e testes.

## 10. Critérios de validação

- Usuários conseguem consultar cursos, disciplinas e conteúdos publicados sem autenticação.
- Os filtros mostram os cursos de graduação da UnB, cada um com as disciplinas da sua estrutura curricular.
- Contribuições novas e editadas permanecem pendentes até uma decisão de moderação.
- O autor consegue ver o estado, editar e excluir as próprias contribuições, mas não as de outros usuários.
- Cada decisão de moderação altera o estado esperado da contribuição e preserva a justificativa informada.
- Aprovações criam ou atualizam o conteúdo publicado correspondente.
- Usuários comuns não acessam operações de moderação ou administração; moderadores não gerem contas da equipe.
- Um administrador não consegue desativar nem excluir a própria conta.
- Um pedido de senha nova tem a mesma resposta para e-mail cadastrado ou não, e a senha temporária leva a pessoa a escolher uma senha nova.
- O sistema apresenta a causa e uma orientação quando ocorre uma falha.
- Os fluxos principais podem ser realizados por teclado.
- O teste de sabotagem passa em 100% dos módulos críticos, e o escore de mutação dos módulos críticos do frontend fica em pelo menos 50%.

## 11. Questões em aberto

- **Tipo "prova":** o formulário de envio não oferece o tipo e o Guia de contribuição orienta a não enviar provas, mas o formulário de edição e a API ainda aceitam "Prova". A equipe precisa decidir se o tipo sai do sistema ou volta a ser aceito.

## 12. Correspondência com a especificação

| Requisito | `specs/001-unb-core/spec.md` |
|---|---|
| RF-001, RF-003 | FR-001, FR-002 |
| RF-002 | FR-022 |
| RF-004, RF-017 | FR-012 |
| RF-005 | FR-009 |
| RF-006 | FR-013, FR-018 |
| RF-007, RF-018 | FR-003, FR-014, FR-015 |
| RF-008 | FR-023 |
| RF-009 | FR-024 |
| RF-010 | FR-004 |
| RF-011 | FR-005, FR-006 |
| RF-012 | FR-007 |
| RF-013 | FR-008 |
| RF-014 | FR-021, FR-029 |
| RF-015 | FR-025, FR-030 |
| RF-016 | FR-010 |
| RF-019 | FR-011, FR-020 |
| RF-020 | FR-026 |
| RF-021 | FR-027 |
| RF-022 | FR-028 |
| RF-023 | FR-031 |
| RNF-002 | FR-019 |
| RNF-003 | FR-016 |
| RNF-004 | FR-017 |
| RNF-006 | SC-006, SC-007 |

## 13. Histórico de alterações

| Data | Alteração |
|---|---|
| 25/11/2026 | Atualização para o estado do sistema publicado: cursos de graduação de toda a UnB (ampliação de 21/11/2026, commit `e5a8a7c`), recuperação de senha, perfil do usuário, exclusão de contribuições e de contas, gestão de usuários por moderadores, expiração da sessão, metas de teste de sabotagem e de mutação, e a questão em aberto sobre o tipo "prova". |
| 15/11/2026 | Refatoração do documento para o escopo acadêmico. Inclusão do recorte do campus do Gama (FCTE), da edição de contribuições e da proteção contra autobloqueio do administrador. |
| 26/10/2026 | Corte de escopo: remoção da Central de Editais, das publicações institucionais, das fontes, das denúncias e da busca unificada. |

## 14. Observação final

O UNB CORE deve priorizar clareza, precisão e transparência. Quando uma informação não puder ser confirmada, o sistema deve mostrar essa limitação claramente em vez de presumir que o conteúdo continua válido.
