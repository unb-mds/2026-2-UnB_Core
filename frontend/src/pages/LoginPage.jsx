import { useState } from 'react'
import { api, ApiError } from '../services/api'
import { consumirAvisoDeLogin, login } from '../state/auth'
import AuthForm from '../components/auth/AuthForm'
import './AuthPage.css'

const AJUDA_SENHA = 'Peça a um administrador do UnB Core para definir uma senha temporária. Depois de entrar, troque a senha em Meu perfil.'

function LoginPage({ onNavigate }) {
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  // Aviso vindo de outra tela (ex.: sessão expirada) ou a ajuda de "Esqueceu a senha?".
  const [aviso, setAviso] = useState(() => consumirAvisoDeLogin())

  async function handleLogin(form) {
    setIsSubmitting(true)
    setError(null)

    try {
      const session = await api.post('/auth/login', { email: form.email, senha: form.senha })
      login(session)
      onNavigate('/base-de-conhecimentos')
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível entrar na conta.')
      throw requestError
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="auth-page-shell page-shell">
      <a className="auth-brand" href="/" onClick={(event) => { event.preventDefault(); onNavigate('/') }}>
        unb<span>core</span>
      </a>
      <main className="auth-page">
        <section className="auth-layout auth-layout--login" aria-labelledby="login-title">
          <div className="auth-message"><span className="auth-dots" aria-hidden="true" />Olá,<br />Bem vindo!</div>
          <section className="auth-card" aria-labelledby="login-title">
            <h1 id="login-title">Login</h1>
            {aviso && <p className="auth-card__notice" role="status">{aviso}</p>}
            <AuthForm mode="login" onSubmit={handleLogin} isSubmitting={isSubmitting} error={error} onForgotPassword={() => setAviso(AJUDA_SENHA)} />
            <p className="auth-card__switch">Não tem conta ainda? <a href="/cadastro" onClick={(event) => { event.preventDefault(); onNavigate('/cadastro') }}>Crie agora</a></p>
          </section>
        </section>
      </main>
    </div>
  )
}

export default LoginPage