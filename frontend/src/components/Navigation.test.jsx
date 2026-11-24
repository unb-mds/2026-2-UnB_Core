// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import Navigation, { secaoAtiva } from './Navigation'
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

describe('item ativo do menu', () => {
  it.each([
    ['/', 'inicio'],
    ['/base-de-conhecimentos', 'conhecimento'],
    ['/conteudos/7', 'conhecimento'],
    ['/contribuicao', 'contribuir'],
    ['/guia-de-contribuicao', 'contribuir'],
    ['/minhas-contribuicoes', 'minhas'],
    ['/minhas-contribuicoes/5', 'minhas'],
    ['/moderacao', 'moderacao'],
    ['/admin/usuarios', 'usuarios'],
    ['/perfil', 'perfil'],
    ['/perfil/', 'perfil'],
    ['/endereco-que-nao-existe', 'conhecimento'],
    // A antiga página /admin foi removida: vale como endereço desconhecido.
    ['/admin', 'conhecimento'],
  ])('%s acende "%s"', (caminho, esperado) => {
    expect(secaoAtiva(caminho)).toBe(esperado)
  })

  it('marca só o link da página atual, com aria-current', () => {
    window.history.replaceState({}, '', '/minhas-contribuicoes/5')

    render(<Navigation onNavigate={() => {}} />)

    const atual = screen.getByRole('link', { name: 'Minhas contribuições' })
    expect(atual).toHaveAttribute('aria-current', 'page')
    expect(atual).toHaveClass('topbar__link--active')
    expect(screen.getByRole('link', { name: 'Base de conhecimento' })).not.toHaveAttribute('aria-current')
    expect(document.querySelectorAll('[aria-current="page"]')).toHaveLength(1)

    window.history.replaceState({}, '', '/')
  })
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
