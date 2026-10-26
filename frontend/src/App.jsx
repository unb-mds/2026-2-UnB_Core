import { useEffect, useState } from 'react'
import ConhecimentoPage from './pages/ConhecimentoPage'
import CadastroPage from './pages/CadastroPage'
import ContribuicaoPage from './pages/ContribuicaoPage'
import GuiaContribuicaoPage from './pages/GuiaContribuicaoPage'
import MinhasContribuicoesPage from './pages/MinhasContribuicoesPage'
import LoginPage from './pages/LoginPage'
import PublicacaoDetalhePage from './pages/PublicacaoDetalhePage'
import PublicacoesPage from './pages/PublicacoesPage'
import ModeracaoPage from './pages/ModeracaoPage'
import AdminUsuariosPage from './pages/AdminUsuariosPage'

function getRoute() {
  const path = window.location.pathname.replace(/\/$/, '') || '/'
  const detailMatch = path.match(/^\/editais\/(\d+)$/)

  if (detailMatch) {
    return { name: 'publication-detail', id: detailMatch[1] }
  }

  if (path === '/base-de-conhecimentos') {
    return { name: 'knowledge' }
  }

  if (path === '/cadastro') {
    return { name: 'signup' }
  }

  if (path === '/login') {
    return { name: 'login' }
  }

  if (path === '/contribuicao') {
    return { name: 'contribution' }
  }

  if (path === '/guia-de-contribuicao') {
    return { name: 'contribution-guide' }
  }

  if (path === '/minhas-contribuicoes') {
    return { name: 'my-contributions' }
  }

  if (path === '/moderacao') {
    return { name: 'moderation' }
  }

  if (path === '/admin/usuarios') {
    return { name: 'admin-users' }
  }

  return { name: 'knowledge' }
}

function App() {
  const [route, setRoute] = useState(getRoute)

  useEffect(() => {
    function handlePopState() {
      setRoute(getRoute())
    }

    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  function navigate(path) {
    window.history.pushState({}, '', path)
    setRoute(getRoute())
  }

  if (route.name === 'publication-detail') {
    return <PublicacaoDetalhePage publicationId={route.id} onBack={() => navigate('/editais')} onNavigate={navigate} />
  }

  if (route.name === 'knowledge') {
    return <ConhecimentoPage onNavigate={navigate} onContribute={() => navigate('/contribuicao')} />
  }

  if (route.name === 'signup') {
    return <CadastroPage onNavigate={navigate} />
  }

  if (route.name === 'login') {
    return <LoginPage onNavigate={navigate} />
  }

  if (route.name === 'contribution') {
    return <ContribuicaoPage onNavigate={navigate} />
  }

  if (route.name === 'contribution-guide') {
    return <GuiaContribuicaoPage onNavigate={navigate} />
  }

  if (route.name === 'my-contributions') {
    return <MinhasContribuicoesPage onNavigate={navigate} />
  }

  if (route.name === 'moderation') {
    return <ModeracaoPage onNavigate={navigate} />
  }

  if (route.name === 'admin-users') {
    return <AdminUsuariosPage onNavigate={navigate} />
  }

  return <ConhecimentoPage onNavigate={navigate} onContribute={() => navigate('/contribuicao')} />
}

export default App
