import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import './MinhasContribuicoesPage.css'

function AdminUsuariosPage({ onNavigate }) {
  const { user, isAuthenticated } = useAuth()
  const canAdminister = user?.perfil === 'administrador'
  const [users, setUsers] = useState([])
  const [form, setForm] = useState({ nome: '', email: '', senha: '', perfil: 'moderador' })
  const [error, setError] = useState(null)

  function loadUsers() {
    api.get('/usuarios')
      .then(setUsers)
      .catch((requestError) => setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível carregar os usuários.'))
  }

  useEffect(() => {
    if (canAdminister) loadUsers()
  }, [canAdminister])

  async function createUser(event) {
    event.preventDefault()
    setError(null)
    try {
      await api.post('/usuarios', form)
      setForm({ nome: '', email: '', senha: '', perfil: 'moderador' })
      loadUsers()
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível criar o usuário.')
    }
  }

  async function toggleUser(usuario) {
    try {
      await api.patch(`/usuarios/${usuario.id}`, { ativo: !usuario.ativo })
      loadUsers()
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível atualizar o usuário.')
    }
  }

  if (!isAuthenticated || !canAdminister) {
    return <EmptyState title="Acesso restrito">Somente administradores podem acessar esta área.</EmptyState>
  }

  return (
    <div className="my-contributions-shell page-shell">
      <SiteHeader active="conhecimento" onNavigate={onNavigate} />
      <main className="my-contributions-page">
        <header className="my-contributions-page__header">
          <p className="my-contributions-page__eyebrow">Administração</p>
          <h1>Usuários administrativos</h1>
          <p>Crie moderadores e administradores e controle o acesso às funções protegidas.</p>
        </header>
        {error && <ErrorMessage>{error}</ErrorMessage>}
        <form className="contribution-form" onSubmit={createUser}>
          <label>Nome<input value={form.nome} onChange={(event) => setForm({ ...form, nome: event.target.value })} required /></label>
          <label>E-mail<input type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required /></label>
          <label>Senha<input type="password" value={form.senha} onChange={(event) => setForm({ ...form, senha: event.target.value })} minLength="8" required /></label>
          <label>Perfil<select value={form.perfil} onChange={(event) => setForm({ ...form, perfil: event.target.value })}><option value="moderador">Moderador</option><option value="administrador">Administrador</option></select></label>
          <Button type="submit">Criar usuário</Button>
        </form>
        <section className="my-contributions-list" aria-label="Usuários cadastrados">
          {users.length === 0 ? <EmptyState title="Nenhum usuário cadastrado" /> : users.map((usuario) => (
            <article className="my-contribution-card" key={usuario.id}>
              <h2>{usuario.nome}</h2>
              <p>{usuario.email} · {usuario.perfil}</p>
              <Button variant="outline" onClick={() => toggleUser(usuario)}>{usuario.ativo ? 'Desativar' : 'Ativar'}</Button>
            </article>
          ))}
        </section>
      </main>
      <SiteFooter />
    </div>
  )
}

export default AdminUsuariosPage
