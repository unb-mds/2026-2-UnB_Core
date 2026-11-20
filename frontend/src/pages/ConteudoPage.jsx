import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import PageLayout, { AsideCard } from '../components/layout/PageLayout'
import ConteudoDetalhe from '../components/conteudos/ConteudoDetalhe'
import { rotuloTipo } from '../components/conteudos/formatacao'
import '../components/conteudos/conteudos.css'

const QUANTIDADE_RELACIONADOS = 5

function ConteudoPage({ conteudoId, onNavigate }) {
  const [content, setContent] = useState(null)
  const [related, setRelated] = useState(null)
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

  // Outros conteúdos da mesma disciplina, para a coluna lateral.
  const disciplinaId = content?.disciplina_id
  useEffect(() => {
    if (!disciplinaId) return undefined

    const controller = new AbortController()
    api
      .get(`/conteudos?disciplina_id=${disciplinaId}&limite=${QUANTIDADE_RELACIONADOS + 1}&ordem=recentes`, { signal: controller.signal })
      .then((response) => {
        const itens = Array.isArray(response?.itens) ? response.itens : []
        setRelated(itens.filter((item) => String(item.id) !== String(conteudoId)).slice(0, QUANTIDADE_RELACIONADOS))
      })
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') setRelated([])
      })

    return () => controller.abort()
  }, [disciplinaId, conteudoId])

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setCopyFeedback('Link copiado.')
    } catch {
      setCopyFeedback('Não foi possível copiar. Copie o endereço da barra do navegador.')
    }
  }

  function goTo(path, state) {
    return (event) => {
      event?.preventDefault()
      onNavigate?.(path, state)
    }
  }

  const disciplinaDoConteudo = content && {
    id: content.disciplina_id,
    codigo: content.disciplina_codigo,
    nome: content.disciplina_nome,
  }

  const aside = content && (
    <>
      <AsideCard title="Disciplina">
        <p className="content-aside__code">{content.disciplina_codigo || 'Código não informado'}</p>
        <p className="content-aside__name">{content.disciplina_nome || 'Disciplina não informada'}</p>
        <Button variant="outline" onClick={goTo('/base-de-conhecimentos', { disciplina: disciplinaDoConteudo })}>
          Ver todos desta disciplina
        </Button>
      </AsideCard>
      <AsideCard title="Mais desta disciplina">
        {related === null && <p>Carregando...</p>}
        {related?.length === 0 && <p>Ainda não há outros conteúdos desta disciplina.</p>}
        {related?.length > 0 && (
          <ul className="content-aside__list">
            {related.map((item) => (
              <li key={item.id}>
                <a href={`/conteudos/${item.id}`} onClick={goTo(`/conteudos/${item.id}`)}>{item.titulo}</a>
                <span>{rotuloTipo(item.tipo)}</span>
              </li>
            ))}
          </ul>
        )}
      </AsideCard>
    </>
  )

  return (
    <PageLayout
      onNavigate={onNavigate}
      back={{ href: '/base-de-conhecimentos', label: 'Voltar para a base de conhecimento' }}
      eyebrow="Base de conhecimento"
      title={content?.titulo || 'Conteúdo'}
      actions={content && (
        <>
          <Button variant="outline" onClick={copyLink}>Copiar link</Button>
          <Button onClick={() => onNavigate?.('/contribuicao')}>Enviar uma contribuição</Button>
        </>
      )}
      aside={aside}
      asideLabel="Sobre a disciplina"
    >
      {copyFeedback && <p className="content-page__feedback" role="status">{copyFeedback}</p>}
      {isLoading && <p className="page-status">Carregando conteúdo...</p>}
      {error && <ErrorMessage>{error}</ErrorMessage>}
      {notFound && (
        <EmptyState title="Conteúdo não encontrado">
          Este conteúdo não existe ou ainda não foi publicado.
          <span className="empty-state__action"><Button variant="outline" onClick={goTo('/base-de-conhecimentos')}>Ir para a base de conhecimento</Button></span>
        </EmptyState>
      )}
      {content && <ConteudoDetalhe content={content} isPage />}
    </PageLayout>
  )
}

export default ConteudoPage
