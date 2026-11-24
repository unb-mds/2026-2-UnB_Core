// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import TipoBadge from './TipoBadge'
import ConteudoCard from './ConteudoCard'
import { classeTipo } from './formatacao'

afterEach(cleanup)

describe('Cores por tipo de conteúdo', () => {
  it('o badge mostra o nome do tipo, com a classe de cor e um ícone decorativo', () => {
    const { container } = render(<TipoBadge tipo="dica" />)

    const badge = screen.getByText('Dica de estudo')
    expect(badge).toHaveClass('badge', 'badge-tipo', 'tipo-dica')
    expect(container.querySelector('svg')).toHaveAttribute('aria-hidden', 'true')
  })

  it('tipo desconhecido fica com o azul do site e sem ícone', () => {
    const { container } = render(<TipoBadge tipo="outro" />)

    expect(screen.getByText('outro').className).toBe('badge badge-tipo')
    expect(container.querySelector('svg')).toBeNull()
    expect(classeTipo(undefined)).toBe('')
  })

  it('o card da Base de Conhecimento leva a cor do tipo na faixa lateral', () => {
    render(<ConteudoCard content={{ id: 1, tipo: 'link', titulo: 'Playlist de Cálculo' }} onOpen={() => {}} />)

    expect(screen.getByRole('article')).toHaveClass('knowledge-card', 'tipo-link')
    expect(screen.getByText('Link útil')).toHaveClass('tipo-link')
  })
})
