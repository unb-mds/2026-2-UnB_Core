import './ui/ui.css'
import { logout, useAuth } from '../state/auth'
import { alternarTema, useTema } from '../state/theme'

// Qual item do menu fica aceso em cada endereço. Páginas internas acendem a seção
// a que pertencem (ex.: a página de um conteúdo acende a Base de conhecimento).
const SECOES = [
  { chave: 'inicio', caminhos: ['/'] },
  { chave: 'conhecimento', caminhos: ['/base-de-conhecimentos', '/conteudos/'] },
  { chave: 'contribuir', caminhos: ['/contribuicao', '/guia-de-contribuicao'] },
  { chave: 'minhas', caminhos: ['/minhas-contribuicoes'] },
  { chave: 'moderacao', caminhos: ['/moderacao'] },
  { chave: 'usuarios', caminhos: ['/admin'] },
  { chave: 'perfil', caminhos: ['/perfil'] },
]

export function secaoAtiva(pathname) {
  const caminho = pathname.replace(/\/$/, '') || '/'
  const secao = SECOES.find(({ caminhos }) => caminhos.some((prefixo) => (
    prefixo === '/' ? caminho === '/' : caminho === prefixo || caminho.startsWith(prefixo.endsWith('/') ? prefixo : `${prefixo}/`)
  )))
  // Endereços desconhecidos abrem a base de conhecimento (ver App.jsx).
  return secao?.chave || 'conhecimento'
}

function Navigation({ onNavigate }) {
  const { isAuthenticated, user } = useAuth()
  const tema = useTema()
  const ativa = secaoAtiva(window.location.pathname)
  const podeModerar = isAuthenticated && ['moderador', 'administrador'].includes(user?.perfil)

  const links = [
    { chave: 'inicio', href: '/', texto: 'Início' },
    { chave: 'conhecimento', href: '/base-de-conhecimentos', texto: 'Base de conhecimento' },
    { chave: 'contribuir', href: '/contribuicao', texto: 'Contribuir' },
    { chave: 'minhas', href: '/minhas-contribuicoes', texto: 'Minhas contribuições' },
    { chave: 'moderacao', href: '/moderacao', texto: 'Moderação', visivel: podeModerar },
    { chave: 'usuarios', href: '/admin/usuarios', texto: 'Usuários', visivel: user?.perfil === 'administrador' },
    { chave: 'perfil', href: '/perfil', texto: 'Meu perfil', visivel: isAuthenticated },
  ].filter((link) => link.visivel !== false)

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
        {links.map((link) => (
          <a
            key={link.chave}
            className={link.chave === ativa ? 'topbar__link--active' : undefined}
            aria-current={link.chave === ativa ? 'page' : undefined}
            href={link.href}
            onClick={(event) => handleNavigate(event, link.href)}
          >
            {link.texto}
          </a>
        ))}
        {isAuthenticated ? (
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
