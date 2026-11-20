import './ui/ui.css'
import { logout, useAuth } from '../state/auth'
import { alternarTema, useTema } from '../state/theme'

function Navigation({ active = 'conhecimento', onNavigate }) {
  const { isAuthenticated, user } = useAuth()
  const tema = useTema()

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
          className={active === 'inicio' ? 'topbar__link--active' : ''}
          href="/"
          onClick={(event) => handleNavigate(event, '/')}
        >
          Início
        </a>
        <a
          className={active === 'conhecimento' ? 'topbar__link--active' : ''}
          href="/base-de-conhecimentos"
          onClick={(event) => handleNavigate(event, '/base-de-conhecimentos')}
        >
          Base de conhecimento
        </a>
        <a href="/contribuicao" onClick={(event) => handleNavigate(event, '/contribuicao')}>
          Contribuir
        </a>
        <a href="/minhas-contribuicoes" onClick={(event) => handleNavigate(event, '/minhas-contribuicoes')}>
          Minhas contribuições
        </a>
        {isAuthenticated && ['moderador', 'administrador'].includes(user?.perfil) && (
          <a href="/moderacao" onClick={(event) => handleNavigate(event, '/moderacao')}>
            Moderação
          </a>
        )}
        {user?.perfil === 'administrador' && (
          <a href="/admin/usuarios" onClick={(event) => handleNavigate(event, '/admin/usuarios')}>
            Usuários
          </a>
        )}
        {isAuthenticated ? (
          <>
            <a
              className={active === 'perfil' ? 'topbar__link--active' : ''}
              href="/perfil"
              onClick={(event) => handleNavigate(event, '/perfil')}
            >
              Meu perfil
            </a>
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
        <button
          type="button"
          className="topbar__theme"
          onClick={alternarTema}
          aria-label={tema === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro'}
          title={tema === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro'}
        >
          {tema === 'dark' ? <IconeSol /> : <IconeLua />}
        </button>
      </div>
    </nav>
  )
}

function IconeSol() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
    </svg>
  )
}

function IconeLua() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  )
}

export default Navigation