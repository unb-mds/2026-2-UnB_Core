import { useSyncExternalStore } from 'react'
import { clearSession, getSession, setSession } from '../services/api'

const listeners = new Set()
let session = getSession()

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

  return {
    session: currentSession,
    user: currentSession?.usuario || currentSession?.user || null,
    isAuthenticated: Boolean(currentSession),
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