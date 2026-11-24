import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import PageLayout, { AsideCard } from '../components/layout/PageLayout'
import DecisaoModal from '../components/moderacao/DecisaoModal'
import StatusBadge from '../components/moderacao/StatusBadge'
import { formatarData, rotuloDisciplinaDoConteudo, rotuloTipo, trecho } from '../components/conteudos/formatacao'
import './MinhasContribuicoesPage.css'
import './governance.css'

const ABAS = [
  { filtro: 'revisar', rotulo: 'Para revisar', vazio: 'Nenhuma contribuição esperando revisão.' },
  { filtro: 'exclusao', rotulo: 'Pedidos de exclusão', vazio: 'Nenhum pedido de exclusão no momento.' },
  { filtro: 'todas', rotulo: 'Todas', vazio: 'Ainda não há contribuições.' },
]

function ModeracaoPage({ onNavigate }) {
  const { user, isAuthenticated } = useAuth()
  const canModerate = ['moderador', 'administrador'].includes(user?.perfil)
  const [filtro, setFiltro] = useState('revisar')
  const [contributions, setContributions] = useState([])
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(canModerate)
  const [selectedContribution, setSelectedContribution] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function loadContributions(filtroAtual = filtro) {
    setIsLoading(true)
    setError(null)
    api.get(`/moderacao/contribuicoes?filtro=${filtroAtual}`)
      .then((response) => setContributions(Array.isArray(response) ? response : []))
      .catch((requestError) => setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível carregar a moderação.'))
      .finally(() => setIsLoading(false))
  }

  useEffect(() => {
    // Recarrega quando a aba ou a permissão mudam.
    if (canModerate) loadContributions(filtro)
  }, [canModerate, filtro])

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

  const abaAtual = ABAS.find((aba) => aba.filtro === filtro)
  const pendentes = contributions.filter((item) => item.estado === 'pendente').length
  const aguardandoAjustes = contributions.filter((item) => item.estado === 'ajustes').length

  const aside = isAuthenticated && canModerate && (
    <>
      {filtro !== 'exclusao' && (
        <AsideCard title={filtro === 'todas' ? 'Nesta lista' : 'Fila de revisão'}>
          <dl className="aside-stats">
            <div><dt>Para revisar</dt><dd>{pendentes}</dd></div>
            <div><dt>Aguardando ajustes do autor</dt><dd>{aguardandoAjustes}</dd></div>
          </dl>
        </AsideCard>
      )}
      <AsideCard title="Boas práticas">
        <ul>
          <li>Ao pedir ajustes, explique o que mudar: o autor vê a justificativa.</li>
          <li>Prefira ajustes a rejeitar quando o material puder ser aproveitado.</li>
          <li>Excluir apaga a contribuição e o conteúdo publicado, sem volta. Use para conteúdo impróprio ou a pedido do autor.</li>
        </ul>
      </AsideCard>
    </>
  )

  return (
    <PageLayout
      onNavigate={onNavigate}
      eyebrow="Equipe de moderação"
      title="Revisar contribuições"
      description="Avalie as contribuições pendentes, responda aos pedidos de exclusão e consulte o histórico."
      aside={aside}
      asideLabel="Fila de revisão"
      width="narrow"
    >
      {!isAuthenticated || !canModerate ? (
        <EmptyState title="Acesso restrito">Somente moderadores e administradores podem acessar esta área.</EmptyState>
      ) : (
        <>
          <div className="governance-tabs" role="tablist" aria-label="Filtrar contribuições">
            {ABAS.map((aba) => (
              <button
                key={aba.filtro}
                type="button"
                role="tab"
                aria-selected={filtro === aba.filtro}
                className={`governance-tab ${filtro === aba.filtro ? 'governance-tab--active' : ''}`}
                onClick={() => setFiltro(aba.filtro)}
              >
                {aba.rotulo}
              </button>
            ))}
          </div>
          {isLoading && <p className="page-status">Carregando contribuições...</p>}
          {error && <ErrorMessage>{error}</ErrorMessage>}
          {!isLoading && !error && contributions.length === 0 && <EmptyState title={abaAtual.vazio}>Volte mais tarde ou escolha outra aba.</EmptyState>}
          {!isLoading && contributions.length > 0 && (
            <section className="my-contributions-list" aria-label="Contribuições para moderação">
              {contributions.map((contribution) => (
                <article className="my-contribution-card" key={contribution.id}>
                  <div className="my-contribution-card__heading">
                    <span className="badge badge-category">{rotuloTipo(contribution.tipo)}</span>
                    <span className="moderation-card__badges">
                      {contribution.exclusao_solicitada_em && <span className="badge badge-exclusao">Exclusão solicitada</span>}
                      <StatusBadge status={contribution.estado} />
                    </span>
                  </div>
                  <h2>{contribution.titulo}</h2>
                  <p className="moderation-card__meta">
                    {rotuloDisciplinaDoConteudo(contribution)} · por {contribution.autor_nome || 'autor não informado'} · {formatarData(contribution.atualizado_em, 'medium')}
                  </p>
                  <p>{trecho(contribution.corpo_ou_url)}</p>
                  {contribution.motivo_exclusao && (
                    <div className="my-contribution-card__feedback">
                      <strong>Motivo do pedido de exclusão</strong>
                      <p>{contribution.motivo_exclusao}</p>
                    </div>
                  )}
                  <span className="my-contribution-card__actions">
                    <Button variant="outline" onClick={() => onNavigate?.(`/moderacao/contribuicoes/${contribution.id}`)}>Ver detalhes</Button>
                    {contribution.estado === 'pendente' && (
                      <Button onClick={() => setSelectedContribution(contribution)}>Tomar decisão</Button>
                    )}
                  </span>
                </article>
              ))}
            </section>
          )}
        </>
      )}
      <DecisaoModal item={selectedContribution} onClose={() => setSelectedContribution(null)} onSubmit={(decision) => decide(selectedContribution.id, decision)} isSubmitting={isSubmitting} />
    </PageLayout>
  )
}

export default ModeracaoPage
