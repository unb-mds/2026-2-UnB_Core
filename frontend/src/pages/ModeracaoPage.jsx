import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import './MinhasContribuicoesPage.css'

const decisions = [
  { value: 'aprovar', label: 'Aprovar' },
  { value: 'ajustes', label: 'Solicitar ajustes' },
  { value: 'rejeitar', label: 'Rejeitar' },
  { value: 'arquivar', label: 'Arquivar' },
]

function ModeracaoPage({ onNavigate }) {
  const { user, isAuthenticated } = useAuth()
  const canModerate = ['moderador', 'administrador'].includes(user?.perfil)
  const [contributions, setContributions] = useState([])
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(canModerate)

  function loadContributions() {
    setIsLoading(true)
    api.get('/moderacao/contribuicoes')
      .then((response) => setContributions(response || []))
      .catch((requestError) => setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível carregar a moderação.'))
      .finally(() => setIsLoading(false))
  }

  useEffect(() => {
    if (canModerate) loadContributions()
  }, [canModerate])

  async function decide(id, decisao) {
    const justificativa = window.prompt('Justificativa (opcional):') || undefined
    try {
      await api.post(`/moderacao/contribuicoes/${id}/decisao`, { decisao, justificativa })
      loadContributions()
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível registrar a decisão.')
    }
  }

  return (
    <div className="my-contributions-shell page-shell">
      <SiteHeader active="conhecimento" onNavigate={onNavigate} />
      <main className="my-contributions-page">
        <header className="my-contributions-page__header">
          <p className="my-contributions-page__eyebrow">Equipe de moderação</p>
          <h1>Revisar contribuições</h1>
          <p>Avalie as contribuições pendentes antes da publicação.</p>
        </header>
        {!isAuthenticated || !canModerate ? (
          <EmptyState title="Acesso restrito">Somente moderadores e administradores podem acessar esta área.</EmptyState>
        ) : (
          <>
            {isLoading && <p className="my-contributions__status">Carregando contribuições...</p>}
            {error && <ErrorMessage>{error}</ErrorMessage>}
            {!isLoading && !error && contributions.length === 0 && <EmptyState title="Nenhuma contribuição pendente">Todas as contribuições foram revisadas.</EmptyState>}
            <section className="my-contributions-list" aria-label="Contribuições para moderação">
              {contributions.map((contribution) => (
                <article className="my-contribution-card" key={contribution.id}>
                  <div className="my-contribution-card__heading">
                    <span className="badge badge-category">{contribution.tipo}</span>
                    <span>{contribution.estado}</span>
                  </div>
                  <h2>{contribution.titulo}</h2>
                  <p>{contribution.corpo_ou_url}</p>
                  <div className="contribution-form__type-options">
                    {decisions.map((decision) => (
                      <Button key={decision.value} variant="outline" onClick={() => decide(contribution.id, decision.value)}>
                        {decision.label}
                      </Button>
                    ))}
                  </div>
                </article>
              ))}
            </section>
          </>
        )}
      </main>
      <SiteFooter />
    </div>
  )
}

export default ModeracaoPage
