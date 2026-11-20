import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import StatusBadge from '../components/ui/StatusBadge'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import EditarContribuicaoForm from '../components/contribuicoes/EditarContribuicaoForm'
import { rotuloDisciplinaDoConteudo, rotuloTipo } from '../components/conteudos/formatacao'
import './ContribuicaoPage.css'
import './MinhasContribuicoesPage.css'

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

function ContributionCard({ contribution, onUpdated, onNavigate }) {
  const [isEditing, setIsEditing] = useState(false)
  const justificativa = contribution.justificativa_moderacao || contribution.justificativa

  return (
    <article className="my-contribution-card">
      <div className="my-contribution-card__heading">
        <span className="badge badge-category">{contribution.tipo ? rotuloTipo(contribution.tipo) : 'Contribuição'}</span>
        <StatusBadge status={contribution.estado || contribution.status || 'pendente'} />
      </div>
      <h2>{contribution.titulo || 'Contribuição sem título'}</h2>
      <dl className="my-contribution-card__metadata">
        {contribution.disciplina_nome && (
          <div>
            <dt>Disciplina</dt>
            <dd>{rotuloDisciplinaDoConteudo(contribution)}</dd>
          </div>
        )}
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
        <EditarContribuicaoForm
          contribution={contribution}
          onCancel={() => setIsEditing(false)}
          onSaved={(updated) => {
            setIsEditing(false)
            onUpdated(updated)
          }}
        />
      ) : (
        <span className="my-contribution-card__actions">
          <Button variant="outline" onClick={() => onNavigate?.(`/minhas-contribuicoes/${contribution.id}`)}>Ver detalhes</Button>
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
              <ContributionCard key={contribution.id} contribution={contribution} onUpdated={replaceContribution} onNavigate={onNavigate} />
            ))}
          </section>
        )}
      </main>
      <SiteFooter />
    </div>
  )
}

export default MinhasContribuicoesPage
