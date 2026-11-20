// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import Navigation from './Navigation'
import { CHAVE_TEMA, iniciarTema } from '../state/theme'

function simularSistema(escuro) {
  window.matchMedia = vi.fn(() => ({ matches: escuro, addEventListener: vi.fn() }))
}

beforeEach(() => {
  localStorage.clear()
  document.documentElement.dataset.theme = 'light'
})

afterEach(() => {
  cleanup()
  delete window.matchMedia
})

describe('tema claro/escuro', () => {
  it('o botão do menu alterna o tema e guarda a escolha', () => {
    render(<Navigation onNavigate={() => {}} />)

    fireEvent.click(screen.getByRole('button', { name: 'Ativar tema escuro' }))

    expect(document.documentElement.dataset.theme).toBe('dark')
    expect(localStorage.getItem(CHAVE_TEMA)).toBe('dark')

    fireEvent.click(screen.getByRole('button', { name: 'Ativar tema claro' }))

    expect(document.documentElement.dataset.theme).toBe('light')
    expect(localStorage.getItem(CHAVE_TEMA)).toBe('light')
  })

  it('sem escolha salva, segue o tema do sistema', () => {
    simularSistema(true)

    iniciarTema()

    expect(document.documentElement.dataset.theme).toBe('dark')
  })

  it('a escolha salva vale mais que o tema do sistema', () => {
    simularSistema(true)
    localStorage.setItem(CHAVE_TEMA, 'light')

    iniciarTema()

    expect(document.documentElement.dataset.theme).toBe('light')
  })
})
