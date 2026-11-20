// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import PageLayout, { AsideCard } from './PageLayout'

afterEach(() => {
  cleanup()
})

describe('PageLayout', () => {
  it('mostra o cabeçalho da página em faixa, com voltar, título e ações', () => {
    const onNavigate = vi.fn()

    render(
      <PageLayout
        onNavigate={onNavigate}
        back={{ href: '/base-de-conhecimentos', label: 'Voltar para a base' }}
        eyebrow="Base de conhecimento"
        title="Compiladores 1"
        description="Resumo da disciplina."
        actions={<button type="button">Copiar link</button>}
      >
        <p>Corpo da página</p>
      </PageLayout>,
    )

    expect(screen.getByRole('heading', { level: 1, name: 'Compiladores 1' })).toBeInTheDocument()
    expect(screen.getByText('Base de conhecimento', { selector: 'p' })).toHaveClass('page-header__eyebrow')
    expect(screen.getByText('Resumo da disciplina.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Copiar link' })).toBeInTheDocument()
    expect(screen.getByText('Corpo da página')).toBeInTheDocument()
    // Menu e rodapé fazem parte do layout.
    expect(screen.getByRole('navigation', { name: 'Navegação principal' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('link', { name: '← Voltar para a base' }))
    expect(onNavigate).toHaveBeenCalledWith('/base-de-conhecimentos')
  })

  it('mostra a coluna lateral quando recebe aside', () => {
    render(
      <PageLayout title="Meu perfil" aside={<AsideCard title="Sua conta"><p>Ana</p></AsideCard>} asideLabel="Resumo da conta">
        <p>Formulário</p>
      </PageLayout>,
    )

    const lateral = screen.getByRole('complementary', { name: 'Resumo da conta' })
    expect(within(lateral).getByRole('heading', { name: 'Sua conta' })).toBeInTheDocument()
    expect(within(lateral).getByText('Ana')).toBeInTheDocument()
  })

  it('sem aside, usa a largura de leitura quando pedida', () => {
    const { container } = render(
      <PageLayout title="Guia" width="narrow">
        <p>Texto</p>
      </PageLayout>,
    )

    expect(container.querySelector('.page-narrow')).toContainElement(screen.getByText('Texto'))
    expect(screen.queryByRole('complementary')).not.toBeInTheDocument()
  })
})
