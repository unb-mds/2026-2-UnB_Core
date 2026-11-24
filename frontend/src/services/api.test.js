// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError, clearSession, getSession, setSession } from './api'

const BASE = 'http://127.0.0.1:8000/api/v1'

// Resposta falsa do fetch, só com o que o api.js usa.
function resposta(corpo, { status = 200, tipo = 'application/json' } = {}) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: { get: () => tipo },
    json: async () => corpo,
  }
}

beforeEach(() => {
  localStorage.clear()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('cliente da API', () => {
  it('envia o corpo em JSON para o endereço da API e devolve a resposta', async () => {
    const fetch = vi.spyOn(globalThis, 'fetch').mockResolvedValue(resposta({ id: 1 }))

    const dados = await api.post('/contribuicoes', { titulo: 'Resumo' })

    expect(dados).toEqual({ id: 1 })
    const [url, opcoes] = fetch.mock.calls[0]
    expect(url).toBe(`${BASE}/contribuicoes`)
    expect(opcoes.method).toBe('POST')
    expect(opcoes.body).toBe(JSON.stringify({ titulo: 'Resumo' }))
    expect(opcoes.headers.get('Content-Type')).toBe('application/json')
    // Sem sessão, não manda token.
    expect(opcoes.headers.has('Authorization')).toBe(false)
  })

  it('manda o token da sessão guardada no cabeçalho Authorization', async () => {
    setSession({ access_token: 'abc123', usuario: { id: 1 } })
    const fetch = vi.spyOn(globalThis, 'fetch').mockResolvedValue(resposta([]))

    await api.get('/contribuicoes/minhas')

    const [, opcoes] = fetch.mock.calls[0]
    expect(opcoes.method).toBe('GET')
    expect(opcoes.body).toBeUndefined()
    expect(opcoes.headers.get('Authorization')).toBe('Bearer abc123')
  })

  it('transforma o erro padrão do backend em ApiError com mensagem, código e status', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      resposta({ erro: { codigo: 'EMAIL_JA_CADASTRADO', mensagem: 'E-mail já cadastrado.', id: 'req-1' } }, { status: 409 }),
    )

    const erro = await api.post('/auth/cadastro', {}).catch((e) => e)

    expect(erro).toBeInstanceOf(ApiError)
    expect(erro.message).toBe('E-mail já cadastrado.')
    expect(erro.code).toBe('EMAIL_JA_CADASTRADO')
    expect(erro.status).toBe(409)
    expect(erro.id).toBe('req-1')
  })

  it('usa uma mensagem genérica quando o erro não vem no formato esperado', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(resposta(null, { status: 500, tipo: 'text/html' }))

    const erro = await api.get('/cursos').catch((e) => e)

    expect(erro.message).toBe('Não foi possível concluir a solicitação.')
    expect(erro.status).toBe(500)
  })

  it('avisa quando não consegue falar com a API (backend desligado)', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Failed to fetch'))

    const erro = await api.get('/cursos').catch((e) => e)

    expect(erro).toBeInstanceOf(ApiError)
    expect(erro.message).toBe('Não foi possível conectar à API.')
    expect(erro.code).toBe('FONTE_INDISPONIVEL')
  })

  it('repassa o cancelamento de uma requisição sem tratar como falha de conexão', async () => {
    const cancelamento = new DOMException('cancelada', 'AbortError')
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(cancelamento)

    await expect(api.get('/cursos')).rejects.toBe(cancelamento)
  })

  it('devolve null quando a resposta não tem corpo JSON (ex.: exclusão)', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(resposta(undefined, { status: 204, tipo: '' }))

    await expect(api.delete('/contribuicoes/minhas/5')).resolves.toBeNull()
  })

  it('guarda, lê e apaga a sessão no navegador', () => {
    setSession({ access_token: 'abc123' })
    expect(getSession()).toEqual({ access_token: 'abc123' })

    clearSession()
    expect(getSession()).toBeNull()

    // Sessão corrompida não quebra o site.
    localStorage.setItem('unb-core-session', '{inválido')
    expect(getSession()).toBeNull()
  })
})
