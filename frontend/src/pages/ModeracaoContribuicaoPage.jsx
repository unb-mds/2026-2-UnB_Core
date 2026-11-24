import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import PageLayout, { AsideCard } from '../components/layout/PageLayout'
import DecisaoModal from '../components/moderacao/DecisaoModal'
import StatusBadge from '../components/moderacao/StatusBadge'
import ConteudoCorpo, { TextoOuLink } from '../components/conteudos/ConteudoCorpo'
import { formatarData, rotuloDisciplinaDoConteudo } from '../components/conteudos/formatacao'
import TipoBadge from '../components/conteudos/TipoBadge'
import '../components/conteudos/conteudos.css'
import './MinhasContribuicoesPage.css'
import './ContribuicaoPage.css'

// O que cada estado significa para quem modera.
const SITUACOES = {
  pendente: 'Esperando a sua decisão: aprovar, pedir ajustes, rejeitar ou arquivar.',
  ajustes: 'Ajustes pedidos ao autor. Ela volta para revisão quando ele editar.',
  aprovada: 'Aprovada e publicada na base de conhecimento.',
  rejeitada: 'Rejeitada. O autor vê a justificativa.',
  arquivada: 'Arquivada, fora da base de conhecimento.',
}

function mensagem(requestError, padrao) {
  return requestError instanceof ApiError ? requestError.message : padrao
}

