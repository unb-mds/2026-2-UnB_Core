// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ModeracaoPage from './ModeracaoPage'

vi.mock('../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { get: vi.fn(), post: vi.fn() },
}))

vi.mock('../state/auth', () => ({
  useAuth: vi.fn(),
  logout: vi.fn(),
}))

const pendente = {
  id: 5,
  autor_nome: 'Ana Souza',
  disciplina_codigo: 'FGA0003',
  disciplina_nome: 'COMPILADORES 1',
  tipo: 'resumo',
  titulo: 'Resumo de análise léxica',
  corpo_ou_url: 'Tokens e lexemas.',
  estado: 'pendente',
  exclusao_solicitada_em: null,
  criado_em: '2026-11-20T12:00:00Z',
  atualizado_em: '2026-11-20T12:00:00Z',
}

async function abrirDecisao() {
  render(<ModeracaoPage onNavigate={() => {}} />)
  fireEvent.click(await screen.findByRole('button', { name: 'Tomar decisão' }))
  return screen.getByRole('dialog', { name: 'Decidir contribuição' })
}

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('acesso à moderação', () => {
  it('manda para o login quem não entrou', () => {
    useAuth.mockReturnValue({ isAuthenticated: false, user: null })
    const onNavigate = vi.fn()
    render(<ModeracaoPage onNavigate={onNavigate} />)

    expect(onNavigate).toHaveBeenCalledWith('/login')
    expect(api.get).not.toHaveBeenCalled()
  })

  it('manda para o início um usuário comum', () => {
    useAuth.mockReturnValue({ isAuthenticated: true, user: { id: 2, perfil: 'usuario' } })
    const onNavigate = vi.fn()
    render(<ModeracaoPage onNavigate={onNavigate} />)

    expect(onNavigate).toHaveBeenCalledWith('/')
    expect(api.get).not.toHaveBeenCalled()
  })
})

describe('decisão da moderação', () => {
  beforeEach(() => {
    useAuth.mockReturnValue({ isAuthenticated: true, user: { id: 9, perfil: 'moderador' } })
    api.get.mockResolvedValue([pendente])
    api.post.mockResolvedValue({})
  })

  it('aprova sem justificativa e recarrega a lista', async () => {
    const dialogo = await abrirDecisao()
    expect(dialogo).toHaveTextContent('Resumo de análise léxica')

    fireEvent.click(screen.getByRole('button', { name: 'Confirmar decisão' }))

    await waitFor(() => expect(api.post).toHaveBeenCalledWith('/moderacao/contribuicoes/5/decisao', { decisao: 'aprovar', justificativa: undefined }))
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(api.get).toHaveBeenCalledTimes(2)
  })

  it.each([
    ['ajustes', 'Solicitar ajustes'],
    ['rejeitar', 'Rejeitar'],
  ])('exige justificativa para %s', async (decisao, rotulo) => {
    await abrirDecisao()
    fireEvent.change(screen.getByRole('combobox', { name: 'Decisão' }), { target: { value: decisao } })

    expect(screen.getByRole('combobox', { name: 'Decisão' })).toHaveDisplayValue(rotulo)
    expect(screen.getByRole('button', { name: 'Confirmar decisão' })).toBeDisabled()

    const texto = '  Cite a fonte do material.  '
    fireEvent.change(screen.getByLabelText(/Justificativa/), { target: { value: texto } })
    expect(screen.getByText(`${texto.length}/1000 caracteres`)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar decisão' }))

    await waitFor(() => expect(api.post).toHaveBeenCalledWith('/moderacao/contribuicoes/5/decisao', { decisao, justificativa: 'Cite a fonte do material.' }))
  })

  it('só espaços não contam como justificativa', async () => {
    await abrirDecisao()
    fireEvent.change(screen.getByRole('combobox', { name: 'Decisão' }), { target: { value: 'rejeitar' } })
    fireEvent.change(screen.getByLabelText(/Justificativa/), { target: { value: '    ' } })

    expect(screen.getByRole('button', { name: 'Confirmar decisão' })).toBeDisabled()
  })

  it('fecha sem decidir com Cancelar ou com a tecla Esc', async () => {
    await abrirDecisao()
    fireEvent.click(screen.getByRole('button', { name: 'Cancelar' }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Tomar decisão' }))
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(api.post).not.toHaveBeenCalled()
  })

  it('mostra o erro quando a decisão não é registrada', async () => {
    api.post.mockRejectedValue(new ApiError('Esta contribuição já foi decidida.', { status: 409 }))
    await abrirDecisao()

    fireEvent.click(screen.getByRole('button', { name: 'Confirmar decisão' }))

    expect(await screen.findByText('Esta contribuição já foi decidida.')).toBeInTheDocument()
  })

  it('mostra o aviso da aba quando não há nada para revisar', async () => {
    api.get.mockResolvedValue([])
    render(<ModeracaoPage onNavigate={() => {}} />)

    expect(await screen.findByText('Nenhuma contribuição esperando revisão.')).toBeInTheDocument()
  })
})
