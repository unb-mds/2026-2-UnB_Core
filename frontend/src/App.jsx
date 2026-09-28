import { useEffect, useState } from 'react'
import ConhecimentoPage from './pages/ConhecimentoPage'
import CadastroPage from './pages/CadastroPage'
import ContribuicaoPage from './pages/ContribuicaoPage'
import MinhasContribuicoesPage from './pages/MinhasContribuicoesPage'
import LoginPage from './pages/LoginPage'
import PublicacaoDetalhePage from './pages/PublicacaoDetalhePage'
import PublicacoesPage from './pages/PublicacoesPage'

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

  if (path === '/minhas-contribuicoes') {
    return { name: 'my-contributions' }
  }

  return { name: 'publications' }
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
    return <ConhecimentoPage onNavigate={navigate} />
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

  if (route.name === 'my-contributions') {
    return <MinhasContribuicoesPage onNavigate={navigate} />
  }

  return <PublicacoesPage onSelectPublication={(publication) => navigate(`/editais/${publication.id}`)} onNavigate={navigate} />
}

export default App
