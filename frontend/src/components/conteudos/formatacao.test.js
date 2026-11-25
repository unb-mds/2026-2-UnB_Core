import { describe, expect, it } from 'vitest'
import { classeTipo, ehLink, formatarData, rotuloDisciplinaDoConteudo, rotuloTipo, trecho } from './formatacao'

describe('rotuloTipo e classeTipo', () => {
  it('traduz os tipos conhecidos e mantém os desconhecidos como vieram', () => {
    expect(rotuloTipo('dica')).toBe('Dica de estudo')
    expect(rotuloTipo('outro')).toBe('outro')
    expect(rotuloTipo(undefined)).toBe('Conteúdo')
    expect(classeTipo('link')).toBe('tipo-link')
    expect(classeTipo('outro')).toBe('')
  })
})

describe('formatarData', () => {
  it('escreve a data por extenso em português', () => {
    expect(formatarData('2026-11-20T12:00:00Z')).toBe('20 de novembro de 2026')
    expect(formatarData('2026-11-20T12:00:00Z', 'medium')).toBe('20 de nov. de 2026')
  })

  it('avisa quando não há data e devolve como veio uma data inválida', () => {
    expect(formatarData(null)).toBe('Data não informada')
    expect(formatarData('')).toBe('Data não informada')
    expect(formatarData('ontem')).toBe('ontem')
  })
})

describe('ehLink', () => {
  it.each([
    ['https://youtube.com/watch?v=1', true],
    ['http://exemplo.com', true],
    ['  https://exemplo.com  ', true],
    ['HTTPS://EXEMPLO.COM', true],
    // Só http(s) vira link: nada de "javascript:" ou outros esquemas.
    ['javascript:alert(1)', false],
    ['ftp://exemplo.com', false],
    // Um texto que só contém um link não é um link.
    ['veja https://exemplo.com', false],
    ['https://exemplo.com e mais texto', false],
    ['https://', false],
    ['', false],
    [null, false],
  ])('%s → %s', (texto, esperado) => {
    expect(ehLink(texto)).toBe(esperado)
  })
})

describe('rotuloDisciplinaDoConteudo', () => {
  it('junta código e nome, e usa o que houver', () => {
    expect(rotuloDisciplinaDoConteudo({ disciplina_codigo: 'FGA0003', disciplina_nome: 'COMPILADORES 1' })).toBe('FGA0003 - COMPILADORES 1')
    expect(rotuloDisciplinaDoConteudo({ disciplina_nome: 'COMPILADORES 1' })).toBe('COMPILADORES 1')
    expect(rotuloDisciplinaDoConteudo({ disciplina: 'Cálculo 1' })).toBe('Cálculo 1')
    expect(rotuloDisciplinaDoConteudo({})).toBe('Não informada')
    expect(rotuloDisciplinaDoConteudo(null)).toBe('Não informada')
  })
})

describe('trecho', () => {
  it('mantém textos curtos e tira os espaços das pontas', () => {
    expect(trecho('  Tokens e lexemas.  ')).toBe('Tokens e lexemas.')
    expect(trecho('')).toBe('')
    expect(trecho(null)).toBe('')
  })

  it('troca um link por uma frase curta', () => {
    expect(trecho('https://exemplo.com/material')).toBe('Link para um material externo.')
  })

  it('corta no tamanho pedido, sem espaço antes das reticências', () => {
    expect(trecho('abcde', 5)).toBe('abcde')
    expect(trecho('abcdef', 5)).toBe('abcde…')
    expect(trecho('abcd efgh', 5)).toBe('abcd…')
    expect(trecho('x'.repeat(220))).toBe('x'.repeat(220))
    expect(trecho('x'.repeat(221))).toBe(`${'x'.repeat(220)}…`)
  })
})
