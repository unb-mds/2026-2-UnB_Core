import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import StatusBadge from '../components/ui/StatusBadge'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import PublicacaoFonte from '../components/publicacoes/PublicacaoFonte'
import PublicacaoStatus from '../components/publicacoes/PublicacaoStatus'
import PublicacaoDatas from '../components/publicacoes/PublicacaoDatas'
import PublicacaoLinkOficial from '../components/publicacoes/PublicacaoLinkOficial'
import './PublicacaoDetalhePage.css'

function formatRelativeTime(value) {
  if (!value) return null
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return null
  const diffDays = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24))
  if (diffDays <= 0) return 'Publicado hoje'
  if (diffDays === 1) return 'Publicado há 1 dia'
  return `Publicado há ${diffDays} dias`
}

function PublicacaoDetalhePage({ publicationId, publication: initialPublication, onBack = () => {}, onNavigate }) {
  const [publication, setPublication] = useState(initialPublication || null)
  const [isLoading, setIsLoading] = useState(!initialPublication)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (initialPublication || !publicationId) {
      return undefined
    }

    const controller = new AbortController()

    api
      .get(`/publicacoes/${publicationId}`, { signal: controller.signal })
      .then((response) => setPublication(response))
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') {
          setError(
            requestError instanceof ApiError
              ? requestError.message
              : 'Não foi possível carregar os detalhes da publicação.',
          )
        }
      })
      .finally(() => setIsLoading(false))

    return () => controller.abort()
  }, [initialPublication, publicationId])

  return (
    <div className="publication-detail-shell page-shell">
      <SiteHeader active="editais" onNavigate={onNavigate} />
      <main className="publication-detail-page">
        <Button variant="outline" onClick={onBack}>← Voltar para editais</Button>

        {isLoading && <p className="publication-detail__status">Carregando publicação...</p>}
        {error && <ErrorMessage>{error}</ErrorMessage>}
        {!isLoading && !error && !publication && (
          <EmptyState title="Publicação não encontrada">
            Verifique o endereço ou volte para a lista de editais.
          </EmptyState>
        )}
        {!isLoading && !error && publication && (
          <article className="publication-detail-card">
            <header className="publication-detail__header">
              <div className="publication-detail__tags">
                <span className="badge badge-category">{publication.categoria || 'Publicação'}</span>
                <StatusBadge status={publication.estado} />
              </div>
              <h1>{publication.titulo}</h1>
              <p className="publication-detail__unit">
                {formatRelativeTime(publication.data_publicacao) || 'Data de publicação não informada'}
                {publication.unidade_responsavel ? ` · Fonte: ${publication.unidade_responsavel}` : ''}
              </p>
            </header>

            <div className="publication-detail__content">
              <section className="publication-detail__summary" aria-labelledby="publication-summary-title">
                <h2 id="publication-summary-title">Resumo</h2>
                <p>{publication.resumo || 'Esta publicação não possui resumo informado.'}</p>
              </section>
              <div className="publication-detail__grid">
                <PublicacaoFonte publicacao={publication} />
                <PublicacaoStatus publicacao={publication} />
                <PublicacaoDatas publicacao={publication} />
              </div>
              <div className="publication-detail__actions">
                {publication.url_oficial && (
                  <Button variant="primary" onClick={() => window.open(publication.url_oficial, '_blank', 'noopener,noreferrer')}>
                    Acessar fonte oficial
                  </Button>
                )}
                <Button
                  variant="outline"
                  onClick={() => window.open(`mailto:unb.core@gmail.com?subject=${encodeURIComponent(`Problema na publicação: ${publication.titulo}`)}`)}
                >
                  Relatar problema
                </Button>
              </div>
              <PublicacaoLinkOficial url={publication.url_oficial} />
            </div>
          </article>
        )}
      </main>
      <SiteFooter />
    </div>
  )
}

export default PublicacaoDetalhePage