# Quickstart de Validação: UNB CORE

## Pré-requisitos

- Python 3.12 ou superior.
- Node.js e npm em versão compatível com React.
- Repositório clonado localmente.

## Preparar o backend

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

Defina uma chave local para os tokens:

```powershell
$env:JWT_SECRET_KEY = "dev-only-change-this-secret"
```

Inicie a API a partir da raiz:

```powershell
python -m uvicorn backend.app.main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000` e a documentação interativa em `/docs`.

## Preparar o frontend

```powershell
cd frontend
npm install
npm run dev
```

## Cenários de validação

### 1. Consulta acadêmica

1. Criar ou carregar um curso, uma disciplina e um conteúdo publicado.
2. Abrir a Base de Conhecimento sem login.
3. Selecionar curso, disciplina e tipo.
4. Abrir os detalhes do conteúdo.

Resultado esperado: somente conteúdos publicados e compatíveis com os filtros aparecem, com autoria ou origem e data de atualização.

### 2. Cadastro e autenticação

1. Criar uma conta de estudante.
2. Fazer login com o e-mail e a senha cadastrados.
3. Consultar os dados da sessão autenticada.
4. Tentar acessar uma rota autenticada sem token.

Resultado esperado: a conta é criada, o login retorna um token e a rota protegida rejeita requisições sem autenticação.

### 3. Contribuição autenticada

1. Criar uma conta de estudante e entrar.
2. Enviar uma contribuição válida.
3. Consultar as contribuições da conta.
4. Confirmar o estado `pendente`.
5. Tentar enviar sem preencher um campo obrigatório.
6. Tentar enviar sem autenticação.

Resultado esperado: a contribuição válida fica pendente; dados incompletos produzem mensagem compreensível; usuário não autenticado não consegue enviar.

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
4. Repetir a operação com usuário sem perfil de administrador.

Resultado esperado: somente administradores podem criar ou alterar perfis administrativos.

## Testes automatizados

Executar a partir da raiz do projeto:

```powershell
python -m pytest
```

Os testes devem cobrir validações de estados, autenticação, permissões, consulta acadêmica, envio de contribuição, aprovação e tratamento de erros.
