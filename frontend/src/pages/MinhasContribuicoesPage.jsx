import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import StatusBadge from '../components/ui/StatusBadge'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import './MinhasContribuicoesPage.css'

function formatDate(value) {
  if (!value) return 'Data não informada'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium' }).format(date)
}

function ContributionCard({ contribution }) {
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
      {contribution.justificativa && (
        <div className="my-contribution-card__feedback">
          <strong>Orientação da moderação</strong>
          <p>{contribution.justificativa}</p>
        </div>
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

    api
      .get('/contribuicoes/minhas', { signal: controller.signal })
      .then((response) => setContributions(response?.itens || response?.contribuicoes || []))
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') {
          setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível carregar suas contribuições.')
        }
      })
      .finally(() => setIsLoading(false))

    return () => controller.abort()
  }, [isAuthenticated])

  return (
    <div className="my-contributions-shell">
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
        {isLoading && <p className="my-contributions__status">Carregando contribuições...</p>}
        {error && <ErrorMessage>{error}</ErrorMessage>}
        {!isLoading && !error && isAuthenticated && contributions.length === 0 && (
          <EmptyState title="Você ainda não enviou contribuições">
            Compartilhe um resumo, uma dica ou um material útil com outros estudantes.
            <span className="my-contributions__action"><Button onClick={() => onNavigate('/contribuicao')}>Enviar contribuição</Button></span>
          </EmptyState>
        )}
        {!isLoading && !error && contributions.length > 0 && (
          <section className="my-contributions-list" aria-label="Lista de contribuições">
            {contributions.map((contribution) => <ContributionCard key={contribution.id} contribution={contribution} />)}
          </section>
        )}
      </main>
      <SiteFooter />
    </div>
  )
}

export default MinhasContribuicoesPage