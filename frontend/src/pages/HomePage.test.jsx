// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../services/api'
import { useAuth } from '../state/auth'
import ConhecimentoPage from './ConhecimentoPage'
import HomePage from './HomePage'

vi.mock('../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { get: vi.fn() },
}))

vi.mock('../state/auth', () => ({
  useAuth: vi.fn(() => ({ isAuthenticated: false, user: null })),
  logout: vi.fn(),
}))

const compiladores = { id: 3, curso_id: [33], codigo: 'FGA0003', nome: 'COMPILADORES 1', periodo: null }

const recente = {
  id: 7,
  disciplina_id: 3,
  disciplina_codigo: 'FGA0003',
  disciplina_nome: 'COMPILADORES 1',
  tipo: 'dica',
  titulo: 'Dica de parser',
  corpo_ou_url: 'Comece pela gramática.',
  autor_id: 1,
  autor_nome: 'Ana Souza',
  origem: null,
  atualizado_em: '2026-11-20T12:00:00Z',
}

function respostas({ conteudos = [recente] } = {}) {
  api.get.mockImplementation((path) => {
    if (path.startsWith('/cursos')) return Promise.resolve({ itens: [{ id: 33, nome: 'ENGENHARIA DE SOFTWARE', sigla: 'FCTE' }] })
    if (path.startsWith('/conteudos?')) return Promise.resolve({ itens: conteudos })
    if (path.startsWith('/disciplinas?busca=')) return Promise.resolve({ itens: [compiladores] })
    if (path.startsWith('/disciplinas/3/conteudos')) return Promise.resolve({ itens: [recente] })
    return Promise.resolve({ itens: [] })
  })
}

beforeEach(() => {
  window.history.replaceState({}, '', '/')
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('HomePage', () => {
  it('mostra os conteúdos recentes com a disciplina e abre a página do conteúdo', async () => {
    respostas()
    const onNavigate = vi.fn()

    render(<HomePage onNavigate={onNavigate} />)

    expect(screen.getByRole('heading', { level: 1, name: /organizado por disciplina/ })).toBeInTheDocument()
    expect(await screen.findByText('Dica de parser')).toBeInTheDocument()
    expect(api.get).toHaveBeenCalledWith('/conteudos?limite=6', expect.anything())
    expect(screen.getByText('FGA0003 - COMPILADORES 1')).toBeInTheDocument()
    expect(screen.getByText('Comece pela gramática.')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Ver conteúdo' }))
    expect(onNavigate).toHaveBeenCalledWith('/conteudos/7')
  })

  it('convida a contribuir quando ainda não há conteúdos', async () => {
    respostas({ conteudos: [] })

    render(<HomePage onNavigate={() => {}} />)

    expect(await screen.findByText('Ainda não há conteúdos publicados')).toBeInTheDocument()
  })

  it('leva para a base de conhecimento com a disciplina escolhida na busca', async () => {
    respostas()
    const onNavigate = vi.fn()

    render(<HomePage onNavigate={onNavigate} />)

    const busca = screen.getByRole('combobox', { name: 'Qual disciplina você quer estudar?' })
    fireEvent.focus(busca)
    fireEvent.change(busca, { target: { value: 'compi' } })
    const opcao = await screen.findByRole('option', { name: /FGA0003 - COMPILADORES 1/ })
    expect(opcao).toHaveTextContent('ENGENHARIA DE SOFTWARE')
    fireEvent.mouseDown(opcao)

    expect(onNavigate).toHaveBeenCalledWith('/base-de-conhecimentos', { disciplina: compiladores })
  })

  it('Enter escolhe o primeiro resultado, mesmo se apertado antes de a busca terminar', async () => {
    respostas()
    const onNavigate = vi.fn()

    render(<HomePage onNavigate={onNavigate} />)

    const busca = screen.getByRole('combobox', { name: 'Qual disciplina você quer estudar?' })
    fireEvent.focus(busca)
    fireEvent.change(busca, { target: { value: 'compi' } })
    // Enter antes do resultado chegar: fica pendente e escolhe quando a resposta vier.
    fireEvent.keyDown(busca, { key: 'Enter' })

    await waitFor(() => expect(onNavigate).toHaveBeenCalledWith('/base-de-conhecimentos', { disciplina: compiladores }))
  })

  it('Enter com os resultados na tela escolhe o primeiro', async () => {
    respostas()
    const onNavigate = vi.fn()

    render(<HomePage onNavigate={onNavigate} />)

    const busca = screen.getByRole('combobox', { name: 'Qual disciplina você quer estudar?' })
    fireEvent.focus(busca)
    fireEvent.change(busca, { target: { value: 'compi' } })
    await screen.findByRole('option', { name: /FGA0003 - COMPILADORES 1/ })
    fireEvent.keyDown(busca, { key: 'Enter' })

    expect(onNavigate).toHaveBeenCalledWith('/base-de-conhecimentos', { disciplina: compiladores })
  })

  it('o título do card é um link para a página do conteúdo', async () => {
    respostas()
    const onNavigate = vi.fn()

    render(<HomePage onNavigate={onNavigate} />)

    const link = await screen.findByRole('link', { name: 'Dica de parser' })
    expect(link).toHaveAttribute('href', '/conteudos/7')
    expect(screen.getByRole('heading', { level: 3, name: 'Dica de parser' })).toBeInTheDocument()

    fireEvent.click(link)
    expect(onNavigate).toHaveBeenCalledWith('/conteudos/7')
  })

  it('mostra a chamada certa para quem não está logado e para quem está', async () => {
    respostas()
    const { unmount } = render(<HomePage onNavigate={() => {}} />)
    expect(screen.getByRole('button', { name: 'Criar conta' })).toBeInTheDocument()
    unmount()

    useAuth.mockReturnValue({ isAuthenticated: true, user: { id: 1, perfil: 'usuario' } })
    render(<HomePage onNavigate={() => {}} />)
    expect(screen.getByRole('button', { name: 'Minhas contribuições' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Criar conta' })).not.toBeInTheDocument()
    await screen.findByText('Dica de parser')
  })
})

describe('ConhecimentoPage aberta pela home', () => {
  it('já carrega os conteúdos da disciplina recebida no histórico', async () => {
    respostas()
    window.history.replaceState({ disciplina: compiladores }, '', '/base-de-conhecimentos')

    render(<ConhecimentoPage onNavigate={() => {}} />)

    expect(screen.getByRole('combobox', { name: 'Disciplina' })).toHaveValue('FGA0003 - COMPILADORES 1')
    expect(await screen.findByText('Dica de parser')).toBeInTheDocument()
    expect(api.get).toHaveBeenCalledWith('/disciplinas/3/conteudos', expect.anything())
  })
})
