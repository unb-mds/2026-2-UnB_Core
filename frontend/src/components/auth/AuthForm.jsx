import { useState } from 'react'
import { ApiError } from '../../services/api'
import ErrorMessage from '../ErrorMessage'
import Button from '../ui/Button'
import './auth.css'

function AuthForm({ mode, onSubmit, isSubmitting = false, error, onForgotPassword }) {
  const isSignup = mode === 'signup'
  const [form, setForm] = useState({ nome: '', email: '', senha: '' })
  const [validationError, setValidationError] = useState(null)

  function updateField(event) {
    const { name, value } = event.target
    setForm((currentForm) => ({ ...currentForm, [name]: value }))
    setValidationError(null)
  }

  async function submitForm(event) {
    event.preventDefault()
    const emailIsValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)

    if (isSignup && !form.nome.trim()) {
      setValidationError('Informe seu nome para criar a conta.')
      return
    }

    if (!emailIsValid) {
      setValidationError('Informe um e-mail válido.')
      return
    }

    if (form.senha.length < 8) {
      setValidationError('A senha deve ter pelo menos 8 caracteres.')
      return
    }

    try {
      await onSubmit(form)
    } catch (submitError) {
      if (!(submitError instanceof ApiError)) {
        setValidationError('Não foi possível concluir. Tente novamente.')
      }
    }
  }

  return (
    <form className="auth-form" onSubmit={submitForm} noValidate>
      {isSignup && (
        <label>
          Nome de usuário
          <input name="nome" value={form.nome} onChange={updateField} autoComplete="name" required />
        </label>
      )}
      <label>
        E-mail
        <input name="email" type="email" value={form.email} onChange={updateField} autoComplete="email" required />
      </label>
      <label>
        Senha
        <input name="senha" type="password" value={form.senha} onChange={updateField} autoComplete={isSignup ? 'new-password' : 'current-password'} required />
      </label>
      {(validationError || error) && <ErrorMessage>{validationError || error}</ErrorMessage>}
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Enviando...' : isSignup ? 'Criar conta' : 'Entrar'}
      </Button>
      {!isSignup && (
        <button type="button" className="auth-form__forgot" onClick={onForgotPassword}>
          Esqueceu a senha?
        </button>
      )}
    </form>
  )
}

export default AuthForm