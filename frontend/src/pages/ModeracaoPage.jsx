import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import PageLayout, { AsideCard } from '../components/layout/PageLayout'
import DecisaoModal from '../components/moderacao/DecisaoModal'
import StatusBadge from '../components/moderacao/StatusBadge'
import { rotuloTipo } from '../components/conteudos/formatacao'
import './MinhasContribuicoesPage.css'
import './governance.css'

function ModeracaoPage({ onNavigate }) {
  const { user, isAuthenticated } = useAuth()
  const canModerate = ['moderador', 'administrador'].includes(user?.perfil)
  const [contributions, setContributions] = useState([])
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(canModerate)
  const [selectedContribution, setSelectedContribution] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

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

  useEffect(() => {
    if (!isAuthenticated) onNavigate?.('/login')
    else if (!canModerate) onNavigate?.('/')
  }, [isAuthenticated, canModerate, onNavigate])

  async function decide(id, decision) {
    setIsSubmitting(true)
    try {
      await api.post(`/moderacao/contribuicoes/${id}/decisao`, decision)
      setSelectedContribution(null)
      loadContributions()
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível registrar a decisão.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const pendentes = contributions.filter((item) => item.estado === 'pendente').length
  const aguardandoAjustes = contributions.filter((item) => item.estado === 'ajustes').length

  const aside = isAuthenticated && canModerate && (
    <>
      <AsideCard title="Fila de revisão">
        <dl className="aside-stats">
          <div><dt>Para revisar</dt><dd>{pendentes}</dd></div>
          <div><dt>Aguardando ajustes do autor</dt><dd>{aguardandoAjustes}</dd></div>
        </dl>
      </AsideCard>
      <AsideCard title="Boas práticas">
        <ul>
          <li>Ao pedir ajustes, explique o que mudar: o autor vê a justificativa.</li>
          <li>Prefira ajustes a rejeitar quando o material puder ser aproveitado.</li>
          <li>Confira a fonte de materiais de terceiros antes de aprovar.</li>
        </ul>
      </AsideCard>
    </>
  )

  return (
    <PageLayout
      onNavigate={onNavigate}
      eyebrow="Equipe de moderação"
      title="Revisar contribuições"
      description="Avalie as contribuições pendentes antes da publicação."
      aside={aside}
      asideLabel="Fila de revisão"
      width="narrow"
    >
      {!isAuthenticated || !canModerate ? (
        <EmptyState title="Acesso restrito">Somente moderadores e administradores podem acessar esta área.</EmptyState>
      ) : (
        <>
          {isLoading && <p className="page-status">Carregando contribuições...</p>}
          {error && <ErrorMessage>{error}</ErrorMessage>}
          {!isLoading && !error && contributions.length === 0 && <EmptyState title="Nenhuma contribuição pendente">Todas as contribuições foram revisadas.</EmptyState>}
          <section className="my-contributions-list" aria-label="Contribuições para moderação">
            {contributions.map((contribution) => (
              <article className="my-contribution-card" key={contribution.id}>
                <div className="my-contribution-card__heading"><span className="badge badge-category">{rotuloTipo(contribution.tipo)}</span><StatusBadge status={contribution.estado} /></div>
                <h2>{contribution.titulo}</h2>
                <p>{contribution.corpo_ou_url}</p>
                <Button variant="outline" onClick={() => setSelectedContribution(contribution)}>Tomar decisão</Button>
              </article>
            ))}
          </section>
        </>
      )}
      <DecisaoModal item={selectedContribution} onClose={() => setSelectedContribution(null)} onSubmit={(decision) => decide(selectedContribution.id, decision)} isSubmitting={isSubmitting} />
    </PageLayout>
  )
}

export default ModeracaoPage
