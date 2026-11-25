// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from '../services/api'
import { consumirAvisoDeLogin, login } from '../state/auth'
import LoginPage from './LoginPage'

vi.mock('../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { post: vi.fn() },
}))

vi.mock('../state/auth', () => ({
  useAuth: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
  consumirAvisoDeLogin: vi.fn(() => null),
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

function entrar(email = 'bia@example.com', senha = 'senha-segura') {
  fireEvent.change(screen.getByLabelText('E-mail'), { target: { value: email } })
  fireEvent.change(screen.getByLabelText('Senha'), { target: { value: senha } })
  fireEvent.click(screen.getByRole('button', { name: 'Entrar' }))
}

function abrirRecuperacao() {
  fireEvent.click(screen.getByRole('button', { name: 'Esqueceu a senha?' }))
}

describe('LoginPage: entrar', () => {
  it('envia e-mail e senha e leva para a Base de Conhecimento', async () => {
    const sessao = { access_token: 'token', usuario: { id: 3 }, trocar_senha: false }
    api.post.mockResolvedValue(sessao)
    const onNavigate = vi.fn()
    render(<LoginPage onNavigate={onNavigate} />)

    entrar()

    await waitFor(() => expect(onNavigate).toHaveBeenCalledWith('/base-de-conhecimentos'))
    expect(api.post).toHaveBeenCalledWith('/auth/login', { email: 'bia@example.com', senha: 'senha-segura' })
    expect(login).toHaveBeenCalledWith(sessao)
  })

  it('mostra "Enviando..." enquanto espera a API', async () => {
    let responder
    api.post.mockReturnValue(new Promise((resolve) => { responder = resolve }))
    render(<LoginPage onNavigate={() => {}} />)

    entrar()

    expect(screen.getByRole('button', { name: 'Enviando...' })).toBeDisabled()
    responder({ access_token: 'token' })
    await waitFor(() => expect(login).toHaveBeenCalled())
  })

  it('mostra o erro da API, não entra e libera o botão de novo', async () => {
    api.post.mockRejectedValue(new ApiError('E-mail ou senha incorretos.', { status: 422 }))
    const onNavigate = vi.fn()
    render(<LoginPage onNavigate={onNavigate} />)

    entrar()

    expect(await screen.findByText('E-mail ou senha incorretos.')).toBeInTheDocument()
    expect(login).not.toHaveBeenCalled()
    expect(onNavigate).not.toHaveBeenCalled()
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeEnabled()
  })

  it('os links levam para o início e para o cadastro', () => {
    const onNavigate = vi.fn()
    render(<LoginPage onNavigate={onNavigate} />)

    fireEvent.click(screen.getByRole('link', { name: /unb/i }))
    fireEvent.click(screen.getByRole('link', { name: 'Crie agora' }))

    expect(onNavigate.mock.calls).toEqual([['/'], ['/cadastro']])
  })
})

describe('LoginPage: pedir uma senha nova', () => {
  it('o aviso da tela de login some ao abrir o pedido', () => {
    consumirAvisoDeLogin.mockReturnValueOnce('Sua sessão expirou. Entre novamente.')
    render(<LoginPage onNavigate={() => {}} />)
    expect(screen.getByRole('status')).toHaveTextContent('Sua sessão expirou')

    abrirRecuperacao()

    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it('"Voltar para o login" fecha o pedido e apaga o erro', () => {
    render(<LoginPage onNavigate={() => {}} />)
    abrirRecuperacao()
    fireEvent.click(screen.getByRole('button', { name: 'Pedir nova senha' }))
    expect(screen.getByText('Informe o e-mail da sua conta.')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Voltar para o login' }))

    expect(screen.getByRole('heading', { name: 'Login' })).toBeInTheDocument()
    expect(screen.queryByText('Informe o e-mail da sua conta.')).not.toBeInTheDocument()
  })

  it('contato só com espaços vai como vazio, e a resposta sem mensagem usa o aviso padrão', async () => {
    api.post.mockResolvedValue({})
    render(<LoginPage onNavigate={() => {}} />)
    abrirRecuperacao()

    fireEvent.change(screen.getByLabelText('E-mail da conta'), { target: { value: 'bia@example.com' } })
    fireEvent.change(screen.getByLabelText(/Como prefere receber a senha/), { target: { value: '   ' } })
    fireEvent.click(screen.getByRole('button', { name: 'Pedir nova senha' }))

    expect(await screen.findByRole('status')).toHaveTextContent('Pedido enviado. A equipe vai entrar em contato com você.')
    expect(api.post).toHaveBeenCalledWith('/auth/recuperar-senha', { email: 'bia@example.com', contato: null })

    // Ao abrir de novo, o formulário vem limpo.
    abrirRecuperacao()
    expect(screen.getByLabelText('E-mail da conta')).toHaveValue('')
  })

  it('mostra "Enviando..." enquanto o pedido vai para a API', async () => {
    let responder
    api.post.mockReturnValue(new Promise((resolve) => { responder = resolve }))
    render(<LoginPage onNavigate={() => {}} />)
    abrirRecuperacao()

    fireEvent.change(screen.getByLabelText('E-mail da conta'), { target: { value: 'bia@example.com' } })
    fireEvent.click(screen.getByRole('button', { name: 'Pedir nova senha' }))

    expect(screen.getByRole('button', { name: 'Enviando...' })).toBeDisabled()
    responder({ mensagem: 'Pedido registrado.' })
    expect(await screen.findByRole('status')).toHaveTextContent('Pedido registrado.')
  })

  it('mostra o erro da API e continua no pedido, com o botão liberado', async () => {
    api.post.mockRejectedValue(new ApiError('Muitos pedidos. Tente mais tarde.', { status: 429 }))
    render(<LoginPage onNavigate={() => {}} />)
    abrirRecuperacao()

    fireEvent.change(screen.getByLabelText('E-mail da conta'), { target: { value: 'bia@example.com' } })
    fireEvent.click(screen.getByRole('button', { name: 'Pedir nova senha' }))

    expect(await screen.findByText('Muitos pedidos. Tente mais tarde.')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Nova senha' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Pedir nova senha' })).toBeEnabled()
  })

  it('usa uma mensagem padrão quando a falha não vem da API', async () => {
    api.post.mockRejectedValue(new Error('falha inesperada'))
    render(<LoginPage onNavigate={() => {}} />)
    abrirRecuperacao()

    fireEvent.change(screen.getByLabelText('E-mail da conta'), { target: { value: 'bia@example.com' } })
    fireEvent.click(screen.getByRole('button', { name: 'Pedir nova senha' }))

    expect(await screen.findByText('Não foi possível enviar o pedido.')).toBeInTheDocument()
  })
})
