# Uso de inteligência artificial

Este documento declara o uso de inteligência artificial (IA) no UNB CORE: que
ferramenta foi usada, por quem, em quais partes do projeto e com que cuidados.
Ele cobre o uso registrado até 25/11/2026. Cada integrante que usar IA acrescenta
o próprio registro aqui.

## Ferramenta e período

- **Ferramenta:** [Claude Code](https://www.anthropic.com/claude-code), assistente de programação da Anthropic, usado dentro do VS Code.
- **Quem usou:** Daniel Almeida Frota (Frontend Dev).
- **Período:** de 15/11/2026 a 25/11/2026 (Sprint 10).

## Como foi usada

1. O Daniel descrevia a tarefa: um bug, uma funcionalidade, um ajuste visual ou um documento.
2. A IA lia o código, propunha a solução e, depois da escolha do Daniel, fazia as alterações numa branch própria.
3. A IA rodava os testes, o lint e o build, e escrevia testes novos para o que mudou.
4. A IA preparava o commit e os textos da issue e do PR, no modelo do projeto.
5. O Daniel conferia o resultado no navegador, abria o PR e fazia o merge.

As decisões de produto foram da equipe. Exemplos:

- quem pode excluir contas;
- recuperação de senha com senha temporária, sem envio de e-mail;
- os cursos atendidos (primeiro só o campus do Gama, depois toda a UnB);
- hospedagem no Vercel, no Render e no Neon.

Os commits aparecem só com o nome do Daniel. Este documento é o registro de quais trabalhos tiveram apoio de IA.

## Trabalhos feitos com apoio de IA

| PR | Data | O que mudou |
| --- | --- | --- |
| #140 | 15/11 | Correção de bugs do frontend e integração da edição de contribuições |
| #142 | 15/11 | Documentação alinhada ao escopo acadêmico do campus Gama |
| #145 | 16/11 | Link de Moderação só para a equipe; disciplinas do Gama ligadas aos cursos pela estrutura curricular |
| #147 | 16/11 | Página Meu perfil |
| #151 | 20/11 | Escolha da disciplina sem selecionar o curso |
| #152 | 20/11 | Unificação de disciplinas repetidas e correção do vínculo com cursos |
| #155 | 20/11 | Contribuição editada atualiza o conteúdo publicado em vez de criar uma cópia |
| #156 | 20/11 | Página própria para cada conteúdo e cada contribuição |
| #159 | 20/11 | Página inicial |
| #160 | 20/11 | Tema escuro e ajustes de usabilidade |
| #162 | 20/11 | Listagem e filtros da Base de Conhecimento |
| #164 | 20/11 | Item ativo do menu |
| #167 | 20/11 | Seção "Como funciona" da página inicial |
| #168 | 20/11 | Layout padrão das páginas |
| #173 | 24/11 | Conteúdos de demonstração e script de importação |
| #176 | 24/11 | Exclusão de contribuições, gestão de usuários, recuperação de senha, expiração do login, cores por tipo e testes do frontend |
| #177 | 24/11 | Remoção da página `/admin` e do formulário de denúncia |
| #178 | 25/11 | Preparação da publicação no Vercel, no Render e no Neon |
| #179 | 25/11 | README com o site publicado |
| #180 | 25/11 | Texto da página inicial (texto escrito pelo Daniel; a IA só fez o commit) |
| #181 | 25/11 | Teste de mutação (Stryker) e teste de sabotagem dos módulos críticos |
| — | 25/11 | Revisão do README, desta declaração e dos requisitos |

Também com apoio de IA, fora do repositório: o roteiro da apresentação de 25/11 e o passo a passo da publicação.

## Conteúdos de demonstração

- **O quê:** os textos de `backend/app/seeds/conteudos_demonstracao.json` (33 conteúdos publicados e 3 contribuições pendentes) foram escritos com apoio de IA, para preencher a plataforma na apresentação.
- **Como ficam identificados:** no site, eles aparecem com o autor "Equipe UnB Core (demonstração)", uma conta desativada e sem login, e com a fonte "Conteúdo de demonstração escrito com apoio de IA para apresentar a plataforma. Confira com o material da disciplina."
- **O que não foi gerado:** nenhum conteúdo do tipo "Prova", para não criar provas que não existem. Os links apontam só para sites oficiais (documentação do Python, Guia do Scrum e simulações PhET).
- **Revisão:** os textos tratam de conteúdo padrão das disciplinas, mas não foram revisados por professores. Não substituem o material oficial.
- **Como remover:** os conteúdos têm todos o mesmo autor (`demonstracao@unbcore.example`), então podem ser apagados juntos depois da apresentação, se a equipe preferir.

## Cuidados adotados

- **Banco de dados:** no começo, a IA criou um banco local sem perguntar. Desde então, a regra é pedir autorização ao Daniel antes de criar, alterar ou apagar bancos e dados, e fazer backup antes de aplicar migrations no banco local.
- **Segredos:** senhas, chaves e URLs de banco ficaram fora do repositório. A chave do JWT da publicação foi gerada direto na máquina do Daniel, sem passar pela conversa.
- **Verificação:** todo código passou pelos testes automatizados (pytest e Vitest), pelo lint e pelo build. O teste de mutação e o teste de sabotagem conferem se os testes pegam defeitos de verdade.
- **Limites:** a IA não fez merge de PRs nem mudou configurações do GitHub. Algumas ações, como instalar ferramentas e alterar o banco, foram bloqueadas pelas permissões do Claude Code e ficaram para o Daniel fazer.
