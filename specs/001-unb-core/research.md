# Research: UNB CORE

## Decisão: backend com FastAPI, Python e SQLModel

- **Rationale**: A equipe já iniciou o backend com FastAPI e SQLModel. A combinação permite validação com Pydantic, persistência simples e contratos JSON adequados ao frontend React.
- **Alternativas consideradas**: NestJS e Django foram descartados para evitar trocar a stack ou adicionar complexidade ao MVP.

## Decisão: PostgreSQL com Alembic

- **Rationale**: A decisão inicial era usar SQLite no MVP. A equipe migrou para PostgreSQL com migrations Alembic e Docker Compose, para aproximar o ambiente de desenvolvimento do ambiente de entrega. SQLite continua sendo usado em memória nos testes automatizados.
- **Alternativas consideradas**: Manter SQLite em todos os ambientes foi descartado após a adoção do Docker Compose.

## Decisão: autenticação local com token

- **Rationale**: A consulta é pública, mas contribuições, moderação e administração precisam identificar o usuário. O MVP usará cadastro, login, senha protegida e token de acesso.
- **Alternativas consideradas**: Login institucional da UnB e OAuth foram adiados por dependerem de integrações externas.

## Decisão: contribuições moderadas

- **Rationale**: Qualquer usuário autenticado pode enviar uma proposta. A proposta começa como `pendente` e só cria ou atualiza conteúdo após decisão de moderador ou administrador.
- **Alternativas consideradas**: Cadastro separado de colaboradores foi descartado por adicionar uma etapa sem benefício proporcional ao MVP.

## Decisão: perfis administrativos controlados

- **Rationale**: Usuários moderadores e administradores podem ser preparados por seed ou banco, e administradores podem criar ou atualizar perfis por uma tela restrita.
- **Alternativas consideradas**: Permitir que o próprio usuário escolha perfil foi descartado por risco de escalada de privilégio.

## Decisão: API REST versionada

- **Rationale**: O frontend e os testes precisam de respostas JSON previsíveis. O prefixo `/api/v1` organiza os contratos sem introduzir uma arquitetura complexa.
- **Alternativas consideradas**: GraphQL e comunicação em tempo real não são necessários para os fluxos do MVP.

## Decisão: escopo exclusivamente acadêmico

- **Rationale**: Editais, fontes institucionais, denúncias e busca unificada foram removidos para concentrar o trabalho no valor principal da Base de Conhecimento e no fluxo de contribuições.
- **Alternativas consideradas**: Manter um módulo institucional mínimo foi descartado pela equipe nesta entrega.

## Decisão: escopo restrito ao campus do Gama (FCTE)

- **Rationale**: A equipe e o público principal estão no campus do Gama. No SIGAA, os cursos desse campus pertencem à unidade "FCTE - CAMPUS UNB GAMA", identificada pela sigla `FCTE`. Restringir os cursos evita duplicidade de cursos com o mesmo nome em outros campi, como Farmácia e Enfermagem na FCTS (Ceilândia).
- **Alternativas consideradas**: Atender todos os campi foi descartado por ampliar a moderação e a curadoria além da capacidade da equipe.

## Decisão: cursos e disciplinas obtidos do SIGAA

- **Rationale**: Cursos e disciplinas são coletados das páginas públicas do SIGAA na primeira inicialização da API, evitando cadastro manual e divergência com a fonte oficial.
- **Alternativas consideradas**: Cadastro manual por administradores foi descartado por exigir manutenção contínua.
