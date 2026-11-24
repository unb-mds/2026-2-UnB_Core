// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import MinhasContribuicoesPage from './MinhasContribuicoesPage'

vi.mock('../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { get: vi.fn(), patch: vi.fn() },
}))

vi.mock('../state/auth', () => ({
  useAuth: vi.fn(),
  logout: vi.fn(),
}))

function contribuicao(dados) {
  return {
    tipo: 'resumo',
    corpo_ou_url: 'Texto da contribuição.',
    origem: null,
    disciplina_codigo: 'FGA0003',
    disciplina_nome: 'COMPILADORES 1',
    criado_em: '2026-11-20T12:00:00Z',
    atualizado_em: '2026-11-21T12:00:00Z',
    justificativa_moderacao: null,
    exclusao_solicitada_em: null,
    ...dados,
  }
}

const pendente = contribuicao({ id: 1, titulo: 'Resumo de análise léxica', estado: 'pendente' })
const comAjustes = contribuicao({ id: 2, tipo: 'dica', titulo: 'Dica de estudo para a P1', estado: 'ajustes', justificativa_moderacao: 'Cite a fonte do material.' })
const aprovada = contribuicao({ id: 3, tipo: 'link', titulo: 'Playlist de Compiladores', estado: 'aprovada' })

// Os números do resumo lateral, como { 'Em revisão': '1', ... }.
function resumo() {
  const aside = screen.getByRole('complementary', { name: 'Resumo das contribuições' })
  return Object.fromEntries(within(aside).getAllByRole('term').map((dt) => [dt.textContent, dt.nextElementSibling.textContent]))
}

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('MinhasContribuicoesPage sem login', () => {
  it('pede para entrar e não chama a API', () => {
    useAuth.mockReturnValue({ isAuthenticated: false, user: null })
    const onNavigate = vi.fn()
    render(<MinhasContribuicoesPage onNavigate={onNavigate} />)

    expect(screen.getByText('Entre para acompanhar seus envios')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(onNavigate).toHaveBeenCalledWith('/login')
    expect(api.get).not.toHaveBeenCalled()
  })
})

describe('MinhasContribuicoesPage com login', () => {
  beforeEach(() => {
    useAuth.mockReturnValue({ isAuthenticated: true, user: { id: 1, perfil: 'usuario' } })
  })

  it('lista as contribuições com o estado, o tipo e a orientação da moderação', async () => {
    api.get.mockResolvedValue([pendente, comAjustes, aprovada])
    render(<MinhasContribuicoesPage onNavigate={() => {}} />)

    expect(await screen.findByRole('heading', { name: 'Resumo de análise léxica' })).toBeInTheDocument()
    expect(api.get).toHaveBeenCalledWith('/contribuicoes/minhas', expect.anything())

    const cartaoAjustes = screen.getByRole('heading', { name: 'Dica de estudo para a P1' }).closest('article')
    expect(within(cartaoAjustes).getByText('Ajustes solicitados')).toBeInTheDocument()
    expect(within(cartaoAjustes).getByText('Dica de estudo')).toHaveClass('tipo-dica')
    expect(within(cartaoAjustes).getByText('Cite a fonte do material.')).toBeInTheDocument()
    expect(within(cartaoAjustes).getByText('FGA0003 - COMPILADORES 1')).toBeInTheDocument()

    expect(resumo()).toMatchObject({ 'Em revisão': '1', 'Com ajustes solicitados': '1', Publicadas: '1', Rejeitadas: '0' })
    expect(screen.getByText(/Uma contribuição precisa de ajustes/)).toBeInTheDocument()
  })

  it('mostra um convite quando a pessoa ainda não enviou nada', async () => {
    api.get.mockResolvedValue([])
    const onNavigate = vi.fn()
    render(<MinhasContribuicoesPage onNavigate={onNavigate} />)

    expect(await screen.findByText('Você ainda não enviou contribuições')).toBeInTheDocument()
    // Sem contribuições, não há resumo lateral.
    expect(screen.queryByRole('complementary')).not.toBeInTheDocument()
  })

  it('mostra o erro quando a lista não carrega', async () => {
    api.get.mockRejectedValue(new ApiError('Não foi possível conectar à API.'))
    render(<MinhasContribuicoesPage onNavigate={() => {}} />)

    expect(await screen.findByText('Não foi possível conectar à API.')).toBeInTheDocument()
    expect(screen.queryByText('Você ainda não enviou contribuições')).not.toBeInTheDocument()
  })

  it('leva para a página da contribuição em "Ver detalhes"', async () => {
    api.get.mockResolvedValue([pendente])
    const onNavigate = vi.fn()
    render(<MinhasContribuicoesPage onNavigate={onNavigate} />)

    fireEvent.click(await screen.findByRole('button', { name: 'Ver detalhes' }))

    expect(onNavigate).toHaveBeenCalledWith('/minhas-contribuicoes/1')
  })

  it('edita na própria lista, e a contribuição volta para revisão', async () => {
    api.get.mockResolvedValue([comAjustes])
    api.patch.mockResolvedValue({ ...comAjustes, titulo: 'Dica de estudo para a P1 (com fonte)', origem: 'Livro do Aho', estado: 'pendente', justificativa_moderacao: null })
    render(<MinhasContribuicoesPage onNavigate={() => {}} />)

    fireEvent.click(await screen.findByRole('button', { name: 'Editar' }))
    fireEvent.change(screen.getByLabelText(/^Título/), { target: { value: 'Dica de estudo para a P1 (com fonte)' } })
    fireEvent.change(screen.getByLabelText(/^Fonte/), { target: { value: 'Livro do Aho' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salvar alterações' }))

    expect(await screen.findByRole('heading', { name: 'Dica de estudo para a P1 (com fonte)' })).toBeInTheDocument()
    expect(api.patch).toHaveBeenCalledWith('/contribuicoes/minhas/2', {
      tipo: 'dica',
      titulo: 'Dica de estudo para a P1 (com fonte)',
      corpo_ou_url: 'Texto da contribuição.',
      origem: 'Livro do Aho',
    })
    expect(screen.getByText('Pendente')).toBeInTheDocument()
    expect(screen.queryByText('Cite a fonte do material.')).not.toBeInTheDocument()
  })

  it('não salva a edição com campo obrigatório vazio e permite cancelar', async () => {
    api.get.mockResolvedValue([pendente])
    render(<MinhasContribuicoesPage onNavigate={() => {}} />)

    fireEvent.click(await screen.findByRole('button', { name: 'Editar' }))
    fireEvent.change(screen.getByLabelText(/^Título/), { target: { value: '  ' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salvar alterações' }))

    expect(screen.getByText('Preencha os campos obrigatórios: título.')).toBeInTheDocument()
    expect(api.patch).not.toHaveBeenCalled()

    fireEvent.click(screen.getByRole('button', { name: 'Cancelar' }))
    await waitFor(() => expect(screen.queryByRole('button', { name: 'Salvar alterações' })).not.toBeInTheDocument())
    expect(screen.getByRole('heading', { name: 'Resumo de análise léxica' })).toBeInTheDocument()
  })
})
