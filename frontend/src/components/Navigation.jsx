import './ui/ui.css'
import { logout, useAuth } from '../state/auth'

function Navigation({ active = 'editais', onNavigate }) {
  const { isAuthenticated } = useAuth()

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
        unb<span className="topbar__logo-accent">core</span>
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
        <a href="/contribuicao" onClick={(event) => handleNavigate(event, '/contribuicao')}>
          Contribuir
        </a>
        <a href="/minhas-contribuicoes" onClick={(event) => handleNavigate(event, '/minhas-contribuicoes')}>
          Minhas contribuições
        </a>
        {isAuthenticated ? (
          <>
            <a
              className="topbar__login"
              href="/login"
              onClick={(event) => {
                event.preventDefault()
                logout()
                onNavigate?.('/login')
              }}
            >
              Sair
            </a>
          </>
        ) : (
          <>
            <a className="topbar__login" href="/login" onClick={(event) => handleNavigate(event, '/login')}>
              Entrar
            </a>
            <a className="topbar__login" href="/cadastro" onClick={(event) => handleNavigate(event, '/cadastro')}>
              Criar conta
            </a>
          </>
        )}
      </div>
    </nav>
  )
}

export default Navigation