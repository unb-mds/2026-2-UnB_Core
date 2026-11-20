// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import MinhaContribuicaoPage from './MinhaContribuicaoPage'

vi.mock('../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { get: vi.fn(), patch: vi.fn() },
}))

vi.mock('../state/auth', () => ({
  useAuth: vi.fn(() => ({ isAuthenticated: true, user: { id: 1, perfil: 'usuario' } })),
  logout: vi.fn(),
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

const contribuicao = {
  id: 5,
  autor_id: 1,
  conteudo_id: 7,
  disciplina_id: 3,
  disciplina_codigo: 'FGA0003',
  disciplina_nome: 'COMPILADORES 1',
  tipo: 'dica',
  titulo: 'Dica de parser',
  corpo_ou_url: 'Comece pela gramática.',
  origem: null,
  estado: 'pendente',
  justificativa_moderacao: null,
  criado_em: '2026-11-18T12:00:00Z',
  atualizado_em: '2026-11-20T12:00:00Z',
}

describe('MinhaContribuicaoPage', () => {
  it('mostra a contribuição e leva para a versão publicada', async () => {
    api.get.mockResolvedValue(contribuicao)
    const onNavigate = vi.fn()

    render(<MinhaContribuicaoPage contribuicaoId="5" onNavigate={onNavigate} />)

    expect(await screen.findByRole('heading', { level: 1, name: 'Dica de parser' })).toBeInTheDocument()
    expect(api.get).toHaveBeenCalledWith('/contribuicoes/minhas/5', expect.anything())
    expect(screen.getByText('FGA0003 - COMPILADORES 1')).toBeInTheDocument()
    expect(screen.getByText('Pendente')).toBeInTheDocument()
    expect(screen.getByText(/continua publicada até a moderação aprovar/)).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Ver versão publicada' }))
    expect(onNavigate).toHaveBeenCalledWith('/conteudos/7')
  })

  it('abre o formulário de edição com os dados atuais', async () => {
    api.get.mockResolvedValue(contribuicao)

    render(<MinhaContribuicaoPage contribuicaoId="5" onNavigate={() => {}} />)

    fireEvent.click(await screen.findByRole('button', { name: 'Editar' }))

    expect(screen.getByDisplayValue('Dica de parser')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Comece pela gramática.')).toBeInTheDocument()
  })

  it('não mostra contribuição de outra pessoa', async () => {
    api.get.mockRejectedValue(new ApiError('Usuario não tem permissão de editar essa contribuição', { status: 422 }))

    render(<MinhaContribuicaoPage contribuicaoId="9" onNavigate={() => {}} />)

    expect(await screen.findByText('Contribuição não encontrada')).toBeInTheDocument()
  })

  it('pede login quando não há sessão', () => {
    useAuth.mockReturnValue({ isAuthenticated: false, user: null })

    render(<MinhaContribuicaoPage contribuicaoId="5" onNavigate={() => {}} />)

    expect(screen.getByText('Entre para ver esta contribuição')).toBeInTheDocument()
    expect(api.get).not.toHaveBeenCalled()
  })
})
