import { useState } from 'react'
import { api, ApiError } from '../services/api'
import { consumirAvisoDeLogin, login } from '../state/auth'
import AuthForm from '../components/auth/AuthForm'
import ErrorMessage from '../components/ErrorMessage'
import Button from '../components/ui/Button'
import '../components/auth/auth.css'
import './AuthPage.css'

const EMAIL_VALIDO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function LoginPage({ onNavigate }) {
  const [modo, setModo] = useState('login')
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  // Aviso vindo de outra tela (ex.: sessão expirada) ou o retorno do pedido de nova senha.
  const [aviso, setAviso] = useState(() => consumirAvisoDeLogin())
  const [recuperacao, setRecuperacao] = useState({ email: '', contato: '' })

  async function handleLogin(form) {
    setIsSubmitting(true)
    setError(null)

    try {
      const session = await api.post('/auth/login', { email: form.email, senha: form.senha })
      login(session)
      // Entrou com senha temporária: vai direto definir uma senha nova.
      onNavigate(session?.trocar_senha ? '/perfil' : '/base-de-conhecimentos')
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível entrar na conta.')
      throw requestError
    } finally {
      setIsSubmitting(false)
    }
  }

  function abrirRecuperacao() {
    setModo('recuperar')
    setAviso(null)
    setError(null)
  }

  function voltarAoLogin() {
    setModo('login')
    setError(null)
  }

  async function pedirNovaSenha(event) {
    event.preventDefault()
    if (!EMAIL_VALIDO.test(recuperacao.email.trim())) {
      setError('Informe o e-mail da sua conta.')
      return
    }

    setIsSubmitting(true)
    setError(null)
    try {
      const resposta = await api.post('/auth/recuperar-senha', {
        email: recuperacao.email.trim(),
        contato: recuperacao.contato.trim() || null,
      })
      setAviso(resposta?.mensagem || 'Pedido enviado. A equipe vai entrar em contato com você.')
      setRecuperacao({ email: '', contato: '' })
      setModo('login')
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível enviar o pedido.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const titulo = modo === 'recuperar' ? 'Nova senha' : 'Login'

  return (
    <div className="auth-page-shell page-shell">
      <a className="auth-brand" href="/" onClick={(event) => { event.preventDefault(); onNavigate('/') }}>
        unb<span>core</span>
      </a>
      <main className="auth-page">
        <section className="auth-layout auth-layout--login" aria-labelledby="login-title">
          <div className="auth-message"><span className="auth-dots" aria-hidden="true" />Olá,<br />Bem vindo!</div>
          <section className="auth-card" aria-labelledby="login-title">
            <h1 id="login-title">{titulo}</h1>
            {aviso && <p className="auth-card__notice" role="status">{aviso}</p>}

            {modo === 'login' ? (
              <AuthForm mode="login" onSubmit={handleLogin} isSubmitting={isSubmitting} error={error} onForgotPassword={abrirRecuperacao} />
            ) : (
              <form className="auth-form" onSubmit={pedirNovaSenha} noValidate>
                <p className="auth-card__help">
                  Informe o e-mail da sua conta. Um administrador vai definir uma senha temporária e passar para você.
                  Ao entrar com ela, você escolhe uma senha nova.
                </p>
                <label>
                  E-mail da conta
                  <input
                    type="email"
                    value={recuperacao.email}
                    onChange={(event) => setRecuperacao({ ...recuperacao, email: event.target.value })}
                    autoComplete="email"
                    required
                  />
                </label>
                <label>
                  Como prefere receber a senha? (opcional)
                  <input
                    value={recuperacao.contato}
                    onChange={(event) => setRecuperacao({ ...recuperacao, contato: event.target.value })}
                    maxLength={300}
                    placeholder="Ex.: WhatsApp, Telegram ou o próprio e-mail"
                  />
                </label>
                {error && <ErrorMessage>{error}</ErrorMessage>}
                <Button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Enviando...' : 'Pedir nova senha'}</Button>
                <button type="button" className="auth-form__forgot" onClick={voltarAoLogin}>
                  Voltar para o login
                </button>
              </form>
            )}

            <p className="auth-card__switch">Não tem conta ainda? <a href="/cadastro" onClick={(event) => { event.preventDefault(); onNavigate('/cadastro') }}>Crie agora</a></p>
          </section>
        </section>
      </main>
    </div>
  )
}

export default LoginPage
