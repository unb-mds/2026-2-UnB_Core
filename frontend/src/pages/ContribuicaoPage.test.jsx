// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ContribuicaoPage from './ContribuicaoPage'

vi.mock('../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { get: vi.fn(), post: vi.fn() },
}))

vi.mock('../state/auth', () => ({
  useAuth: vi.fn(),
  logout: vi.fn(),
}))

const compiladores = { id: 7, codigo: 'FGA0003', nome: 'COMPILADORES 1', curso_id: [33] }
const calculo = { id: 8, codigo: 'MAT0025', nome: 'CÁLCULO 1', curso_id: [40] }

// Respostas falsas da API, por endereço.
function responderApi(path) {
  if (path === '/cursos') return Promise.resolve({ itens: [{ id: 33, nome: 'Engenharia de Software' }, { id: 40, nome: 'Matemática' }] })
  if (path.startsWith('/disciplinas?busca=')) return Promise.resolve({ itens: [compiladores, calculo] })
  if (path === '/cursos/40/disciplinas') return Promise.resolve({ itens: [calculo] })
  return Promise.resolve({ itens: [] })
}

async function escolherDisciplina(nome = /COMPILADORES 1/) {
  const campo = screen.getByRole('combobox', { name: /^Disciplina/ })
  fireEvent.focus(campo)
  fireEvent.change(campo, { target: { value: 'comp' } })
  fireEvent.mouseDown(await screen.findByRole('option', { name: nome }))
}

function preencherTexto({ titulo = 'Resumo de análise léxica', conteudo = 'Tokens, lexemas e autômatos.', url = '' } = {}) {
  fireEvent.change(screen.getByLabelText(/^Título/), { target: { value: titulo } })
  fireEvent.change(screen.getByLabelText('Conteúdo'), { target: { value: conteudo } })
  if (url) fireEvent.change(screen.getByLabelText(/^Fonte/), { target: { value: url } })
}

const enviar = () => fireEvent.click(screen.getByRole('button', { name: 'Enviar contribuição' }))

