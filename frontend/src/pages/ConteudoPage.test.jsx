// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError } from '../services/api'
import ConteudoPage from './ConteudoPage'

vi.mock('../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { get: vi.fn() },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

const conteudo = {
  id: 7,
  disciplina_id: 3,
  disciplina_codigo: 'FGA0003',
  disciplina_nome: 'COMPILADORES 1',
  tipo: 'resumo',
  titulo: 'Resumo de análise léxica',
  corpo_ou_url: 'Tokens, lexemas e autômatos.',
  autor_id: 1,
  autor_nome: 'Ana Souza',
  origem: 'https://exemplo.unb.br/aula-1',
  atualizado_em: '2026-11-20T12:00:00Z',
}

describe('ConteudoPage', () => {
  it('mostra o conteúdo publicado com disciplina, autoria e texto', async () => {
    api.get.mockResolvedValue(conteudo)

    render(<ConteudoPage conteudoId="7" onNavigate={() => {}} />)

    expect(await screen.findByRole('heading', { level: 1, name: 'Resumo de análise léxica' })).toBeInTheDocument()
    expect(api.get).toHaveBeenCalledWith('/conteudos/7', expect.anything())
    expect(screen.getByText('FGA0003 - COMPILADORES 1')).toBeInTheDocument()
    expect(screen.getByText('Ana Souza')).toBeInTheDocument()
    expect(screen.getByText('Resumo')).toBeInTheDocument()
    expect(screen.getByText('Tokens, lexemas e autômatos.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'https://exemplo.unb.br/aula-1' })).toHaveAttribute('href', conteudo.origem)
    // Na página não há botão de fechar nem link para a própria página.
    expect(screen.queryByLabelText('Fechar detalhes')).not.toBeInTheDocument()
    expect(screen.queryByText('Abrir página do conteúdo')).not.toBeInTheDocument()
  })

  it('mostra um link quando o conteúdo é uma URL e não transforma outros esquemas em link', async () => {
    api.get.mockResolvedValueOnce({ ...conteudo, corpo_ou_url: 'https://github.com/unb-mds' })
    render(<ConteudoPage conteudoId="7" onNavigate={() => {}} />)
    expect(await screen.findByRole('link', { name: 'Abrir material' })).toHaveAttribute('href', 'https://github.com/unb-mds')
    cleanup()

    api.get.mockResolvedValueOnce({ ...conteudo, corpo_ou_url: 'javascript:alert(1)' })
    render(<ConteudoPage conteudoId="7" onNavigate={() => {}} />)
    expect(await screen.findByText('javascript:alert(1)')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Abrir material' })).not.toBeInTheDocument()
  })

  it('avisa quando o conteúdo não existe', async () => {
    api.get.mockRejectedValue(new ApiError('O conteúdo publicado não foi encontrado.', { status: 404 }))

    render(<ConteudoPage conteudoId="999" onNavigate={() => {}} />)

    expect(await screen.findByText('Conteúdo não encontrado')).toBeInTheDocument()
  })
})
