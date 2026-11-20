import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import ConteudoDetalhe from '../components/conteudos/ConteudoDetalhe'
import '../components/conteudos/conteudos.css'

function ConteudoPage({ conteudoId, onNavigate }) {
  const [content, setContent] = useState(null)
  const [error, setError] = useState(null)
  const [notFound, setNotFound] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [copyFeedback, setCopyFeedback] = useState('')

  useEffect(() => {
    const controller = new AbortController()

    api
      .get(`/conteudos/${conteudoId}`, { signal: controller.signal })
      .then(setContent)
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return
        if (requestError instanceof ApiError && requestError.status === 404) {
          setNotFound(true)
        } else {
          setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível carregar o conteúdo.')
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false)
      })

    return () => controller.abort()
  }, [conteudoId])

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setCopyFeedback('Link copiado.')
    } catch {
      setCopyFeedback('Não foi possível copiar. Copie o endereço da barra do navegador.')
    }
  }

  function goToKnowledgeBase(event) {
    event?.preventDefault()
    onNavigate?.('/base-de-conhecimentos')
  }

  return (
    <div className="knowledge-shell page-shell">
      <SiteHeader active="conhecimento" onNavigate={onNavigate} />
      <main className="content-page">
        <a className="content-page__back" href="/base-de-conhecimentos" onClick={goToKnowledgeBase}>
          ← Voltar para a base de conhecimento
        </a>

        {isLoading && <p className="content-page__status">Carregando conteúdo...</p>}
        {error && <ErrorMessage>{error}</ErrorMessage>}
        {notFound && (
          <EmptyState title="Conteúdo não encontrado">
            Este conteúdo não existe ou ainda não foi publicado.
            <span className="knowledge-results__action"><Button variant="outline" onClick={goToKnowledgeBase}>Ir para a base de conhecimento</Button></span>
          </EmptyState>
        )}
        {content && (
          <>
            <ConteudoDetalhe content={content} isPage />
            <div className="content-page__actions">
              <Button variant="outline" onClick={copyLink}>Copiar link</Button>
              <Button onClick={() => onNavigate?.('/contribuicao')}>Enviar uma contribuição</Button>
              {copyFeedback && <span className="content-page__feedback" role="status">{copyFeedback}</span>}
            </div>
          </>
        )}
      </main>
      <SiteFooter />
    </div>
  )
}

export default ConteudoPage
