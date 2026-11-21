import { describe, expect, it } from 'vitest'

import { extrairCursos } from '../src/services/cursos.js'


describe('extrairCursos', () => {
  it('mantem cursos de todas as unidades da UnB', () => {
    const response = {
      itens: [
        { id: 6, nome: 'CIÊNCIA DA COMPUTAÇÃO', sigla: 'CIC' },
        { id: 33, nome: 'ENGENHARIA DE SOFTWARE', sigla: 'FCTE' },
      ],
    }

    expect(extrairCursos(response)).toEqual([
      { id: 6, nome: 'CIÊNCIA DA COMPUTAÇÃO', sigla: 'CIC' },
      { id: 33, nome: 'ENGENHARIA DE SOFTWARE', sigla: 'FCTE' },
    ])
  })
})
