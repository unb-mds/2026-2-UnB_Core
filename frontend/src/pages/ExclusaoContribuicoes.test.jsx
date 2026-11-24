// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../services/api'
import { useAuth } from '../state/auth'
import MinhaContribuicaoPage from './MinhaContribuicaoPage'
import ModeracaoContribuicaoPage from './ModeracaoContribuicaoPage'
import ModeracaoPage from './ModeracaoPage'

vi.mock('../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

vi.mock('../state/auth', () => ({
  useAuth: vi.fn(),
  logout: vi.fn(),
}))

const base = {
  id: 5,
  autor_id: 1,
  autor_nome: 'Ana Souza',
  conteudo_id: null,
  disciplina_id: 3,
  disciplina_codigo: 'FGA0003',
  disciplina_nome: 'COMPILADORES 1',
  tipo: 'resumo',
  titulo: 'Resumo de análise léxica',
  corpo_ou_url: 'Tokens e lexemas.',
  origem: null,
  estado: 'pendente',
  justificativa_moderacao: null,
  exclusao_solicitada_em: null,
  motivo_exclusao: null,
  criado_em: '2026-11-20T12:00:00Z',
  atualizado_em: '2026-11-20T12:00:00Z',
}

beforeEach(() => {
  vi.spyOn(window, 'confirm').mockReturnValue(true)
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
  vi.restoreAllMocks()
})

describe('autor', () => {
  beforeEach(() => {
    useAuth.mockReturnValue({ isAuthenticated: true, user: { id: 1, perfil: 'usuario' } })
  })

  it('exclui na hora uma contribuição ainda não publicada', async () => {
    api.get.mockResolvedValue(base)
    api.delete.mockResolvedValue(null)
    const onNavigate = vi.fn()

    render(<MinhaContribuicaoPage contribuicaoId="5" onNavigate={onNavigate} />)
    fireEvent.click(await screen.findByRole('button', { name: 'Excluir contribuição' }))

    await waitFor(() => expect(onNavigate).toHaveBeenCalledWith('/minhas-contribuicoes'))
    expect(window.confirm).toHaveBeenCalled()
    expect(api.delete).toHaveBeenCalledWith('/contribuicoes/minhas/5')
    expect(screen.queryByRole('button', { name: 'Pedir exclusão' })).not.toBeInTheDocument()
  })

  it('não exclui se a pessoa desistir na confirmação', async () => {
    window.confirm.mockReturnValue(false)
    api.get.mockResolvedValue(base)

    render(<MinhaContribuicaoPage contribuicaoId="5" onNavigate={() => {}} />)
    fireEvent.click(await screen.findByRole('button', { name: 'Excluir contribuição' }))

    expect(api.delete).not.toHaveBeenCalled()
  })

  it('pede exclusão de uma contribuição publicada, com motivo', async () => {
    const publicada = { ...base, conteudo_id: 7, estado: 'aprovada' }
    api.get.mockResolvedValue(publicada)
    api.post.mockResolvedValue({ ...publicada, exclusao_solicitada_em: '2026-11-24T12:00:00Z', motivo_exclusao: 'Achei um erro no texto.' })

    render(<MinhaContribuicaoPage contribuicaoId="5" onNavigate={() => {}} />)
    expect(await screen.findByRole('heading', { level: 1, name: 'Resumo de análise léxica' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Excluir contribuição' })).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Pedir exclusão' }))
    fireEvent.change(screen.getByRole('textbox', { name: /Por que você quer excluir/ }), { target: { value: 'Achei um erro no texto.' } })
    fireEvent.click(screen.getByRole('button', { name: 'Enviar pedido' }))

    expect(await screen.findByText(/Pedido de exclusão enviado em/)).toBeInTheDocument()
    expect(api.post).toHaveBeenCalledWith('/contribuicoes/minhas/5/pedido-exclusao', { motivo: 'Achei um erro no texto.' })
    expect(screen.getByRole('button', { name: 'Cancelar pedido de exclusão' })).toBeInTheDocument()
  })
})

describe('moderação', () => {
  beforeEach(() => {
    useAuth.mockReturnValue({ isAuthenticated: true, user: { id: 9, perfil: 'moderador' } })
  })

  it('troca de aba e mostra disciplina, autor e o pedido de exclusão', async () => {
    const comPedido = { ...base, conteudo_id: 7, estado: 'aprovada', exclusao_solicitada_em: '2026-11-24T12:00:00Z', motivo_exclusao: 'Achei um erro.' }
    api.get.mockImplementation((path) => Promise.resolve(path.includes('filtro=exclusao') ? [comPedido] : [base]))
    const onNavigate = vi.fn()

    render(<ModeracaoPage onNavigate={onNavigate} />)
    expect(await screen.findByText(/FGA0003 - COMPILADORES 1 · por Ana Souza/)).toBeInTheDocument()
    expect(api.get).toHaveBeenCalledWith('/moderacao/contribuicoes?filtro=revisar')

    fireEvent.click(screen.getByRole('tab', { name: 'Pedidos de exclusão' }))

    expect(await screen.findByText('Achei um erro.')).toBeInTheDocument()
    expect(api.get).toHaveBeenCalledWith('/moderacao/contribuicoes?filtro=exclusao')
    // Só pendentes podem receber decisão.
    expect(screen.queryByRole('button', { name: 'Tomar decisão' })).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Ver detalhes' }))
    expect(onNavigate).toHaveBeenCalledWith('/moderacao/contribuicoes/5')
  })

  it('exclui de vez pela página de detalhe, depois de confirmar', async () => {
    api.get.mockResolvedValue({ ...base, conteudo_id: 7, estado: 'aprovada' })
    api.delete.mockResolvedValue(null)
    const onNavigate = vi.fn()

    render(<ModeracaoContribuicaoPage contribuicaoId="5" onNavigate={onNavigate} />)
    fireEvent.click(await screen.findByRole('button', { name: 'Excluir de vez' }))

    await waitFor(() => expect(onNavigate).toHaveBeenCalledWith('/moderacao'))
    expect(api.delete).toHaveBeenCalledWith('/moderacao/contribuicoes/5')
  })

  it('recusa um pedido de exclusão com justificativa', async () => {
    const comPedido = { ...base, conteudo_id: 7, estado: 'aprovada', exclusao_solicitada_em: '2026-11-24T12:00:00Z', motivo_exclusao: 'Achei um erro.' }
    api.get.mockResolvedValue(comPedido)
    api.post.mockResolvedValue({ ...comPedido, exclusao_solicitada_em: null, motivo_exclusao: null, justificativa_moderacao: 'Pedido de exclusão recusado: O texto está correto.' })

    render(<ModeracaoContribuicaoPage contribuicaoId="5" onNavigate={() => {}} />)
    fireEvent.click(await screen.findByRole('button', { name: 'Recusar pedido de exclusão' }))
    fireEvent.change(screen.getByRole('textbox', { name: /Por que o pedido de exclusão foi recusado/ }), { target: { value: 'O texto está correto.' } })
    fireEvent.click(screen.getByRole('button', { name: 'Recusar pedido' }))

    expect(await screen.findByText('Pedido de exclusão recusado: O texto está correto.')).toBeInTheDocument()
    expect(api.post).toHaveBeenCalledWith('/moderacao/contribuicoes/5/recusar-exclusao', { justificativa: 'O texto está correto.' })
  })
})
