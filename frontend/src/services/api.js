const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'
const SESSION_STORAGE_KEY = 'unb-core-session'
// Disparado quando a API recusa o token da sessão (expirado ou inválido).
export const EVENTO_SESSAO_EXPIRADA = 'unb-core:sessao-expirada'
const MENSAGEM_SESSAO_EXPIRADA = 'Sua sessão expirou. Entre de novo para continuar.'

export class ApiError extends Error {
  constructor(message, { code = 'ERRO_INTERNO', id = null, status = 0, details = null } = {}) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.id = id
    this.status = status
    this.details = details
  }
}

function readStoredSession() {
  try {
    const storedSession = localStorage.getItem(SESSION_STORAGE_KEY)
    return storedSession ? JSON.parse(storedSession) : null
  } catch {
    return null
  }
}

export function getSession() {
  return readStoredSession()
}

export function setSession(session) {
  localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session))
  return session
}

export function clearSession() {
  localStorage.removeItem(SESSION_STORAGE_KEY)
}

function getAccessToken(session) {
  return session?.access_token || session?.token || session?.accessToken
}

function getErrorPayload(payload) {
  const error = payload?.erro || payload?.error

  return {
    code: error?.codigo || error?.code || 'ERRO_INTERNO',
    message: error?.mensagem || error?.message || 'Não foi possível concluir a solicitação.',
    id: error?.id || null,
    details: error,
  }
}

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || ''

  if (!contentType.includes('application/json')) {
    return null
  }

  try {
    return await response.json()
  } catch {
    return null
  }
}

export async function request(path, options = {}) {
  const { body, headers = {}, ...fetchOptions } = options
  const session = getSession()
  const token = getAccessToken(session)
  const requestHeaders = new Headers(headers)

  if (body !== undefined && !requestHeaders.has('Content-Type')) {
    requestHeaders.set('Content-Type', 'application/json')
  }

  if (token) {
    requestHeaders.set('Authorization', `Bearer ${token}`)
  }

  let response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...fetchOptions,
      headers: requestHeaders,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch (error) {
    // Requisições canceladas (troca de página, StrictMode) não são falha de conexão.
    if (error?.name === 'AbortError') {
      throw error
    }

    throw new ApiError('Não foi possível conectar à API.', {
      code: 'FONTE_INDISPONIVEL',
      details: error,
    })
  }

  const payload = await parseResponse(response)

  if (!response.ok) {
    const error = getErrorPayload(payload)

    // O token enviado foi recusado: a sessão guardada não vale mais.
    if (response.status === 401 && token) {
      clearSession()
      window.dispatchEvent(new Event(EVENTO_SESSAO_EXPIRADA))
      throw new ApiError(MENSAGEM_SESSAO_EXPIRADA, { ...error, status: response.status })
    }

    throw new ApiError(error.message, {
      ...error,
      status: response.status,
    })
  }

  return payload
}

export const api = {
  request,
  get: (path, options) => request(path, { ...options, method: 'GET' }),
  post: (path, body, options) => request(path, { ...options, method: 'POST', body }),
  patch: (path, body, options) => request(path, { ...options, method: 'PATCH', body }),
  delete: (path, options) => request(path, { ...options, method: 'DELETE' }),
}

export default api