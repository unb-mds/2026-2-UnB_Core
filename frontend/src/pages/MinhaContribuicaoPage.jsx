import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import StatusBadge from '../components/ui/StatusBadge'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import ConteudoCorpo, { TextoOuLink } from '../components/conteudos/ConteudoCorpo'
import EditarContribuicaoForm from '../components/contribuicoes/EditarContribuicaoForm'
import { formatarData, rotuloDisciplinaDoConteudo, rotuloTipo } from '../components/conteudos/formatacao'
import '../components/conteudos/conteudos.css'
import './MinhasContribuicoesPage.css'

function MinhaContribuicaoPage({ contribuicaoId, onNavigate }) {
  const { isAuthenticated } = useAuth()
  const [contribution, setContribution] = useState(null)
  const [error, setError] = useState(null)
  const [notFound, setNotFound] = useState(false)
  const [isLoading, setIsLoading] = useState(isAuthenticated)
  const [isEditing, setIsEditing] = useState(false)
  const [savedMessage, setSavedMessage] = useState('')

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

  const justificativa = contribution?.justificativa_moderacao
  const hasPublishedVersion = Boolean(contribution?.conteudo_id)

  return (
    <div className="my-contributions-shell page-shell">
      <SiteHeader active="conhecimento" onNavigate={onNavigate} />
      <main className="content-page">
        <a className="content-page__back" href="/minhas-contribuicoes" onClick={goToList}>
          ← Voltar para minhas contribuições
        </a>

        {!isAuthenticated && (
          <EmptyState title="Entre para ver esta contribuição">
            Os detalhes das suas contribuições ficam disponíveis somente para você.
            <span className="my-contributions__action"><Button onClick={() => onNavigate?.('/login')}>Entrar</Button></span>
          </EmptyState>
        )}
        {isAuthenticated && isLoading && <p className="content-page__status">Carregando contribuição...</p>}
        {error && <ErrorMessage>{error}</ErrorMessage>}
        {notFound && (
          <EmptyState title="Contribuição não encontrada">
            Ela não existe ou não foi enviada pela sua conta.
            <span className="my-contributions__action"><Button variant="outline" onClick={goToList}>Ver minhas contribuições</Button></span>
          </EmptyState>
        )}

        {contribution && (
          <article className="content-detail" aria-labelledby="contribution-title">
            <div className="my-contribution-card__heading">
              <span className="badge badge-category">{rotuloTipo(contribution.tipo)}</span>
              <StatusBadge status={contribution.estado} />
            </div>
            <div className="content-detail__heading">
              <div>
                <h1 id="contribution-title">{contribution.titulo}</h1>
              </div>
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
                </div>
                {hasPublishedVersion && ['pendente', 'ajustes'].includes(contribution.estado) && (
                  <p className="my-contribution-card__note">
                    A versão aprovada antes continua publicada até a moderação aprovar esta edição.
                  </p>
                )}
              </>
            )}
          </article>
        )}
      </main>
      <SiteFooter />
    </div>
  )
}

export default MinhaContribuicaoPage
