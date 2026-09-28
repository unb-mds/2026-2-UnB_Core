import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import SearchInput from '../components/ui/SearchInput'
import StatusBadge from '../components/ui/StatusBadge'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import './PublicacoesPage.css'

const initialFilters = {
  termo: '',
  categoria: '',
  unidade: '',
  estado: '',
  prazo: '',
}

function formatDate(value) {
  if (!value) {
    return null
  }

  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium' }).format(date)
}

function getPublicationWarning(publicacao) {
  if (!publicacao.ultima_verificacao) {
    return 'Esta publicação ainda não foi verificada. Consulte a fonte oficial.'
  }

  if (!publicacao.prazo) {
    return 'Esta publicação não informa prazo. Consulte a fonte oficial para confirmar as datas.'
  }

  return null
}

function PublicationCard({ publicacao, onSelect }) {
  const warning = getPublicationWarning(publicacao)

  return (
    <article className={`publication-card publication-card--${publicacao.estado || 'unknown'}`}>
      <div className="publication-card__heading">
        <span className="badge badge-category">{publicacao.categoria || 'Publicação'}</span>
        <StatusBadge status={publicacao.estado} />
      </div>
      <h2>{publicacao.titulo}</h2>
      <p>{publicacao.resumo}</p>
      <dl className="publication-card__metadata">
        <div>
          <dt>Unidade responsável</dt>
          <dd>{publicacao.unidade_responsavel}</dd>
        </div>
        <div>
          <dt>Verificado em</dt>
          <dd>{formatDate(publicacao.ultima_verificacao) || 'Não informado'}</dd>
        </div>
        <div>
          <dt>Prazo</dt>
          <dd>{formatDate(publicacao.prazo) || 'Não informado'}</dd>
        </div>
      </dl>
      {warning && <p className="publication-card__warning">{warning}</p>}
      <Button onClick={() => onSelect(publicacao)}>
        Ver detalhes
      </Button>
    </article>
  )
}

function PublicacoesPage({ onSelectPublication = () => {}, onNavigate }) {
  const [filters, setFilters] = useState(initialFilters)
  const [publicacoes, setPublicacoes] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const controller = new AbortController()
    const searchParams = new URLSearchParams()

    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        searchParams.set(key, value)
      }
    })

    api
      .get(`/publicacoes${searchParams.toString() ? `?${searchParams}` : ''}`, {
        signal: controller.signal,
      })
      .then((response) => setPublicacoes(response?.itens || []))
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') {
          setError(
            requestError instanceof ApiError
              ? requestError.message
              : 'Não foi possível carregar as publicações. Tente novamente.',
          )
        }
      })
      .finally(() => setIsLoading(false))

    return () => controller.abort()
  }, [filters])

  function updateFilter(event) {
    const { name, value } = event.target
    setIsLoading(true)
    setError(null)
    setFilters((currentFilters) => ({ ...currentFilters, [name]: value }))
  }

  function clearFilters() {
    setIsLoading(true)
    setError(null)
    setFilters(initialFilters)
  }

  return (
    <div className="publications-shell">
      <SiteHeader active="editais" onNavigate={onNavigate} />

      <main className="publications-page">
        <aside className="filter-sidebar" aria-label="Filtros de publicações">
          <div className="filter-sidebar__heading">
            <h2>Filtrar por</h2>
            <button type="button" onClick={clearFilters}>Limpar</button>
          </div>
          <fieldset>
            <legend>Categoria</legend>
            {['edital', 'aviso', 'comunicado', 'oportunidade'].map((categoria) => (
              <label key={categoria} className="filter-check">
                <input type="checkbox" checked={filters.categoria === categoria} onChange={() => updateFilter({ target: { name: 'categoria', value: filters.categoria === categoria ? '' : categoria } })} />
                <span>{categoria}</span>
              </label>
            ))}
          </fieldset>
          <fieldset>
            <legend>Estado</legend>
            {['ativa', 'encerrada', 'arquivada'].map((estado) => (
              <label key={estado} className="filter-check">
                <input type="checkbox" checked={filters.estado === estado} onChange={() => updateFilter({ target: { name: 'estado', value: filters.estado === estado ? '' : estado } })} />
                <span>{estado === 'ativa' ? 'Ativo' : estado === 'encerrada' ? 'Encerrado' : 'Arquivado'}</span>
              </label>
            ))}
          </fieldset>
          <label className="filter-sidebar__field">
            Unidade responsável
            <input name="unidade" value={filters.unidade} onChange={updateFilter} placeholder="Ex.: DEG" />
          </label>
          <label className="filter-sidebar__field">
            Curso relacionado
            <input name="curso_id" value={filters.curso_id || ''} onChange={updateFilter} placeholder="Código do curso" />
          </label>
        </aside>

        <section className="publications-content" aria-labelledby="publications-title">
          <header className="publications-page__header">
            <p className="publications-page__eyebrow">Publicações oficiais</p>
            <h1 id="publications-title">Central de editais</h1>
            <p>Encontre editais e avisos da UnB em um só lugar.</p>
          </header>
          <SearchInput value={filters.termo} onChange={updateFilter} placeholder="Buscar por título, palavra-chave ou unidade" />

          <section aria-live="polite" className="publications-results">
            {isLoading && <p className="publications-results__status">Carregando publicações...</p>}
            {error && <ErrorMessage>{error}</ErrorMessage>}
            {!isLoading && !error && publicacoes.length === 0 && (
              <EmptyState title="Nenhuma publicação encontrada">Tente ajustar os filtros ou consulte novamente mais tarde.</EmptyState>
            )}
            {!isLoading && !error && publicacoes.length > 0 && (
              <div className="publications-grid">
                {publicacoes.map((publicacao) => (
                  <PublicationCard key={publicacao.id} publicacao={publicacao} onSelect={onSelectPublication} />
                ))}
              </div>
            )}
          </section>
        </section>
      </main>

      <SiteFooter />
    </div>
  )
}

export default PublicacoesPage