function ModeracaoContribuicaoPage({ contribuicaoId, onNavigate }) {
  const { user, isAuthenticated } = useAuth()
  const canModerate = ['moderador', 'administrador'].includes(user?.perfil)
  const [contribution, setContribution] = useState(null)
  const [notFound, setNotFound] = useState(false)
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(canModerate)
  const [isDeciding, setIsDeciding] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isRefusing, setIsRefusing] = useState(false)
  const [refusal, setRefusal] = useState('')

  useEffect(() => {
    if (!isAuthenticated) onNavigate?.('/login')
    else if (!canModerate) onNavigate?.('/')
  }, [isAuthenticated, canModerate, onNavigate])

  useEffect(() => {
    if (!canModerate) return undefined

    const controller = new AbortController()
    api
      .get(`/moderacao/contribuicoes/${contribuicaoId}`, { signal: controller.signal })
      .then(setContribution)
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return
        if (requestError instanceof ApiError && requestError.status === 404) setNotFound(true)
        else setError(mensagem(requestError, 'Não foi possível carregar a contribuição.'))
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false)
      })

    return () => controller.abort()
  }, [canModerate, contribuicaoId])

  async function decide(decision) {
    setIsSubmitting(true)
    setError(null)
    try {
      setContribution(await api.post(`/moderacao/contribuicoes/${contribuicaoId}/decisao`, decision))
      setIsDeciding(false)
    } catch (requestError) {
      setError(mensagem(requestError, 'Não foi possível registrar a decisão.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  async function excluir() {
    const confirmado = window.confirm(
      'Excluir esta contribuição de vez? O conteúdo publicado também será apagado. Não dá para desfazer.',
    )
    if (!confirmado) return
    setIsSubmitting(true)
    setError(null)
    try {
      await api.delete(`/moderacao/contribuicoes/${contribuicaoId}`)
      onNavigate?.('/moderacao')
    } catch (requestError) {
      setError(mensagem(requestError, 'Não foi possível excluir a contribuição.'))
      setIsSubmitting(false)
    }
  }

  async function recusarPedido(event) {
    event.preventDefault()
    if (refusal.trim().length < 5) {
      setError('Explique ao autor por que o pedido foi recusado (pelo menos 5 caracteres).')
      return
    }
    setIsSubmitting(true)
    setError(null)
    try {
      setContribution(await api.post(`/moderacao/contribuicoes/${contribuicaoId}/recusar-exclusao`, { justificativa: refusal.trim() }))
      setIsRefusing(false)
      setRefusal('')
    } catch (requestError) {
      setError(mensagem(requestError, 'Não foi possível recusar o pedido.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  const aside = contribution && (
    <>
      <AsideCard title="Situação">
        <p>{SITUACOES[contribution.estado] || 'Estado não informado.'}</p>
      </AsideCard>
      <AsideCard title="Sobre excluir">
        <p>Excluir apaga a contribuição e, se houver, o conteúdo publicado. Não dá para desfazer.</p>
      </AsideCard>
    </>
  )

  return (
    <PageLayout
      onNavigate={onNavigate}
      back={{ href: '/moderacao', label: 'Voltar para a moderação' }}
      eyebrow="Moderação"
      title={contribution?.titulo || 'Contribuição'}
      aside={aside}
      asideLabel="Situação da contribuição"
    >
      {isLoading && <p className="page-status">Carregando contribuição...</p>}
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {notFound && (
        <EmptyState title="Contribuição não encontrada">
          Ela pode ter sido excluída.
          <span className="empty-state__action"><Button variant="outline" onClick={() => onNavigate?.('/moderacao')}>Voltar para a moderação</Button></span>
        </EmptyState>
      )}

      {contribution && (
        <article className="content-detail" aria-label={contribution.titulo}>
          <div className="my-contribution-card__heading">
            <TipoBadge tipo={contribution.tipo} />
            <span className="moderation-card__badges">
              {contribution.exclusao_solicitada_em && <span className="badge badge-exclusao">Exclusão solicitada</span>}
              <StatusBadge status={contribution.estado} />
            </span>
          </div>
          <dl className="content-detail__metadata">
            <div><dt>Disciplina</dt><dd>{rotuloDisciplinaDoConteudo(contribution)}</dd></div>
            <div><dt>Autor</dt><dd>{contribution.autor_nome || 'Não informado'}</dd></div>
            <div><dt>Enviada em</dt><dd>{formatarData(contribution.criado_em)}</dd></div>
            <div><dt>Atualizada em</dt><dd>{formatarData(contribution.atualizado_em)}</dd></div>
            {contribution.origem && <div><dt>Fonte / referência</dt><dd><TextoOuLink texto={contribution.origem} /></dd></div>}
          </dl>

          {contribution.motivo_exclusao && (
            <div className="my-contribution-card__feedback">
              <strong>Pedido de exclusão do autor ({formatarData(contribution.exclusao_solicitada_em, 'medium')})</strong>
              <p>{contribution.motivo_exclusao}</p>
            </div>
          )}
          {contribution.justificativa_moderacao && (
            <div className="my-contribution-card__feedback">
              <strong>Última orientação da moderação</strong>
              <p>{contribution.justificativa_moderacao}</p>
            </div>
          )}

          <div className="content-detail__body">
            <ConteudoCorpo texto={contribution.corpo_ou_url} />
          </div>

          {isRefusing && (
            <form className="contribution-form" onSubmit={recusarPedido} noValidate>
              <label>
                Por que o pedido de exclusão foi recusado? <span aria-hidden="true">*</span>
                <textarea value={refusal} onChange={(event) => setRefusal(event.target.value)} rows="3" maxLength={2000} />
              </label>
              <span className="my-contribution-card__actions">
                <Button variant="outline" onClick={() => setIsRefusing(false)} disabled={isSubmitting}>Cancelar</Button>
                <Button type="submit" disabled={isSubmitting}>Recusar pedido</Button>
              </span>
            </form>
          )}

          <div className="content-page__actions">
            {contribution.estado === 'pendente' && <Button onClick={() => setIsDeciding(true)} disabled={isSubmitting}>Tomar decisão</Button>}
            {contribution.exclusao_solicitada_em && !isRefusing && (
              <Button variant="outline" onClick={() => setIsRefusing(true)} disabled={isSubmitting}>Recusar pedido de exclusão</Button>
            )}
            {contribution.conteudo_id && (
              <Button variant="outline" onClick={() => onNavigate?.(`/conteudos/${contribution.conteudo_id}`)}>Ver publicação</Button>
            )}
            <Button variant="danger" onClick={excluir} disabled={isSubmitting}>Excluir de vez</Button>
          </div>
        </article>
      )}

      <DecisaoModal item={isDeciding ? contribution : null} onClose={() => setIsDeciding(false)} onSubmit={decide} isSubmitting={isSubmitting} />
    </PageLayout>
  )
}

export default ModeracaoContribuicaoPage
