// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { useAuth } from '../state/auth'
import GuiaContribuicaoPage from './GuiaContribuicaoPage'

vi.mock('../state/auth', () => ({
  useAuth: vi.fn(() => ({ isAuthenticated: false, user: null })),
  logout: vi.fn(),
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('GuiaContribuicaoPage', () => {
  it('apresenta os tipos que podem ser enviados, cada um com a sua cor', () => {
    render(<GuiaContribuicaoPage onNavigate={() => {}} />)

    expect(useAuth).toHaveBeenCalled()
    for (const [rotulo, classe] of [
      ['Resumo', 'tipo-resumo'],
      ['Dica de estudo', 'tipo-dica'],
      ['Dificuldade comum', 'tipo-dificuldade'],
      ['Implementação', 'tipo-implementacao'],
      ['Link útil', 'tipo-link'],
    ]) {
      expect(screen.getByText(rotulo)).toHaveClass('badge-tipo', classe)
    }
  })

  it('leva para o formulário de contribuição', () => {
    const onNavigate = vi.fn()
    render(<GuiaContribuicaoPage onNavigate={onNavigate} />)

    fireEvent.click(screen.getByRole('button', { name: 'Começar minha contribuição' }))

    expect(onNavigate).toHaveBeenCalledWith('/contribuicao')
  })
})