beforeEach(() => {
  api.get.mockImplementation(responderApi)
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('ContribuicaoPage sem login', () => {
  it('deixa preencher, mas pede login para enviar', async () => {
    useAuth.mockReturnValue({ isAuthenticated: false, user: null })
    const onNavigate = vi.fn()
    render(<ContribuicaoPage onNavigate={onNavigate} />)

    enviar()

    expect(screen.getByText('Entre na sua conta para enviar uma contribuição.')).toBeInTheDocument()
    expect(api.post).not.toHaveBeenCalled()

    fireEvent.click(screen.getByRole('link', { name: 'entre na sua conta' }))
    expect(onNavigate).toHaveBeenCalledWith('/login')
  })
})

describe('ContribuicaoPage com login', () => {
  beforeEach(() => {
    useAuth.mockReturnValue({ isAuthenticated: true, user: { id: 1, perfil: 'usuario' } })
  })

  it('lista todos os campos obrigatórios que faltam', () => {
    render(<ContribuicaoPage onNavigate={() => {}} />)

    enviar()

    expect(screen.getByText('Preencha os campos obrigatórios: disciplina, tipo de conteúdo, título, conteúdo ou URL.')).toBeInTheDocument()
    expect(api.post).not.toHaveBeenCalled()
  })

  it('marca o tipo escolhido e troca quando a pessoa clica em outro', () => {
    render(<ContribuicaoPage onNavigate={() => {}} />)

    fireEvent.click(screen.getByRole('button', { name: 'Resumo' }))
    expect(screen.getByRole('button', { name: 'Resumo' })).toHaveAttribute('aria-pressed', 'true')

    fireEvent.click(screen.getByRole('button', { name: 'Link útil' }))
    expect(screen.getByRole('button', { name: 'Link útil' })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('button', { name: 'Resumo' })).toHaveAttribute('aria-pressed', 'false')
  })

  it('envia a contribuição completa e mostra a confirmação', async () => {
    api.post.mockResolvedValue({ id: 15, estado: 'pendente' })
    const onNavigate = vi.fn()
    render(<ContribuicaoPage onNavigate={onNavigate} />)

    await escolherDisciplina()
    fireEvent.click(screen.getByRole('button', { name: 'Resumo' }))
    preencherTexto({ titulo: '  Resumo de análise léxica  ' })
    enviar()

    expect(await screen.findByText('Recebemos a sua contribuição')).toBeInTheDocument()
    // O título vai sem os espaços das pontas, e sem origem quando não há fonte.
    expect(api.post).toHaveBeenCalledWith('/contribuicoes', {
      disciplina_id: 7,
      tipo: 'resumo',
      titulo: 'Resumo de análise léxica',
      corpo_ou_url: 'Tokens, lexemas e autômatos.',
      origem: undefined,
    })

    fireEvent.click(screen.getByRole('button', { name: 'Acompanhar em Minhas contribuições' }))
    expect(onNavigate).toHaveBeenCalledWith('/minhas-contribuicoes')
  })

  it('aceita só a fonte, sem texto, e usa o link como conteúdo', async () => {
    api.post.mockResolvedValue({ id: 16 })
    render(<ContribuicaoPage onNavigate={() => {}} />)

    await escolherDisciplina()
    fireEvent.click(screen.getByRole('button', { name: 'Link útil' }))
    preencherTexto({ titulo: 'Playlist de Compiladores', conteudo: '', url: 'https://youtube.com/playlist?list=abc' })
    enviar()

    await waitFor(() => expect(api.post).toHaveBeenCalled())
    expect(api.post.mock.calls[0][1]).toMatchObject({
      tipo: 'link',
      corpo_ou_url: 'https://youtube.com/playlist?list=abc',
      origem: 'https://youtube.com/playlist?list=abc',
    })
  })

  it('"Enviar outra" limpa o formulário para um novo envio', async () => {
    api.post.mockResolvedValue({ id: 17 })
    render(<ContribuicaoPage onNavigate={() => {}} />)

    await escolherDisciplina()
    fireEvent.click(screen.getByRole('button', { name: 'Dica de estudo' }))
    preencherTexto()
    enviar()
    fireEvent.click(await screen.findByRole('button', { name: 'Enviar outra' }))

    expect(screen.getByLabelText(/^Título/)).toHaveValue('')
    expect(screen.getByRole('combobox', { name: /^Disciplina/ })).toHaveValue('')
    expect(screen.getByRole('button', { name: 'Dica de estudo' })).toHaveAttribute('aria-pressed', 'false')
  })

  it('mostra o erro da API e mantém o que foi preenchido', async () => {
    api.post.mockRejectedValue(new ApiError('Disciplina não encontrada.', { status: 404 }))
    render(<ContribuicaoPage onNavigate={() => {}} />)

    await escolherDisciplina()
    fireEvent.click(screen.getByRole('button', { name: 'Resumo' }))
    preencherTexto()
    enviar()

    expect(await screen.findByText('Disciplina não encontrada.')).toBeInTheDocument()
    expect(screen.getByLabelText(/^Título/)).toHaveValue('Resumo de análise léxica')
    expect(screen.getByRole('button', { name: 'Enviar contribuição' })).toBeEnabled()
  })

  it('o curso só filtra: tira a disciplina escolhida se ela não for daquele curso', async () => {
    render(<ContribuicaoPage onNavigate={() => {}} />)
    const curso = screen.getByRole('combobox', { name: /^Curso/ })
    await screen.findByRole('option', { name: 'Matemática' })

    await escolherDisciplina()
    fireEvent.change(curso, { target: { value: '40' } })

    // COMPILADORES 1 não é de Matemática, então a escolha é desfeita.
    expect(screen.getByRole('combobox', { name: /^Disciplina/ })).toHaveValue('')

    fireEvent.change(curso, { target: { value: '' } })
    await escolherDisciplina()
    fireEvent.change(curso, { target: { value: '33' } })
    // Já COMPILADORES 1 é de Engenharia de Software e continua escolhida.
    expect(screen.getByRole('combobox', { name: /^Disciplina/ })).toHaveValue('FGA0003 - COMPILADORES 1')
  })
})
