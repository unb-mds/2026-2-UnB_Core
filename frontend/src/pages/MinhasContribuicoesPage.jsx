import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import StatusBadge from '../components/ui/StatusBadge'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import './ContribuicaoPage.css'
import './MinhasContribuicoesPage.css'

const contentTypes = [
  { value: 'resumo', label: 'Resumo' },
  { value: 'dica', label: 'Dica de estudo' },
  { value: 'dificuldade', label: 'Dificuldade comum' },
  { value: 'prova', label: 'Prova' },
  { value: 'implementacao', label: 'Implementação' },
  { value: 'link', label: 'Link útil' },
]

function formatDate(value) {
  if (!value) return 'Data não informada'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium' }).format(date)
}

// O backend devolve a lista diretamente; mantém compatibilidade com formatos { itens }.
function extractContributions(response) {
  if (Array.isArray(response)) return response
  return response?.itens || response?.contribuicoes || []
}

function toEditForm(contribution) {
  return {
    tipo: contribution.tipo || '',
    titulo: contribution.titulo || '',
    corpo_ou_url: contribution.corpo_ou_url || '',
    origem: contribution.origem || '',
  }
}

function EditContributionForm({ contribution, onCancel, onSaved }) {
  const [form, setForm] = useState(() => toEditForm(contribution))
  const [error, setError] = useState(null)
  const [isSaving, setIsSaving] = useState(false)

  function updateField(event) {
    const { name, value } = event.target
    setForm((currentForm) => ({ ...currentForm, [name]: value }))
    setError(null)
  }

  async function submitEdit(event) {
    event.preventDefault()

    const missingFields = []
    if (!form.tipo) missingFields.push('tipo de conteúdo')
    if (!form.titulo.trim()) missingFields.push('título')
    if (!form.corpo_ou_url.trim()) missingFields.push('conteúdo ou URL')

    if (missingFields.length > 0) {
      setError(`Preencha os campos obrigatórios: ${missingFields.join(', ')}.`)
      return
    }

    setIsSaving(true)
    setError(null)

    try {
      const updated = await api.patch(`/contribuicoes/minhas/${contribution.id}`, {
        tipo: form.tipo,
        titulo: form.titulo.trim(),
        corpo_ou_url: form.corpo_ou_url.trim(),
        origem: form.origem.trim() || null,
      })
      onSaved(updated)
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível salvar a contribuição.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <form className="contribution-form my-contribution-card__edit" onSubmit={submitEdit} noValidate>
      <label>
        Tipo de conteúdo <span aria-hidden="true">*</span>
        <select name="tipo" value={form.tipo} onChange={updateField}>
          <option value="">Selecione um tipo</option>
          {contentTypes.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
        </select>
      </label>
      <label>
        Título <span aria-hidden="true">*</span>
        <input name="titulo" value={form.titulo} onChange={updateField} maxLength={200} />
      </label>
      <label>
        Conteúdo ou URL <span aria-hidden="true">*</span>
        <textarea name="corpo_ou_url" value={form.corpo_ou_url} onChange={updateField} rows="6" />
      </label>
      <label>
        Fonte / referência <span className="contribution-form__hint">(opcional)</span>
        <input name="origem" value={form.origem} onChange={updateField} maxLength={500} />
      </label>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      <div className="contribution-form__footer">
        <p><strong>Atenção:</strong> ao salvar, a contribuição volta para o estado pendente e passa por nova revisão.</p>
        <span className="my-contribution-card__actions">
          <Button variant="outline" onClick={onCancel} disabled={isSaving}>Cancelar</Button>
          <Button type="submit" disabled={isSaving}>{isSaving ? 'Salvando...' : 'Salvar alterações'}</Button>
        </span>
      </div>
    </form>
  )
}

function ContributionCard({ contribution, onUpdated }) {
  const [isEditing, setIsEditing] = useState(false)
  const justificativa = contribution.justificativa_moderacao || contribution.justificativa

  return (
    <article className="my-contribution-card">
      <div className="my-contribution-card__heading">
        <span className="badge badge-category">{contribution.tipo || 'Contribuição'}</span>
        <StatusBadge status={contribution.estado || contribution.status || 'pendente'} />
      </div>
      <h2>{contribution.titulo || 'Contribuição sem título'}</h2>
      <dl className="my-contribution-card__metadata">
        <div>
          <dt>Enviada em</dt>
          <dd>{formatDate(contribution.criado_em || contribution.data_criacao)}</dd>
        </div>
        <div>
          <dt>Atualizada em</dt>
          <dd>{formatDate(contribution.atualizado_em || contribution.data_atualizacao)}</dd>
        </div>
      </dl>
      {justificativa && (
        <div className="my-contribution-card__feedback">
          <strong>Orientação da moderação</strong>
          <p>{justificativa}</p>
        </div>
      )}
      {isEditing ? (
        <EditContributionForm
          contribution={contribution}
          onCancel={() => setIsEditing(false)}
          onSaved={(updated) => {
            setIsEditing(false)
            onUpdated(updated)
          }}
        />
      ) : (
        <span className="my-contribution-card__actions">
          <Button variant="outline" onClick={() => setIsEditing(true)}>Editar</Button>
        </span>
      )}
    </article>
  )
}

function MinhasContribuicoesPage({ onNavigate }) {
  const { isAuthenticated } = useAuth()
  const [contributions, setContributions] = useState([])
  const [isLoading, setIsLoading] = useState(Boolean(isAuthenticated))
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!isAuthenticated) return undefined

    const controller = new AbortController()
    setIsLoading(true)
    setError(null)

    api
      .get('/contribuicoes/minhas', { signal: controller.signal })
      .then((response) => setContributions(extractContributions(response)))
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') {
          setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível carregar suas contribuições.')
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false)
      })

    return () => controller.abort()
  }, [isAuthenticated])

  function replaceContribution(updated) {
    if (!updated?.id) return
    setContributions((current) => current.map((item) => (item.id === updated.id ? updated : item)))
  }

  return (
    <div className="my-contributions-shell page-shell">
      <SiteHeader active="conhecimento" onNavigate={onNavigate} />
      <main className="my-contributions-page">
        <header className="my-contributions-page__header">
          <p className="my-contributions-page__eyebrow">Área do colaborador</p>
          <h1>Minhas contribuições</h1>
          <p>Acompanhe o estado dos conteúdos que você enviou para a comunidade.</p>
        </header>

        {!isAuthenticated && (
          <EmptyState title="Entre para acompanhar seus envios">
            Sua lista de contribuições fica disponível somente para usuários autenticados.
            <span className="my-contributions__action"><Button onClick={() => onNavigate('/login')}>Entrar</Button></span>
          </EmptyState>
        )}
        {isAuthenticated && isLoading && <p className="my-contributions__status">Carregando contribuições...</p>}
        {error && <ErrorMessage>{error}</ErrorMessage>}
        {!isLoading && !error && isAuthenticated && contributions.length === 0 && (
          <EmptyState title="Você ainda não enviou contribuições">
            Compartilhe um resumo, uma dica ou um material útil com outros estudantes.
            <span className="my-contributions__action"><Button onClick={() => onNavigate('/contribuicao')}>Enviar contribuição</Button></span>
          </EmptyState>
        )}
        {!isLoading && !error && contributions.length > 0 && (
          <section className="my-contributions-list" aria-label="Lista de contribuições">
            {contributions.map((contribution) => (
              <ContributionCard key={contribution.id} contribution={contribution} onUpdated={replaceContribution} />
            ))}
          </section>
        )}
      </main>
      <SiteFooter />
    </div>
  )
}

export default MinhasContribuicoesPage
