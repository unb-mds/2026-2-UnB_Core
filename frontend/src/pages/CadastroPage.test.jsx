// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from '../services/api'
import CadastroPage from './CadastroPage'

vi.mock('../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { post: vi.fn() },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

function preencher({ nome = 'Bia Estudante', email = 'bia@example.com', senha = 'senha-segura' } = {}) {
  fireEvent.change(screen.getByLabelText('Nome de usuário'), { target: { value: nome } })
  fireEvent.change(screen.getByLabelText('E-mail'), { target: { value: email } })
  fireEvent.change(screen.getByLabelText('Senha'), { target: { value: senha } })
  fireEvent.click(screen.getByRole('button', { name: 'Criar conta' }))
}

describe('CadastroPage', () => {
  it('cria a conta e leva para o login', async () => {
    api.post.mockResolvedValue({ id: 3, nome: 'Bia Estudante' })
    const onNavigate = vi.fn()
    render(<CadastroPage onNavigate={onNavigate} />)

    preencher()

    await waitFor(() => expect(onNavigate).toHaveBeenCalledWith('/login?cadastro=sucesso'))
    expect(api.post).toHaveBeenCalledWith('/auth/cadastro', { nome: 'Bia Estudante', email: 'bia@example.com', senha: 'senha-segura' })
  })

  it.each([
    ['sem nome', { nome: '   ' }, 'Informe seu nome para criar a conta.'],
    ['com e-mail inválido', { email: 'bia@example' }, 'Informe um e-mail válido.'],
    ['com senha curta', { senha: '1234567' }, 'A senha deve ter pelo menos 8 caracteres.'],
  ])('não envia o cadastro %s', (_caso, dados, mensagem) => {
    render(<CadastroPage onNavigate={() => {}} />)

    preencher(dados)

    expect(screen.getByText(mensagem)).toBeInTheDocument()
    expect(api.post).not.toHaveBeenCalled()
  })

  it('mostra o erro da API, como e-mail já cadastrado, e continua na página', async () => {
    api.post.mockRejectedValue(new ApiError('E-mail já cadastrado.', { status: 409 }))
    const onNavigate = vi.fn()
    render(<CadastroPage onNavigate={onNavigate} />)

    preencher()

    expect(await screen.findByText('E-mail já cadastrado.')).toBeInTheDocument()
    expect(onNavigate).not.toHaveBeenCalled()
    // O botão volta a ficar disponível para tentar de novo.
    expect(screen.getByRole('button', { name: 'Criar conta' })).toBeEnabled()
  })

  it('apaga o aviso de validação quando a pessoa corrige o campo', () => {
    render(<CadastroPage onNavigate={() => {}} />)

    preencher({ senha: '123' })
    expect(screen.getByText('A senha deve ter pelo menos 8 caracteres.')).toBeInTheDocument()

    fireEvent.change(screen.getByLabelText('Senha'), { target: { value: 'senha-segura' } })
    expect(screen.queryByText('A senha deve ter pelo menos 8 caracteres.')).not.toBeInTheDocument()
  })
})
