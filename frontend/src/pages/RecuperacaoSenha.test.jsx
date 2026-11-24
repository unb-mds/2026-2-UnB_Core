// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { api } from '../services/api'
import { consumirAvisoDeLogin, login, useAuth } from '../state/auth'
import LoginPage from './LoginPage'
import PerfilPage from './PerfilPage'

vi.mock('../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}))

vi.mock('../state/auth', () => ({
  useAuth: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
  consumirAvisoDeLogin: vi.fn(() => null),
}))

const MENSAGEM = 'Se o e-mail estiver cadastrado, o pedido foi registrado.'

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('Recuperação de senha na tela de login', () => {
  it('envia o pedido com o contato e mostra a resposta genérica', async () => {
    api.post.mockResolvedValue({ mensagem: MENSAGEM })
    render(<LoginPage onNavigate={() => {}} />)

    fireEvent.click(screen.getByRole('button', { name: 'Esqueceu a senha?' }))
    expect(screen.getByRole('heading', { name: 'Nova senha' })).toBeInTheDocument()

    fireEvent.change(screen.getByLabelText('E-mail da conta'), { target: { value: ' bia@example.com ' } })
    fireEvent.change(screen.getByLabelText(/Como prefere receber a senha/), { target: { value: 'Telegram @bia' } })
    fireEvent.click(screen.getByRole('button', { name: 'Pedir nova senha' }))

    await waitFor(() => expect(api.post).toHaveBeenCalledWith('/auth/recuperar-senha', { email: 'bia@example.com', contato: 'Telegram @bia' }))
    // Volta para o login com o aviso.
    expect(await screen.findByRole('status')).toHaveTextContent(MENSAGEM)
    expect(screen.getByRole('heading', { name: 'Login' })).toBeInTheDocument()
  })

  it('não envia o pedido sem um e-mail válido', () => {
    render(<LoginPage onNavigate={() => {}} />)

    fireEvent.click(screen.getByRole('button', { name: 'Esqueceu a senha?' }))
    fireEvent.click(screen.getByRole('button', { name: 'Pedir nova senha' }))

    expect(screen.getByText('Informe o e-mail da sua conta.')).toBeInTheDocument()
    expect(api.post).not.toHaveBeenCalled()
  })

  it('quem entra com senha temporária vai direto para Meu perfil', async () => {
    const sessao = { access_token: 'token', usuario: { id: 3, nome: 'Bia' }, trocar_senha: true }
    api.post.mockResolvedValue(sessao)
    const onNavigate = vi.fn()
    render(<LoginPage onNavigate={onNavigate} />)

    fireEvent.change(screen.getByLabelText('E-mail'), { target: { value: 'bia@example.com' } })
    fireEvent.change(screen.getByLabelText('Senha'), { target: { value: 'temporaria-123' } })
    fireEvent.click(screen.getByRole('button', { name: 'Entrar' }))

    await waitFor(() => expect(onNavigate).toHaveBeenCalledWith('/perfil'))
    expect(login).toHaveBeenCalledWith(sessao)
  })

  it('mostra o aviso de sessão expirada vindo de outra tela', () => {
    consumirAvisoDeLogin.mockReturnValueOnce('Sua sessão expirou. Entre novamente.')
    render(<LoginPage onNavigate={() => {}} />)

    expect(screen.getByRole('status')).toHaveTextContent('Sua sessão expirou')
  })
})

describe('Troca da senha temporária em Meu perfil', () => {
  it('avisa sobre a senha temporária e deixa de pedir a troca depois de salvar', async () => {
    const usuario = { id: 3, nome: 'Bia', email: 'bia@example.com', perfil: 'usuario' }
    const session = { access_token: 'token', usuario, trocar_senha: true }
    useAuth.mockReturnValue({ session, user: usuario, isAuthenticated: true })
    api.patch.mockResolvedValue(usuario)

    render(<PerfilPage onNavigate={() => {}} />)

    expect(screen.getByRole('alert')).toHaveTextContent('Você entrou com uma senha temporária')

    fireEvent.change(screen.getByLabelText('Nova senha'), { target: { value: 'minha-senha-nova' } })
    fireEvent.change(screen.getByLabelText('Confirmar nova senha'), { target: { value: 'minha-senha-nova' } })
    fireEvent.change(screen.getByLabelText(/Senha atual/), { target: { value: 'temporaria-123' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() => expect(api.patch).toHaveBeenCalledWith('/auth/me', { nova_senha: 'minha-senha-nova', senha_atual: 'temporaria-123' }))
    expect(login).toHaveBeenCalledWith({ ...session, usuario, trocar_senha: false })
  })
})
