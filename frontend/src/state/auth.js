import { useSyncExternalStore } from 'react'
import { clearSession, getSession, setSession } from '../services/api'

const listeners = new Set()
let session = getSession()
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
  const devUser = authBypassEnabled ? { nome: 'Usuário local', perfil: 'admin' } : null

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
  session = getSession()
  emitChange()
  return session
}

export { subscribe }