import './ui/ui.css'

function Navigation({ active = 'editais', onNavigate }) {
  function handleNavigate(event, path) {
    if (!onNavigate) {
      return
    }

    event.preventDefault()
    onNavigate(path)
  }

  return (
    <nav className="topbar" aria-label="Navegação principal">
      <a className="topbar__logo" href="/" onClick={(event) => handleNavigate(event, '/')}>
        unbcore
      </a>
      <div className="topbar__links">
        <a
          className={active === 'conhecimento' ? 'topbar__link--active' : ''}
          href="/base-de-conhecimentos"
          onClick={(event) => handleNavigate(event, '/base-de-conhecimentos')}
        >
          Base de conhecimento
        </a>
        <a
          className={active === 'editais' ? 'topbar__link--active' : ''}
          href="/editais"
          aria-current={active === 'editais' ? 'page' : undefined}
          onClick={(event) => handleNavigate(event, '/editais')}
        >
          Editais
        </a>
        <a className="topbar__login" href="/login" onClick={(event) => handleNavigate(event, '/login')}>
          Entrar
        </a>
      </div>
    </nav>
  )
}

export default Navigation