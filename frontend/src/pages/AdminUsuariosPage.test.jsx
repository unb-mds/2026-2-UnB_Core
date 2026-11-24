// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../services/api'
import { useAuth } from '../state/auth'
import AdminUsuariosPage from './AdminUsuariosPage'

vi.mock('../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

vi.mock('../state/auth', () => ({
  useAuth: vi.fn(),
  logout: vi.fn(),
}))

const bia = { id: 3, nome: 'Bia Estudante', email: null, perfil: 'usuario', ativo: true, criado_em: '2026-11-20T12:00:00Z', total_contribuicoes: 2 }

beforeEach(() => {
  vi.spyOn(window, 'confirm').mockReturnValue(true)
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
  vi.restoreAllMocks()
})

describe('AdminUsuariosPage', () => {
  it('moderador vê só usuários comuns, sem abas de equipe nem ações de administrador', async () => {
    useAuth.mockReturnValue({ isAuthenticated: true, user: { id: 9, perfil: 'moderador' } })
    api.get.mockResolvedValue([bia])

    render(<AdminUsuariosPage onNavigate={() => {}} />)

    expect(await screen.findByRole('heading', { name: 'Bia Estudante' })).toBeInTheDocument()
    expect(screen.getByText(/2 contribuições/)).toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: 'Equipe' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Senha temporária' })).not.toBeInTheDocument()
    expect(screen.queryByRole('combobox', { name: 'Perfil de Bia Estudante' })).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Desativar' }))
    await waitFor(() => expect(api.patch).toHaveBeenCalledWith('/usuarios/3/situacao', { ativo: false }))

    fireEvent.click(screen.getByRole('button', { name: 'Excluir conta' }))
    await waitFor(() => expect(api.delete).toHaveBeenCalledWith('/usuarios/3'))
    expect(window.confirm.mock.calls[0][0]).toContain('Usuário removido')
  })

  it('administrador vê a equipe primeiro e pode definir senha temporária em Todos', async () => {
    useAuth.mockReturnValue({ isAuthenticated: true, user: { id: 1, perfil: 'administrador' } })
    const admin = { ...bia, id: 1, nome: 'Ana Admin', email: 'admin@example.com', perfil: 'administrador', total_contribuicoes: 0 }
    api.get.mockImplementation((path) => Promise.resolve(path.includes('perfil=equipe') ? [admin] : [admin, { ...bia, email: 'bia@example.com' }]))
    api.post.mockResolvedValue({})

    render(<AdminUsuariosPage onNavigate={() => {}} />)

    expect(await screen.findByRole('heading', { name: 'Ana Admin (você)' })).toBeInTheDocument()
    expect(api.get).toHaveBeenCalledWith('/usuarios/gestao?perfil=equipe', expect.anything())
    // A própria conta não tem ações de desativar ou excluir.
    expect(screen.queryByRole('button', { name: 'Excluir conta' })).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('tab', { name: 'Todos os usuários' }))
    expect(await screen.findByText(/bia@example.com/)).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Senha temporária' }))
    fireEvent.change(screen.getByLabelText(/Nova senha temporária para Bia Estudante/), { target: { value: 'temporaria-123' } })
    fireEvent.click(screen.getByRole('button', { name: 'Definir senha' }))

    await waitFor(() => expect(api.post).toHaveBeenCalledWith('/usuarios/3/senha-temporaria', { nova_senha: 'temporaria-123' }))
    expect(await screen.findByText(/Senha temporária definida para Bia Estudante/)).toBeInTheDocument()
  })

  it('administrador vê os pedidos de senha com a data e o contato informado', async () => {
    useAuth.mockReturnValue({ isAuthenticated: true, user: { id: 1, perfil: 'administrador' } })
    const pedido = {
      ...bia,
      email: 'bia@example.com',
      recuperacao_senha_solicitada_em: '2026-11-24T13:00:00Z',
      contato_recuperacao: 'WhatsApp (61) 90000-0000',
    }
    api.get.mockImplementation((path) => Promise.resolve(path.includes('recuperacao=true') ? [pedido] : []))
    api.post.mockResolvedValue({})

    render(<AdminUsuariosPage onNavigate={() => {}} />)
    fireEvent.click(await screen.findByRole('tab', { name: 'Pedidos de senha' }))

    expect(await screen.findByText(/Contato informado: WhatsApp \(61\) 90000-0000/)).toBeInTheDocument()
    expect(api.get).toHaveBeenCalledWith('/usuarios/gestao?recuperacao=true', expect.anything())
    expect(screen.getByText('Pediu nova senha')).toBeInTheDocument()
    expect(screen.getByText(/Pedido de nova senha em/)).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Senha temporária' }))
    fireEvent.change(screen.getByLabelText(/Nova senha temporária para Bia Estudante/), { target: { value: 'temporaria-123' } })
    fireEvent.click(screen.getByRole('button', { name: 'Definir senha' }))

    await waitFor(() => expect(api.post).toHaveBeenCalledWith('/usuarios/3/senha-temporaria', { nova_senha: 'temporaria-123' }))
  })

  it('usuário comum não acessa a gestão', () => {
    useAuth.mockReturnValue({ isAuthenticated: true, user: { id: 5, perfil: 'usuario' } })

    render(<AdminUsuariosPage onNavigate={() => {}} />)

    expect(screen.getByText('Acesso restrito')).toBeInTheDocument()
    expect(api.get).not.toHaveBeenCalled()
  })
})
