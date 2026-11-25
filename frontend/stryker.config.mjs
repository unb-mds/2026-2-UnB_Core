// Teste de mutação do frontend (escore de mutação), com o Stryker Mutator.
//
// O Stryker faz pequenas sabotagens no código, uma de cada vez: troca `<` por `<=`,
// `&&` por `||`, apaga uma linha, esvazia um texto, e assim por diante. Para cada
// sabotagem ("mutante") ele roda os testes:
// - se algum teste falha, o mutante foi "morto": os testes perceberam o defeito;
// - se todos passam, o mutante "sobreviveu": há um defeito que os testes não pegam.
// A nota de mutação é a porcentagem de mutantes mortos.
//
// Rodar: npm run test:mutacao   (relatório em reports/mutacao/index.html)

/** @type {import('@stryker-mutator/api/core').PartialStrykerOptions} */
export default {
  testRunner: 'vitest',
  // Só roda, para cada mutante, os testes que passam pelo trecho sabotado.
  coverageAnalysis: 'perTest',
  // Arquivos com as regras e os fluxos principais do site.
  mutate: [
    'src/services/api.js',
    'src/state/auth.js',
    'src/components/auth/AuthForm.jsx',
    'src/components/conteudos/DisciplinaBusca.jsx',
    'src/components/conteudos/formatacao.js',
    'src/components/contribuicoes/EditarContribuicaoForm.jsx',
    'src/components/moderacao/DecisaoModal.jsx',
    'src/pages/ContribuicaoPage.jsx',
    'src/pages/CadastroPage.jsx',
    'src/pages/LoginPage.jsx',
  ],
  // Constantes do topo do arquivo exigem rodar todos os testes a cada mutante; ficam de fora.
  ignoreStatic: true,
  reporters: ['clear-text', 'progress', 'html'],
  htmlReporter: { fileName: 'reports/mutacao/index.html' },
  // Faixas de cor do relatório: verde a partir de 80%, vermelho abaixo de 60%.
  thresholds: { high: 80, low: 60, break: null },
  tempDirName: '.stryker-tmp',
}
