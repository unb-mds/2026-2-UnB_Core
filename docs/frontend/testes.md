# Testes do frontend

O frontend usa Vitest para executar testes, Testing Library para renderizar e
interagir com os componentes e `jest-dom` para asserções de interface. Os
testes ficam junto ao código, em arquivos `*.test.js` ou `*.test.jsx`.

## Executar testes

Na raiz do repositório, instale as dependências do frontend uma vez e execute
a suíte:

```powershell
cd frontend
npm ci
npm test
```

Os testes de componentes rodam em ambiente `jsdom`. Em geral, as chamadas à API
são simuladas para testar os estados e interações da interface sem precisar
iniciar o backend ou banco de dados.

Para executar um arquivo específico:

```powershell
npx vitest run src/pages/LoginPage.test.jsx
```

Para manter o Vitest em execução durante alterações:

```powershell
npx vitest
```

## Cobertura funcional existente

A suíte cobre fluxos e componentes das principais áreas:

- busca, seleção de disciplina, filtros e conteúdos;
- cadastro, login, sessão expirada e recuperação de senha;
- envio, consulta, edição e exclusão de contribuições;
- moderação e permissões de acesso;
- perfil e gestão de usuários;
- componentes compartilhados, como navegação, layout, badges e formatação de
  conteúdo.

## Lint e build

Na pasta `frontend`:

```powershell
npm run lint
npm run build
```

O lint verifica `src/` com ESLint. O build executa a compilação de produção com
Vite.

## Teste de mutação

O Stryker altera temporariamente trechos do código para verificar se os testes
detectam mudanças que podem representar defeitos. Execute na pasta `frontend`
com Node.js 22 ou superior:

```powershell
npm run test:mutacao
```

O relatório HTML é gerado em `frontend/reports/mutacao/index.html`. Sobreviventes
indicam mutações que não foram detectadas pela suíte; algumas mutações podem ser
equivalentes e não alterar o comportamento observável.

## Teste de sabotagem

O script do repositório também verifica se os testes percebem defeitos
propositais nos módulos críticos do frontend. Na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe scripts/teste_sabotagem.py --parte frontend
```

O script confirma primeiro que a suíte passa sem defeitos, aplica cada
sabotagem, roda os testes e restaura os arquivos alterados. Consulte a seção
[Teste de sabotagem](../como-rodar.md#teste-de-sabotagem) para os comandos de
backend e frontend.
