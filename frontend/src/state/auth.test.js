// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const CHAVE_SESSAO = 'unb-core-session'

function token(exp) {
  const payload = btoa(JSON.stringify({ sub: '1', exp })).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
  return `cabecalho.${payload}.assinatura`
}

const agoraEmSegundos = () => Math.floor(Date.now() / 1000)

beforeEach(() => {
  localStorage.clear()
  sessionStorage.clear()
  vi.resetModules()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('sessão de login', () => {
  it('reconhece um token vencido pelo campo exp', async () => {
    const { tokenExpirado } = await import('./auth')

    expect(tokenExpirado(token(agoraEmSegundos() - 60))).toBe(true)
    expect(tokenExpirado(token(agoraEmSegundos() + 600))).toBe(false)
    // Token sem formato JWT não derruba a sessão.
    expect(tokenExpirado('dev-bypass')).toBe(false)
  })

  it('descarta ao abrir o site uma sessão com token vencido', async () => {
    localStorage.setItem(CHAVE_SESSAO, JSON.stringify({ access_token: token(agoraEmSegundos() - 60), usuario: { perfil: 'administrador' } }))

    const { refreshAuth } = await import('./auth')

    expect(refreshAuth()).toBeNull()
    expect(localStorage.getItem(CHAVE_SESSAO)).toBeNull()
  })

  it('mantém a sessão com token válido', async () => {
    const sessao = { access_token: token(agoraEmSegundos() + 600), usuario: { perfil: 'usuario' } }
    localStorage.setItem(CHAVE_SESSAO, JSON.stringify(sessao))

    const { refreshAuth } = await import('./auth')

    expect(refreshAuth()).toEqual(sessao)
  })

  it('encerra a sessão quando a API recusa o token (401) e avisa na tela de login', async () => {
    localStorage.setItem(CHAVE_SESSAO, JSON.stringify({ access_token: token(agoraEmSegundos() + 600), usuario: { perfil: 'administrador' } }))
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 401,
      headers: { get: () => 'application/json' },
      json: async () => ({ erro: { codigo: 'NAO_AUTENTICADO', mensagem: 'Token inválido ou expirado' } }),
    })

    const { consumirAvisoDeLogin, subscribe } = await import('./auth')
    const { api } = await import('../services/api')
    const ouvinte = vi.fn()
    subscribe(ouvinte)

    await expect(api.get('/usuarios/gestao')).rejects.toThrow('Sua sessão expirou')

    expect(localStorage.getItem(CHAVE_SESSAO)).toBeNull()
    expect(ouvinte).toHaveBeenCalled()
    expect(consumirAvisoDeLogin()).toBe('Sua sessão expirou. Entre de novo para continuar.')
    // O aviso aparece uma vez só.
    expect(consumirAvisoDeLogin()).toBeNull()
  })

  it('erro 401 sem sessão (ex.: login errado) não dispara o aviso', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: false,
      status: 401,
      headers: { get: () => 'application/json' },
      json: async () => ({ erro: { codigo: 'NAO_AUTENTICADO', mensagem: 'É necessário entrar.' } }),
    })

    const { consumirAvisoDeLogin } = await import('./auth')
    const { api } = await import('../services/api')

    await expect(api.get('/usuarios/gestao')).rejects.toThrow('É necessário entrar.')
    expect(consumirAvisoDeLogin()).toBeNull()
  })
})
