import { useState } from 'react'
import { api, ApiError } from '../services/api'
import AuthForm from '../components/auth/AuthForm'
import './AuthPage.css'

function CadastroPage({ onNavigate }) {
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSignup(form) {
    setIsSubmitting(true)
    setError(null)

    try {
      await api.post('/auth/cadastro', form)
      onNavigate('/login?cadastro=sucesso')
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível criar sua conta.')
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
        <section className="auth-layout auth-layout--signup" aria-labelledby="signup-title">
          <section className="auth-card" aria-labelledby="signup-title">
            <h1 id="signup-title">Cadastro</h1>
            <AuthForm mode="signup" onSubmit={handleSignup} isSubmitting={isSubmitting} error={error} />
          </section>
          <div className="auth-message"><span className="auth-dots" aria-hidden="true" />Junte-se<br />a nós!</div>
        </section>
      </main>
    </div>
  )
}

export default CadastroPage