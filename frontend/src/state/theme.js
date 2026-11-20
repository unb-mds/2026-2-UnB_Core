import { useSyncExternalStore } from 'react'

// Tema claro/escuro do site. O tema fica em <html data-theme="...">, e o CSS
// troca as cores pelos tokens de index.css. O index.html aplica o mesmo tema
// antes de a página aparecer, para não piscar em branco.
export const CHAVE_TEMA = 'unb-core-tema'
const CORES_BARRA = { light: '#1B3A8F', dark: '#0E1220' }
const listeners = new Set()

function temaSalvo() {
  try {
    const valor = localStorage.getItem(CHAVE_TEMA)
    return valor === 'dark' || valor === 'light' ? valor : null
  } catch {
    return null
  }
}

function consultaSistema() {
  return typeof window.matchMedia === 'function' ? window.matchMedia('(prefers-color-scheme: dark)') : null
}

function temaDoSistema() {
  return consultaSistema()?.matches ? 'dark' : 'light'
}

export function temaAtual() {
  return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light'
}

function aplicarTema(tema) {
  document.documentElement.dataset.theme = tema
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', CORES_BARRA[tema])
  listeners.forEach((listener) => listener())
}

export function alternarTema() {
  const novo = temaAtual() === 'dark' ? 'light' : 'dark'
  try {
    localStorage.setItem(CHAVE_TEMA, novo)
  } catch {
    // Sem localStorage (modo privado): o tema vale só até recarregar.
  }
  aplicarTema(novo)
}

// Chamado uma vez no main.jsx. Sem escolha salva, segue o tema do sistema,
// inclusive se ele mudar com o site aberto.
export function iniciarTema() {
  aplicarTema(temaSalvo() || temaDoSistema())
  consultaSistema()?.addEventListener?.('change', (evento) => {
    if (!temaSalvo()) aplicarTema(evento.matches ? 'dark' : 'light')
  })
}

function subscribe(listener) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export function useTema() {
  return useSyncExternalStore(subscribe, temaAtual, () => 'light')
}
