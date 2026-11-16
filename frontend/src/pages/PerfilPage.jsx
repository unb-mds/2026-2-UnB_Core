import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { login, useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import './MinhasContribuicoesPage.css'
import './ContribuicaoPage.css'
import './PerfilPage.css'

const perfilLabels = {
  usuario: 'Usuário',
  moderador: 'Moderador',
  administrador: 'Administrador',
}

function emptyForm(user) {
  return {
    nome: user?.nome || '',
    email: user?.email || '',
    senhaAtual: '',
    novaSenha: '',
    confirmacao: '',
  }
}

function PerfilPage({ onNavigate }) {
  const { session, user, isAuthenticated } = useAuth()
  const [form, setForm] = useState(() => emptyForm(user))
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) onNavigate?.('/login')
  }, [isAuthenticated, onNavigate])

  const nome = form.nome.trim()
  const email = form.email.trim().toLowerCase()
  const changesName = nome !== (user?.nome || '')
  const changesEmail = email !== (user?.email || '').toLowerCase()
  const changesPassword = form.novaSenha.length > 0
  const needsCurrentPassword = changesEmail || changesPassword

  function updateField(field) {
    return (event) => {
      setForm({ ...form, [field]: event.target.value })
      setError(null)
      setSuccess(null)
    }
  }

  async function submit(event) {
    event.preventDefault()
    setError(null)
    setSuccess(null)

    if (!nome) {
      setError('Informe o seu nome.')
      return
    }
    if (!changesName && !changesEmail && !changesPassword) {
      setError('Nenhum dado foi alterado.')
      return
    }
    if (changesPassword && form.novaSenha.length < 8) {
      setError('A nova senha precisa ter pelo menos 8 caracteres.')
      return
    }
    if (changesPassword && form.novaSenha !== form.confirmacao) {
      setError('A confirmação não confere com a nova senha.')
      return
    }
    if (needsCurrentPassword && !form.senhaAtual) {
      setError('Informe a sua senha atual para alterar o e-mail ou a senha.')
      return
    }

    const payload = {}
    if (changesName) payload.nome = nome
    if (changesEmail) payload.email = email
    if (changesPassword) payload.nova_senha = form.novaSenha
    if (needsCurrentPassword) payload.senha_atual = form.senhaAtual

    setIsSubmitting(true)
    try {
      const updatedUser = await api.patch('/auth/me', payload)
      // Mantém o token e troca só os dados do usuário guardados na sessão.
      login({ ...session, usuario: updatedUser })
      setForm(emptyForm(updatedUser))
      setSuccess('Seus dados foram atualizados.')
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível atualizar os seus dados.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="my-contributions-shell page-shell">
      <SiteHeader active="perfil" onNavigate={onNavigate} />
      <main className="my-contributions-page">
        <header className="my-contributions-page__header">
          <p className="my-contributions-page__eyebrow">Minha conta</p>
          <h1>Meu perfil</h1>
          <p>Atualize o seu nome, e-mail e senha de acesso.</p>
        </header>

        <section className="profile-summary" aria-label="Resumo da conta">
          <dl>
            <div><dt>Nome</dt><dd>{user?.nome}</dd></div>
            <div><dt>E-mail</dt><dd>{user?.email}</dd></div>
            <div><dt>Perfil</dt><dd>{perfilLabels[user?.perfil] || user?.perfil}</dd></div>
          </dl>
        </section>

        <form className="contribution-form" onSubmit={submit} noValidate>
          <div className="contribution-form__grid">
            <label>Nome<input value={form.nome} onChange={updateField('nome')} maxLength="120" autoComplete="name" required /></label>
            <label>E-mail<input type="email" value={form.email} onChange={updateField('email')} autoComplete="email" required /></label>
            <label>Nova senha<input type="password" value={form.novaSenha} onChange={updateField('novaSenha')} minLength="8" maxLength="128" autoComplete="new-password" placeholder="Deixe em branco para manter" /></label>
            <label>Confirmar nova senha<input type="password" value={form.confirmacao} onChange={updateField('confirmacao')} maxLength="128" autoComplete="new-password" disabled={!changesPassword} /></label>
          </div>
          {needsCurrentPassword && (
            <label>
              Senha atual
              <input type="password" value={form.senhaAtual} onChange={updateField('senhaAtual')} maxLength="128" autoComplete="current-password" required />
              <span className="contribution-form__hint">Necessária para alterar o e-mail ou a senha.</span>
            </label>
          )}
          {error && <ErrorMessage>{error}</ErrorMessage>}
          {success && <p className="profile-success" role="status">{success}</p>}
          <div className="profile-actions">
            <Button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Salvando...' : 'Salvar alterações'}</Button>
            <Button type="button" variant="outline" onClick={() => { setForm(emptyForm(user)); setError(null); setSuccess(null) }} disabled={isSubmitting}>Descartar</Button>
          </div>
        </form>
      </main>
      <SiteFooter />
    </div>
  )
}

export default PerfilPage
