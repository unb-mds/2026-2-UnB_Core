// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { useState } from 'react'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from '../../services/api'
import DisciplinaBusca from './DisciplinaBusca'

vi.mock('../../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { get: vi.fn() },
}))

const compiladores = { id: 1, codigo: 'FGA0003', nome: 'COMPILADORES 1', curso_id: [33, 34] }
const calculo = { id: 2, codigo: 'MAT0025', nome: 'CÁLCULO 1', curso_id: [33] }
const cursos = [{ id: 33, nome: 'Engenharia de Software' }, { id: 34, nome: 'Engenharia Eletrônica' }]

// Guarda a disciplina escolhida, como fazem as páginas que usam o campo.
function Campo({ cursoId = '', onChange = () => {} }) {
  const [valor, setValor] = useState(null)
  return (
    <DisciplinaBusca
      cursoId={cursoId}
      cursos={cursos}
      value={valor}
      onChange={(disciplina) => { setValor(disciplina); onChange(disciplina) }}
    />
  )
}

function digitar(texto) {
  const campo = screen.getByRole('combobox', { name: 'Disciplina' })
  fireEvent.focus(campo)
  fireEvent.change(campo, { target: { value: texto } })
  return campo
}

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('DisciplinaBusca sem curso escolhido', () => {
  it('pede pelo menos 2 letras antes de buscar', () => {
    render(<Campo />)

    digitar('c')

    expect(screen.getByRole('status')).toHaveTextContent('Digite pelo menos 2 letras')
    expect(api.get).not.toHaveBeenCalled()
  })

  it('busca na API sem acento e mostra os cursos de cada disciplina', async () => {
    api.get.mockResolvedValue({ itens: [compiladores] })
    const onChange = vi.fn()
    render(<Campo onChange={onChange} />)

    const campo = digitar('Compilá')

    const opcao = await screen.findByRole('option', { name: /FGA0003 - COMPILADORES 1/ })
    expect(api.get).toHaveBeenCalledWith('/disciplinas?busca=compila', expect.anything())
    expect(opcao).toHaveTextContent('Engenharia de Software, Engenharia Eletrônica')

    fireEvent.mouseDown(opcao)

    expect(onChange).toHaveBeenCalledWith(compiladores)
    expect(campo).toHaveValue('FGA0003 - COMPILADORES 1')
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
  })

  it('Enter escolhe o primeiro resultado', async () => {
    api.get.mockResolvedValue({ itens: [compiladores, calculo] })
    const onChange = vi.fn()
    render(<Campo onChange={onChange} />)

    const campo = digitar('engenharia')
    await screen.findByRole('option', { name: /COMPILADORES 1/ })
    fireEvent.keyDown(campo, { key: 'Enter' })

    expect(onChange).toHaveBeenCalledWith(compiladores)
  })

  it('setas do teclado destacam a opção que o Enter escolhe', async () => {
    api.get.mockResolvedValue({ itens: [compiladores, calculo] })
    const onChange = vi.fn()
    render(<Campo onChange={onChange} />)

    const campo = digitar('engenharia')
    await screen.findByRole('option', { name: /CÁLCULO 1/ })
    fireEvent.keyDown(campo, { key: 'ArrowDown' })
    fireEvent.keyDown(campo, { key: 'ArrowDown' })

    expect(screen.getByRole('option', { name: /CÁLCULO 1/ })).toHaveAttribute('aria-selected', 'true')
    fireEvent.keyDown(campo, { key: 'Enter' })
    expect(onChange).toHaveBeenCalledWith(calculo)
  })

  it('avisa quando nada é encontrado e quando a busca falha', async () => {
    api.get.mockResolvedValueOnce({ itens: [] })
    render(<Campo />)

    digitar('xyz')
    expect(await screen.findByText('Nenhuma disciplina encontrada.')).toBeInTheDocument()

    api.get.mockRejectedValueOnce(new ApiError('A API está fora do ar.'))
    digitar('abc')
    expect(await screen.findByText('A API está fora do ar.')).toBeInTheDocument()
  })

  it('o botão de limpar apaga a disciplina escolhida', async () => {
    api.get.mockResolvedValue({ itens: [compiladores] })
    const onChange = vi.fn()
    render(<Campo onChange={onChange} />)

    const campo = digitar('comp')
    fireEvent.mouseDown(await screen.findByRole('option', { name: /COMPILADORES 1/ }))
    fireEvent.click(screen.getByRole('button', { name: 'Limpar disciplina' }))

    expect(onChange).toHaveBeenLastCalledWith(null)
    expect(campo).toHaveValue('')
  })
})

describe('DisciplinaBusca com curso escolhido', () => {
  it('carrega as disciplinas do curso e filtra pelo começo das palavras, sem buscar de novo na API', async () => {
    api.get.mockResolvedValue({ itens: [compiladores, calculo] })
    render(<Campo cursoId="33" />)

    expect(api.get).toHaveBeenCalledWith('/cursos/33/disciplinas', expect.anything())
    const campo = screen.getByRole('combobox', { name: 'Disciplina' })
    fireEvent.focus(campo)
    expect(await screen.findAllByRole('option')).toHaveLength(2)

    fireEvent.change(campo, { target: { value: 'calc' } })

    await waitFor(() => expect(screen.getAllByRole('option')).toHaveLength(1))
    expect(screen.getByRole('option')).toHaveTextContent('MAT0025 - CÁLCULO 1')
    // "pila" está no meio de "compiladores": não conta como começo de palavra.
    fireEvent.change(campo, { target: { value: 'pila' } })
    expect(screen.getByText('Nenhuma disciplina encontrada.')).toBeInTheDocument()
    expect(api.get).toHaveBeenCalledTimes(1)
  })
})
