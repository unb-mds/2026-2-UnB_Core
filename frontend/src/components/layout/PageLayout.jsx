import SiteHeader from '../SiteHeader'
import SiteFooter from '../SiteFooter'
import './layout.css'

/**
 * Estrutura padrão das páginas internas:
 * - faixa de cabeçalho de largura total, com link de voltar, eyebrow, título,
 *   descrição, ações e, opcionalmente, conteúdo extra (`headerContent`, ex.: filtros);
 * - corpo alinhado ao menu (mesma largura e margens da barra superior);
 * - coluna lateral opcional (`aside`), que vai para baixo do conteúdo em telas estreitas.
 *
 * `width="narrow"` limita o corpo à largura de leitura quando não há coluna lateral.
 */
function PageLayout({
  onNavigate,
  back,
  eyebrow,
  title,
  description,
  actions,
  headerContent,
  aside,
  asideLabel = 'Informações complementares',
  width = 'wide',
  children,
}) {
  function goBack(event) {
    if (!onNavigate) return
    event.preventDefault()
    onNavigate(back.href)
  }

  return (
    <div className="page-shell">
      <SiteHeader onNavigate={onNavigate} />
      <main>
        <header className="page-band">
          <div className="page-container page-header">
            {back && (
              <a className="page-header__back" href={back.href} onClick={goBack}>
                ← {back.label}
              </a>
            )}
            <div className="page-header__row">
              <div className="page-header__text">
                {eyebrow && <p className="page-header__eyebrow">{eyebrow}</p>}
                <h1>{title}</h1>
                {description && <p className="page-header__description">{description}</p>}
              </div>
              {actions && <div className="page-header__actions">{actions}</div>}
            </div>
            {headerContent && <div className="page-header__content">{headerContent}</div>}
          </div>
        </header>

        <div className="page-container page-body">
          {aside ? (
            <div className="page-columns">
              <div className="page-columns__main">{children}</div>
              <aside className="page-columns__aside" aria-label={asideLabel}>{aside}</aside>
            </div>
          ) : (
            <div className={width === 'narrow' ? 'page-narrow' : undefined}>{children}</div>
          )}
        </div>
      </main>
      <SiteFooter />
    </div>
  )
}

/** Cartão da coluna lateral. */
export function AsideCard({ title, children }) {
  return (
    <section className="aside-card">
      {title && <h2>{title}</h2>}
      {children}
    </section>
  )
}

export default PageLayout
