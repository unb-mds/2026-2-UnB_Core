import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import StatusBadge from '../components/ui/StatusBadge'
import Button from '../components/ui/Button'
import PageLayout, { AsideCard } from '../components/layout/PageLayout'
import ConteudoCorpo, { TextoOuLink } from '../components/conteudos/ConteudoCorpo'
import EditarContribuicaoForm from '../components/contribuicoes/EditarContribuicaoForm'
import { formatarData, rotuloDisciplinaDoConteudo } from '../components/conteudos/formatacao'
import TipoBadge from '../components/conteudos/TipoBadge'
import '../components/conteudos/conteudos.css'
import './ContribuicaoPage.css'
import './MinhasContribuicoesPage.css'

// O que cada estado significa para quem enviou, na coluna lateral.
const SITUACOES = {
  pendente: 'Aguardando a revisão da moderação. Enquanto isso, você ainda pode editar.',
  ajustes: 'A moderação pediu ajustes. Leia a orientação, edite a contribuição e ela volta para revisão.',
  aprovada: 'Aprovada e publicada na base de conhecimento.',
  rejeitada: 'Não foi publicada. Veja a orientação da moderação para entender o motivo.',
  arquivada: 'Arquivada pela moderação e fora da base de conhecimento.',
}

function MinhaContribuicaoPage({ contribuicaoId, onNavigate }) {
  const { isAuthenticated } = useAuth()
  const [contribution, setContribution] = useState(null)
  const [error, setError] = useState(null)
  const [notFound, setNotFound] = useState(false)
  const [isLoading, setIsLoading] = useState(isAuthenticated)
  const [isEditing, setIsEditing] = useState(false)
  const [savedMessage, setSavedMessage] = useState('')
  const [isRequestingDeletion, setIsRequestingDeletion] = useState(false)
  const [deleteReason, setDeleteReason] = useState('')
  const [isWorking, setIsWorking] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) return undefined

    const controller = new AbortController()
    api
      .get(`/contribuicoes/minhas/${contribuicaoId}`, { signal: controller.signal })
      .then(setContribution)
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return
        // 404: não existe. 422: pertence a outra pessoa. Nos dois casos, não há o que mostrar.
        if (requestError instanceof ApiError && [404, 422].includes(requestError.status)) {
          setNotFound(true)
        } else {
          setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível carregar a contribuição.')
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false)
      })

    return () => controller.abort()
  }, [isAuthenticated, contribuicaoId])

  function goToList(event) {
    event?.preventDefault()
    onNavigate?.('/minhas-contribuicoes')
  }

  async function excluir() {
    const confirmado = window.confirm('Excluir esta contribuição? Não dá para desfazer.')
    if (!confirmado) return
    setIsWorking(true)
    setError(null)
    try {
      await api.delete(`/contribuicoes/minhas/${contribuicaoId}`)
      onNavigate?.('/minhas-contribuicoes')
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível excluir a contribuição.')
      setIsWorking(false)
    }
  }

  async function pedirExclusao(event) {
    event.preventDefault()
    if (deleteReason.trim().length < 5) {
      setError('Conte o motivo do pedido (pelo menos 5 caracteres).')
      return
    }
    setIsWorking(true)
    setError(null)
    try {
      setContribution(await api.post(`/contribuicoes/minhas/${contribuicaoId}/pedido-exclusao`, { motivo: deleteReason.trim() }))
      setIsRequestingDeletion(false)
      setDeleteReason('')
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível enviar o pedido.')
    } finally {
      setIsWorking(false)
    }
  }

  async function cancelarPedido() {
    setIsWorking(true)
    setError(null)
    try {
      setContribution(await api.delete(`/contribuicoes/minhas/${contribuicaoId}/pedido-exclusao`))
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível cancelar o pedido.')
    } finally {
      setIsWorking(false)
    }
  }

  const justificativa = contribution?.justificativa_moderacao
  const hasPublishedVersion = Boolean(contribution?.conteudo_id)
  const exclusaoSolicitada = Boolean(contribution?.exclusao_solicitada_em)

  const situacao = SITUACOES[contribution?.estado]

  const aside = contribution && (
    <>
      <AsideCard title="Situação">
        <p>{situacao || 'Estado da contribuição não informado.'}</p>
      </AsideCard>
      <AsideCard title="Como funciona a revisão">
        <ol>
          <li>Você envia ou edita a contribuição.</li>
          <li>A moderação aprova, pede ajustes ou rejeita.</li>
          <li>Depois de aprovada, ela aparece na base de conhecimento.</li>
        </ol>
        <a href="/guia-de-contribuicao" onClick={(event) => { event.preventDefault(); onNavigate?.('/guia-de-contribuicao') }}>
          Ler o guia de contribuição
        </a>
      </AsideCard>
    </>
  )

  return (
    <PageLayout
      onNavigate={onNavigate}
      back={{ href: '/minhas-contribuicoes', label: 'Voltar para minhas contribuições' }}
      eyebrow="Minha contribuição"
      title={contribution?.titulo || 'Minha contribuição'}
      aside={aside}
      asideLabel="Situação da contribuição"
    >
      {!isAuthenticated && (
        <EmptyState title="Entre para ver esta contribuição">
          Os detalhes das suas contribuições ficam disponíveis somente para você.
          <span className="empty-state__action"><Button onClick={() => onNavigate?.('/login')}>Entrar</Button></span>
        </EmptyState>
      )}
      {isAuthenticated && isLoading && <p className="page-status">Carregando contribuição...</p>}
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {notFound && (
        <EmptyState title="Contribuição não encontrada">
          Ela não existe ou não foi enviada pela sua conta.
          <span className="empty-state__action"><Button variant="outline" onClick={goToList}>Ver minhas contribuições</Button></span>
        </EmptyState>
      )}

      {contribution && (
        <article className="content-detail" aria-label={contribution.titulo}>
          <div className="my-contribution-card__heading">
            <TipoBadge tipo={contribution.tipo} />
            <StatusBadge status={contribution.estado} />
          </div>
          <dl className="content-detail__metadata">
            <div>
              <dt>Disciplina</dt>
              <dd>{rotuloDisciplinaDoConteudo(contribution)}</dd>
            </div>
            <div>
              <dt>Enviada em</dt>
              <dd>{formatarData(contribution.criado_em)}</dd>
            </div>
            <div>
              <dt>Atualizada em</dt>
              <dd>{formatarData(contribution.atualizado_em)}</dd>
            </div>
            {contribution.origem && (
              <div>
                <dt>Fonte / referência</dt>
                <dd><TextoOuLink texto={contribution.origem} /></dd>
              </div>
            )}
          </dl>

          {justificativa && (
            <div className="my-contribution-card__feedback">
              <strong>Orientação da moderação</strong>
              <p>{justificativa}</p>
            </div>
          )}
          {savedMessage && <p className="content-page__feedback" role="status">{savedMessage}</p>}
          {exclusaoSolicitada && (
            <div className="my-contribution-card__feedback">
              <strong>Pedido de exclusão enviado em {formatarData(contribution.exclusao_solicitada_em, 'medium')}</strong>
              <p>Motivo: {contribution.motivo_exclusao}</p>
              <p>A moderação vai analisar. Até lá, o conteúdo continua publicado.</p>
            </div>
          )}

          {isEditing ? (
            <EditarContribuicaoForm
              contribution={contribution}
              onCancel={() => setIsEditing(false)}
              onSaved={(updated) => {
                setContribution(updated)
                setIsEditing(false)
                setSavedMessage('Alterações salvas. A contribuição voltou para revisão.')
              }}
            />
          ) : (
            <>
              <div className="content-detail__body">
                <ConteudoCorpo texto={contribution.corpo_ou_url} />
              </div>
              <div className="content-page__actions">
                <Button variant="outline" onClick={() => { setSavedMessage(''); setIsEditing(true) }}>Editar</Button>
                {hasPublishedVersion && (
                  <Button variant="outline" onClick={() => onNavigate?.(`/conteudos/${contribution.conteudo_id}`)}>
                    {contribution.estado === 'aprovada' ? 'Ver publicação' : 'Ver versão publicada'}
                  </Button>
                )}
                {/* Não publicada: exclui na hora. Publicada: pede à moderação. */}
                {!hasPublishedVersion && (
                  <Button variant="danger" onClick={excluir} disabled={isWorking}>Excluir contribuição</Button>
                )}
                {hasPublishedVersion && !exclusaoSolicitada && !isRequestingDeletion && (
                  <Button variant="danger" onClick={() => setIsRequestingDeletion(true)} disabled={isWorking}>Pedir exclusão</Button>
                )}
                {exclusaoSolicitada && (
                  <Button variant="outline" onClick={cancelarPedido} disabled={isWorking}>Cancelar pedido de exclusão</Button>
                )}
              </div>
              {isRequestingDeletion && (
                <form className="contribution-form" onSubmit={pedirExclusao} noValidate>
                  <label>
                    Por que você quer excluir esta contribuição? <span aria-hidden="true">*</span>
                    <textarea value={deleteReason} onChange={(event) => setDeleteReason(event.target.value)} rows="3" maxLength={500} />
                  </label>
                  <p className="my-contribution-card__note">Como ela já está publicada, a moderação analisa o pedido antes de excluir.</p>
                  <span className="my-contribution-card__actions">
                    <Button variant="outline" onClick={() => setIsRequestingDeletion(false)} disabled={isWorking}>Cancelar</Button>
                    <Button type="submit" disabled={isWorking}>Enviar pedido</Button>
                  </span>
                </form>
              )}
              {hasPublishedVersion && ['pendente', 'ajustes'].includes(contribution.estado) && (
                <p className="my-contribution-card__note">
                  A versão aprovada antes continua publicada até a moderação aprovar esta edição.
                </p>
              )}
            </>
          )}
        </article>
      )}
    </PageLayout>
  )
}

export default MinhaContribuicaoPage
