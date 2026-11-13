import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import TabelaEntidades from '../components/admin/TabelaEntidades'
import EntidadeFormModal from '../components/admin/EntidadeFormModal'
import './MinhasContribuicoesPage.css'
import './governance.css'

const entityConfig = {
  publicacoes: { label: 'Publicações', fields: [{ name: 'titulo', label: 'Título' }, { name: 'descricao', label: 'Descrição' }] },
  fontes: { label: 'Fontes', fields: [{ name: 'nome', label: 'Nome' }, { name: 'url', label: 'URL', type: 'url' }] },
  categorias: { label: 'Categorias', fields: [{ name: 'nome', label: 'Nome' }] },
  disciplinas: { label: 'Disciplinas', fields: [{ name: 'nome', label: 'Nome' }, { name: 'codigo', label: 'Código' }] },
}

function AdminPage({ onNavigate }) {
  const { user, isAuthenticated } = useAuth()
  const allowed = user?.perfil === 'administrador'
  const [activeEntity, setActiveEntity] = useState('publicacoes')
  const [rows, setRows] = useState([])
  const [editing, setEditing] = useState(null)
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const config = entityConfig[activeEntity]

  useEffect(() => {
    if (!allowed) return
    setIsLoading(true)
    setError(null)
    api.get(`/administracao/${activeEntity}`)
      .then((response) => setRows(response?.itens || response || []))
      .catch((requestError) => setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível carregar o catálogo.'))
      .finally(() => setIsLoading(false))
  }, [activeEntity, allowed])

  useEffect(() => {
    if (!isAuthenticated) onNavigate?.('/login')
    else if (!allowed) onNavigate?.('/')
  }, [isAuthenticated, allowed, onNavigate])

  async function save(data) {
    setIsSubmitting(true)
    setError(null)
    try {
      const path = `/administracao/${activeEntity}${data.id ? `/${data.id}` : ''}`
      await (data.id ? api.patch(path, data) : api.post(path, data))
      setEditing(null)
      const response = await api.get(`/administracao/${activeEntity}`)
      setRows(response?.itens || response || [])
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível salvar o registro.')
    } finally {
      setIsSubmitting(false)
    }
  }

  async function archive(row) {
    try {
      await api.delete(`/administracao/${activeEntity}/${row.id}`)
      setRows((current) => current.filter((item) => item.id !== row.id))
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível arquivar o registro.')
    }
  }

  if (!isAuthenticated || !allowed) {
    return <EmptyState title="Acesso restrito">Somente administradores podem acessar esta área.</EmptyState>
  }

  return (
    <div className="my-contributions-shell page-shell">
      <SiteHeader active="conhecimento" onNavigate={onNavigate} />
      <main className="my-contributions-page">
        <header className="my-contributions-page__header"><p className="my-contributions-page__eyebrow">Administração do catálogo</p><h1>Gerenciar conteúdos</h1><p>Crie, edite e arquive entidades usadas na Base de Conhecimento.</p></header>
        {error && <ErrorMessage>{error}</ErrorMessage>}
        <div className="governance-tabs" role="tablist" aria-label="Entidades do catálogo">
          {Object.entries(entityConfig).map(([key, item]) => <button key={key} type="button" role="tab" aria-selected={activeEntity === key} className={activeEntity === key ? 'governance-tab governance-tab--active' : 'governance-tab'} onClick={() => setActiveEntity(key)}>{item.label}</button>)}
        </div>
        <div className="governance-toolbar"><h2>{config.label}</h2><Button onClick={() => setEditing({})}>Novo registro</Button></div>
        <TabelaEntidades columns={config.fields.map((field) => ({ key: field.name, label: field.label }))} rows={rows} isLoading={isLoading} onEdit={setEditing} onDelete={archive} />
        <EntidadeFormModal entity={editing && config.label.slice(0, -1)} initialData={editing} fields={config.fields} onClose={() => setEditing(null)} onSubmit={save} isSubmitting={isSubmitting} />
      </main>
      <SiteFooter />
    </div>
  )
}

export default AdminPage
