import { useEffect, useState } from 'react'
import HomePage from './pages/HomePage'
import ConhecimentoPage from './pages/ConhecimentoPage'
import CadastroPage from './pages/CadastroPage'
import ContribuicaoPage from './pages/ContribuicaoPage'
import GuiaContribuicaoPage from './pages/GuiaContribuicaoPage'
import MinhasContribuicoesPage from './pages/MinhasContribuicoesPage'
import LoginPage from './pages/LoginPage'
import ModeracaoPage from './pages/ModeracaoPage'
import PerfilPage from './pages/PerfilPage'
import AdminUsuariosPage from './pages/AdminUsuariosPage'
import AdminPage from './pages/AdminPage'
import ConteudoPage from './pages/ConteudoPage'
import MinhaContribuicaoPage from './pages/MinhaContribuicaoPage'

function getRoute() {
  const path = window.location.pathname.replace(/\/$/, '') || '/'

  if (path === '/') {
    return { name: 'home' }
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

  if (path === '/perfil') {
    return { name: 'profile' }
  }

  if (path === '/admin/usuarios') {
    return { name: 'admin-users' }
  }

  if (path === '/admin') {
    return { name: 'admin' }
  }

  const contentMatch = path.match(/^\/conteudos\/(\d+)$/)
  if (contentMatch) {
    return { name: 'content', id: contentMatch[1] }
  }

  const myContributionMatch = path.match(/^\/minhas-contribuicoes\/(\d+)$/)
  if (myContributionMatch) {
    return { name: 'my-contribution', id: myContributionMatch[1] }
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

  // `state` permite levar dados para a próxima página (ex.: a disciplina escolhida na home).
  function navigate(path, state = {}) {
    window.history.pushState(state, '', path)
    setRoute(getRoute())
  }

  if (route.name === 'home') {
    return <HomePage onNavigate={navigate} />
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

  if (route.name === 'profile') {
    return <PerfilPage onNavigate={navigate} />
  }

  if (route.name === 'admin-users') {
    return <AdminUsuariosPage onNavigate={navigate} />
  }

  if (route.name === 'admin') {
    return <AdminPage onNavigate={navigate} />
  }

  // A key recria a página ao trocar de id, sem reaproveitar o estado anterior.
  if (route.name === 'content') {
    return <ConteudoPage key={route.id} conteudoId={route.id} onNavigate={navigate} />
  }

  if (route.name === 'my-contribution') {
    return <MinhaContribuicaoPage key={route.id} contribuicaoId={route.id} onNavigate={navigate} />
  }

  return <ConhecimentoPage onNavigate={navigate} onContribute={() => navigate('/contribuicao')} />
}

export default App
