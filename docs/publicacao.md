# Publicação no Vercel, Render e Neon

Este guia descreve como publicar o UNB CORE usando o Neon para PostgreSQL, o
Render para a API e o Vercel para o frontend. A configuração gratuita é adequada
para demonstrações e apresentações, mas não é um ambiente de produção: serviços
podem pausar quando ficam sem uso e demorar para responder ao primeiro acesso.

## Pré-requisitos

- Conta no [Neon](https://neon.tech), [Render](https://render.com) e
  [Vercel](https://vercel.com).
- Repositório acessível à plataforma escolhida.
- Permissão para autorizar o acesso ao repositório da organização `unb-mds`.
  Caso não tenha essa permissão, solicite aprovação a um administrador ou use um
  fork autorizado.

## 1. Criar o banco no Neon

1. Crie um projeto no Neon.
2. Crie ou selecione um banco de dados e um usuário.
3. Copie a connection string PostgreSQL fornecida pelo Neon e guarde-a como
   segredo. Ela será usada como `DATABASE_URL` no Render. Não publique nem
   versione essa URL, pois contém credenciais.

O backend reconhece URLs `postgresql://` e `postgres://` do Neon e converte o
driver para `psycopg2`, usado pelo projeto.

## 2. Publicar a API no Render

1. No Render, crie um **Web Service** conectado ao repositório.
2. Selecione **Docker** como ambiente.
3. Configure:
   - **Dockerfile Path:** `backend/Dockerfile`
   - **Docker Build Context Directory:** `.`
4. Adicione estas variáveis em **Environment**:

   | Variável | Valor |
   |---|---|
   | `DATABASE_URL` | Connection string copiada do Neon |
   | `JWT_SECRET_KEY` | Chave aleatória forte e exclusiva para o serviço |
   | `CORS_ORIGINS` | Endereço de produção do frontend no Vercel, incluindo `https://` |

   Para gerar uma chave localmente com Python:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   Se precisar autorizar mais de uma origem, separe os endereços de frontend
   por vírgula em `CORS_ORIGINS`. Informe origens exatas, sem caminho final,
   como `https://unb-core.vercel.app`.

5. Inicie o deploy. O container executa as migrations do Alembic antes de
   iniciar a API.
6. Copie o endereço público do Web Service, por exemplo
   `https://nome-do-servico.onrender.com`.

A documentação interativa da API ficará em
`https://<servico>.onrender.com/docs`.

## 3. Publicar o frontend no Vercel

1. No Vercel, importe o mesmo repositório.
2. Defina **Root Directory** como `frontend`.
3. Em **Environment Variables**, adicione:

   | Variável | Valor |
   |---|---|
   | `VITE_API_URL` | Endereço do Render seguido de `/api/v1`, por exemplo `https://nome-do-servico.onrender.com/api/v1` |

4. Mantenha as configurações de build definidas em `frontend/vercel.json`:
   - instalação: `npm ci --legacy-peer-deps`
   - build: `npm run build`
   - saída: `dist`
5. Faça o deploy e copie o endereço de produção atribuído ao site.

O arquivo `vercel.json` também configura o redirecionamento das rotas da
aplicação para `index.html`, necessário para que o recarregamento de páginas
internas funcione.

## 4. Conferir a integração

1. Confira se `CORS_ORIGINS` no Render contém exatamente o endereço de produção
   do Vercel, incluindo `https://`. Se alterar essa variável, faça um novo
   deploy ou reinicie o serviço.
2. Se alterar `VITE_API_URL` no Vercel, faça um novo deploy do frontend para
   aplicar a variável ao bundle.
3. Abra `https://<servico>.onrender.com/docs` e confirme que a API responde.
4. Abra o endereço do Vercel e confira se a aplicação carrega e consegue
   consultar a API.

Quando o banco do Neon estiver vazio, a API realiza a carga inicial dos cursos
e disciplinas a partir do SIGAA. Essa operação ocorre em segundo plano e
depende de acesso à internet.

## Problemas comuns

| Sintoma | O que conferir |
|---|---|
| A aplicação não conecta à API | Aguarde a API acordar. Confira se `VITE_API_URL` termina com `/api/v1`, se aponta para o serviço correto e se o frontend foi publicado novamente após a alteração. |
| Erro de CORS no navegador | Confira se `CORS_ORIGINS` contém o endereço exato do frontend, com `https://`, e reinicie ou publique novamente a API. |
| Erro 404 ao recarregar uma rota do site | Confirme que o **Root Directory** do Vercel é `frontend` para que o `vercel.json` seja aplicado. |
| O Render não encontra o Dockerfile | Confira `backend/Dockerfile` e o contexto de build `.`. |
| Login ou dados não funcionam | Confira os logs do Render e a `DATABASE_URL`; confirme que o banco Neon correto está conectado e que as migrations foram aplicadas. |

No plano gratuito, o Render pode suspender o serviço após 15 minutos sem acesso.
O primeiro acesso depois desse período pode levar cerca de um minuto. O Neon
também pode suspender o banco inativo e reativá-lo quando houver uma nova
conexão.
