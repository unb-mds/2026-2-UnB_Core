# Quickstart de Validação: UNB CORE

## Pré-requisitos

- Python 3.12 ou superior.
- PostgreSQL local ou Docker Compose.
- Node.js 20.19+ ou 22.12+ e npm.
- Repositório clonado localmente.

## Preparar o backend

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

Defina o banco e uma chave local para os tokens, e aplique as migrations:

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://USUARIO:SENHA@localhost:5432/NOME_DO_BANCO"
$env:JWT_SECRET_KEY = "dev-only-change-this-secret-key-32-bytes-minimum"
.\.venv\Scripts\alembic.exe -c backend\alembic.ini upgrade head
```

Na primeira inicialização, a API coleta cursos e disciplinas das páginas públicas do SIGAA.

Inicie a API a partir da raiz:

```powershell
python -m uvicorn backend.app.main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000` e a documentação interativa em `/docs`.

## Preparar o frontend

```powershell
cd frontend
npm ci
npm run dev
```

Se a instalação falhar por conflito de dependências, siga as instruções de reinstalação do `README.md`.

## Cenários de validação

### 1. Consulta acadêmica

1. Criar ou carregar um curso, uma disciplina e um conteúdo publicado.
2. Abrir a Base de Conhecimento sem login.
3. Selecionar curso, disciplina e tipo.
4. Abrir os detalhes do conteúdo.

Resultado esperado: somente cursos da FCTE (campus do Gama) aparecem no filtro; somente conteúdos publicados e compatíveis com os filtros aparecem, com autoria ou origem e data de atualização.

### 2. Cadastro e autenticação

1. Criar uma conta de estudante.
2. Fazer login com o e-mail e a senha cadastrados.
3. Consultar os dados da sessão autenticada.
4. Tentar acessar uma rota autenticada sem token.

Resultado esperado: a conta é criada, o login retorna um token e a rota protegida rejeita requisições sem autenticação.

### 3. Contribuição autenticada

1. Criar uma conta de estudante e entrar.
2. Abrir as orientações da primeira contribuição e confirmar que qualidade, escopo, autoria e fontes são explicados.
3. Enviar uma contribuição válida.
4. Consultar as contribuições da conta.
5. Confirmar o estado `pendente`.
6. Tentar enviar sem preencher um campo obrigatório.
7. Tentar enviar sem autenticação.
8. Editar a contribuição em "Minhas contribuições".

Resultado esperado: a contribuição válida fica pendente; dados incompletos produzem mensagem compreensível; usuário não autenticado não consegue enviar; a contribuição editada volta para `pendente`.

### 4. Moderação e permissões

1. Pré-cadastrar ou criar um usuário moderador.
2. Criar uma contribuição pendente.
3. Acessar a moderação com o moderador.
4. Solicitar ajustes ou aprovar a contribuição.
5. Confirmar o novo estado e a justificativa.
6. Confirmar que aprovação cria ou atualiza o conteúdo.
7. Repetir a tentativa com usuário comum.

Resultado esperado: decisões autorizadas alteram o estado e refletem no conteúdo; operações não autorizadas são negadas.

### 5. Administração de usuários

1. Acessar a administração com um administrador.
2. Criar um usuário moderador.
3. Atualizar o perfil ou estado ativo de um usuário.
4. Tentar desativar a própria conta de administrador.
5. Repetir a operação com usuário sem perfil de administrador.

Resultado esperado: somente administradores podem criar ou alterar perfis administrativos, e nenhum administrador consegue desativar a própria conta.

### 6. Acessibilidade e compatibilidade

1. Repetir consulta, contribuição e moderação usando somente teclado.
2. Confirmar foco visível, ordem de foco coerente e nomes acessíveis nos controles principais.
3. Repetir a consulta nos navegadores Chrome, Edge e Firefox para desktop.
4. Repetir a consulta no Chrome para Android e Safari para iOS nas versões estáveis mais recentes disponíveis no ciclo de validação.

Resultado esperado: os fluxos principais podem ser concluídos sem mouse e mantêm comportamento funcional na matriz de navegadores definida no plano.

## Testes automatizados

Executar a partir da raiz do projeto:

```powershell
python -m pytest backend\tests\unit
python -m pytest backend\tests\integration
```

As pastas são executadas separadamente porque `unit` e `integration` possuem arquivos `test_errors.py` com o mesmo nome.

Os testes devem cobrir validações de estados, autenticação, permissões, consulta acadêmica, envio de contribuição, aprovação e tratamento de erros.
