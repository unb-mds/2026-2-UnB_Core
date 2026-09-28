import { useState } from 'react'
import { api, ApiError } from '../services/api'
import { login } from '../state/auth'
import AuthForm from '../components/auth/AuthForm'
import './AuthPage.css'

function LoginPage({ onNavigate }) {
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleLogin(form) {
    setIsSubmitting(true)
    setError(null)

    try {
      const session = await api.post('/auth/login', { email: form.email, senha: form.senha })
      login(session)
      onNavigate('/editais')
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível entrar na conta.')
      throw requestError
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="auth-page-shell">
      <a className="auth-brand" href="/" onClick={(event) => { event.preventDefault(); onNavigate('/') }}>
        unb<span>core</span>
      </a>
      <main className="auth-page">
        <section className="auth-layout auth-layout--login" aria-labelledby="login-title">
          <div className="auth-message"><span className="auth-dots" aria-hidden="true" />Olá,<br />Bem vindo!</div>
          <section className="auth-card" aria-labelledby="login-title">
            <h1 id="login-title">Login</h1>
            <AuthForm mode="login" onSubmit={handleLogin} isSubmitting={isSubmitting} error={error} onForgotPassword={() => {}} />
            <p className="auth-card__switch">Não tem conta ainda? <a href="/cadastro" onClick={(event) => { event.preventDefault(); onNavigate('/cadastro') }}>Crie agora</a></p>
          </section>
        </section>
      </main>
    </div>
  )
}

export default LoginPage