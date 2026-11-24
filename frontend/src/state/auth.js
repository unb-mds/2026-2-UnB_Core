import { useSyncExternalStore } from 'react'
import { clearSession, EVENTO_SESSAO_EXPIRADA, getSession, setSession } from '../services/api'

const listeners = new Set()

// O token (JWT) traz a data de expiração no campo "exp", em segundos.
export function tokenExpirado(token, agora = Date.now()) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return typeof payload.exp === 'number' && payload.exp * 1000 <= agora
  } catch {
    return false
  }
}

// Ao abrir o site, descarta uma sessão cujo token já venceu, para não mostrar
// o menu de quem está logado com um token que a API vai recusar.
function sessaoValida(sessao) {
  const token = sessao?.access_token || sessao?.token || sessao?.accessToken
  if (token && tokenExpirado(token)) {
    clearSession()
    return null
  }
  return sessao
}

let session = sessaoValida(getSession())
const authBypassEnabled = import.meta.env.DEV && (import.meta.env.VITE_SKIP_AUTH === 'true' || import.meta.env.VITE_ALLOW_NO_LOGIN === 'true')

function emitChange() {
  listeners.forEach((listener) => listener())
}

function subscribe(listener) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

function getSnapshot() {
  return session
}

function getServerSnapshot() {
  return null
}

export function useAuth() {
  const currentSession = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
  const devUser = authBypassEnabled ? { nome: 'Usuário local', perfil: 'administrador' } : null

  return {
    session: currentSession || (authBypassEnabled ? { usuario: devUser, access_token: 'dev-bypass' } : null),
    user: currentSession?.usuario || currentSession?.user || devUser,
    isAuthenticated: authBypassEnabled || Boolean(currentSession),
  }
}

export function login(sessionData) {
  session = setSession(sessionData)
  emitChange()
  return session
}

export function logout() {
  clearSession()
  session = null
  emitChange()
}

export function refreshAuth() {
  session = sessaoValida(getSession())
  emitChange()
  return session
}

// A API recusou o token (401) durante o uso: encerra a sessão em todas as telas.
// As páginas protegidas levam ao login quando a sessão some.
const CHAVE_AVISO_LOGIN = 'unb-core-aviso-login'

if (typeof window !== 'undefined') {
  window.addEventListener(EVENTO_SESSAO_EXPIRADA, () => {
    try {
      sessionStorage.setItem(CHAVE_AVISO_LOGIN, 'Sua sessão expirou. Entre de novo para continuar.')
    } catch {
      // Sem sessionStorage, a pessoa só não vê o aviso na tela de login.
    }
    session = null
    emitChange()
  })
}

// Lê (uma única vez) o aviso para a tela de login, como o de sessão expirada.
export function consumirAvisoDeLogin() {
  try {
    const aviso = sessionStorage.getItem(CHAVE_AVISO_LOGIN)
    sessionStorage.removeItem(CHAVE_AVISO_LOGIN)
    return aviso
  } catch {
    return null
  }
}

export { subscribe }