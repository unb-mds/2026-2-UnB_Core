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

describe('validade do token', () => {
  it('vence exatamente no instante do campo exp', async () => {
    const { tokenExpirado } = await import('./auth')

    expect(tokenExpirado(token(1000), 1000 * 1000)).toBe(true)
    expect(tokenExpirado(token(1001), 1000 * 1000)).toBe(false)
  })

  it('token sem o campo exp não é tratado como vencido', async () => {
    const { tokenExpirado } = await import('./auth')
    const semExp = `cabecalho.${btoa(JSON.stringify({ sub: '1' }))}.assinatura`

    expect(tokenExpirado(semExp)).toBe(false)
  })
})

describe('entrar e sair', () => {
  it('login guarda a sessão, avisa as telas e o useAuth passa a mostrar a pessoa', async () => {
    const { renderHook, act } = await import('@testing-library/react')
    const { login, logout, subscribe, useAuth } = await import('./auth')
    const sessao = { access_token: token(agoraEmSegundos() + 600), usuario: { nome: 'Bia', perfil: 'usuario' } }
    const ouvinte = vi.fn()
    const cancelar = subscribe(ouvinte)
    const { result } = renderHook(() => useAuth())

    expect(result.current).toEqual({ session: null, user: null, isAuthenticated: false })

    act(() => { login(sessao) })

    expect(JSON.parse(localStorage.getItem(CHAVE_SESSAO))).toEqual(sessao)
    expect(ouvinte).toHaveBeenCalledTimes(1)
    expect(result.current).toEqual({ session: sessao, user: sessao.usuario, isAuthenticated: true })

    // Depois de cancelar a inscrição, a tela não é mais avisada.
    cancelar()
    act(() => { logout() })

    expect(ouvinte).toHaveBeenCalledTimes(1)
    expect(localStorage.getItem(CHAVE_SESSAO)).toBeNull()
    expect(result.current).toEqual({ session: null, user: null, isAuthenticated: false })
  })

  it('aceita sessões antigas que guardavam a pessoa em "user"', async () => {
    const { renderHook } = await import('@testing-library/react')
    localStorage.setItem(CHAVE_SESSAO, JSON.stringify({ token: token(agoraEmSegundos() + 600), user: { nome: 'Caio' } }))
    const { useAuth } = await import('./auth')

    const { result } = renderHook(() => useAuth())

    expect(result.current.user).toEqual({ nome: 'Caio' })
    expect(result.current.isAuthenticated).toBe(true)
  })
})

describe('modo sem login de desenvolvimento', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
  })

  it('com VITE_SKIP_AUTH, o ambiente de desenvolvimento entra como administrador local', async () => {
    vi.stubEnv('DEV', true)
    vi.stubEnv('VITE_SKIP_AUTH', 'true')
    const { renderHook } = await import('@testing-library/react')
    const { useAuth } = await import('./auth')

    const { result } = renderHook(() => useAuth())

    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user).toEqual({ nome: 'Usuário local', perfil: 'administrador' })
    expect(result.current.session.access_token).toBe('dev-bypass')
  })

  it('VITE_ALLOW_NO_LOGIN também liga o modo, mas só no desenvolvimento', async () => {
    vi.stubEnv('DEV', true)
    vi.stubEnv('VITE_ALLOW_NO_LOGIN', 'true')
    const { renderHook } = await import('@testing-library/react')
    const { useAuth } = await import('./auth')

    expect(renderHook(() => useAuth()).result.current.isAuthenticated).toBe(true)
  })

  it('no site publicado (build de produção) o modo nunca liga, mesmo com a variável', async () => {
    vi.stubEnv('DEV', false)
    vi.stubEnv('VITE_SKIP_AUTH', 'true')
    vi.stubEnv('VITE_ALLOW_NO_LOGIN', 'true')
    const { renderHook } = await import('@testing-library/react')
    const { useAuth } = await import('./auth')

    const { result } = renderHook(() => useAuth())

    expect(result.current).toEqual({ session: null, user: null, isAuthenticated: false })
  })

  it('sem as variáveis, o desenvolvimento também exige login', async () => {
    vi.stubEnv('DEV', true)
    vi.stubEnv('VITE_SKIP_AUTH', 'false')
    vi.stubEnv('VITE_ALLOW_NO_LOGIN', 'false')
    const { renderHook } = await import('@testing-library/react')
    const { useAuth } = await import('./auth')

    expect(renderHook(() => useAuth()).result.current.isAuthenticated).toBe(false)
  })
})
