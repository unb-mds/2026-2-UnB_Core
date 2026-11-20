import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { extrairCursos } from '../services/cursos'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import PageLayout from '../components/layout/PageLayout'
import ConteudoCard from '../components/conteudos/ConteudoCard'
import DisciplinaBusca from '../components/conteudos/DisciplinaBusca'
import './ConhecimentoPage.css'

const POR_PAGINA = 12

const contentTypes = [
  { value: '', label: 'Todos os tipos' },
  { value: 'resumo', label: 'Resumos' },
  { value: 'dica', label: 'Dicas' },
  { value: 'dificuldade', label: 'Dificuldades comuns' },
  { value: 'prova', label: 'Provas' },
  { value: 'implementacao', label: 'Implementações' },
  { value: 'link', label: 'Links úteis' },
]

const ordens = [
  { value: 'recentes', label: 'Mais recentes' },
  { value: 'antigos', label: 'Mais antigos' },
  { value: 'titulo', label: 'Título (A–Z)' },
]

function montarConsulta({ cursoId, disciplinaId, tipo, ordem, pagina }) {
  const params = new URLSearchParams({ limite: String(POR_PAGINA), pagina: String(pagina), ordem })
  if (cursoId) params.set('curso_id', cursoId)
  if (disciplinaId) params.set('disciplina_id', disciplinaId)
  if (tipo) params.set('tipo', tipo)
  return `/conteudos?${params}`
}

function mensagemDeErro(requestError, padrao) {
  return requestError instanceof ApiError ? requestError.message : padrao
}

function ConhecimentoPage({ onContribute = () => {}, onNavigate }) {
  const [courses, setCourses] = useState([])
  const [coursesError, setCoursesError] = useState(null)
  const [selectedCourseId, setSelectedCourseId] = useState('')
  // A home pode abrir esta página com uma disciplina já escolhida (history.state).
  const [selectedDiscipline, setSelectedDiscipline] = useState(() => window.history.state?.disciplina || null)
  const [selectedType, setSelectedType] = useState('')
  const [order, setOrder] = useState('recentes')
  // `chave` identifica os filtros da busca que gerou o resultado. Enquanto ela for
  // diferente dos filtros atuais, a página está carregando.
  const [result, setResult] = useState({ chave: null, itens: [], total: 0, pagina: 1, erro: null })
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const [loadMoreError, setLoadMoreError] = useState(null)

  const selectedDisciplineId = selectedDiscipline?.id || ''
  const chave = [selectedCourseId, selectedDisciplineId, selectedType, order].join('|')
  const isLoading = result.chave !== chave
  const hasFilters = Boolean(selectedCourseId || selectedDisciplineId || selectedType)

  useEffect(() => {
    const controller = new AbortController()

    api
      .get('/cursos', { signal: controller.signal })
      .then((response) => setCourses(extrairCursos(response)))
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') setCoursesError(mensagemDeErro(requestError, 'Não foi possível carregar os cursos.'))
      })

    return () => controller.abort()
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    const filtros = { cursoId: selectedCourseId, disciplinaId: selectedDisciplineId, tipo: selectedType, ordem: order }

    api
      .get(montarConsulta({ ...filtros, pagina: 1 }), { signal: controller.signal })
      .then((response) => {
        const itens = response?.itens || []
        setResult({ chave, itens, total: response?.total ?? itens.length, pagina: 1, erro: null })
      })
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return
        setResult({ chave, itens: [], total: 0, pagina: 1, erro: mensagemDeErro(requestError, 'Não foi possível carregar os conteúdos.') })
      })

    return () => controller.abort()
  }, [chave, selectedCourseId, selectedDisciplineId, selectedType, order])

  async function loadMore() {
    const proximaPagina = result.pagina + 1
    const chaveDaBusca = chave
    setIsLoadingMore(true)
    setLoadMoreError(null)

    try {
      const response = await api.get(montarConsulta({
        cursoId: selectedCourseId,
        disciplinaId: selectedDisciplineId,
        tipo: selectedType,
        ordem: order,
        pagina: proximaPagina,
      }))
      setResult((atual) => {
        // Se os filtros mudaram enquanto carregava, descarta esta página.
        if (atual.chave !== chaveDaBusca) return atual
        const ids = new Set(atual.itens.map((item) => item.id))
        const novos = (response?.itens || []).filter((item) => !ids.has(item.id))
        return { ...atual, itens: [...atual.itens, ...novos], total: response?.total ?? atual.total, pagina: proximaPagina }
      })
    } catch (requestError) {
      setLoadMoreError(mensagemDeErro(requestError, 'Não foi possível carregar mais conteúdos.'))
    } finally {
      setIsLoadingMore(false)
    }
  }

  function selectDiscipline(discipline) {
    setSelectedDiscipline(discipline)
    setLoadMoreError(null)
    // Guarda a escolha no histórico para mantê-la ao recarregar ou voltar para a página.
    window.history.replaceState({ ...window.history.state, disciplina: discipline }, '')
  }

  function selectCourse(event) {
    const courseId = event.target.value
    setSelectedCourseId(courseId)
    setLoadMoreError(null)

    // O curso é só um filtro: a disciplina escolhida continua se o novo curso também a oferece.
    const courseIds = Array.isArray(selectedDiscipline?.curso_id) ? selectedDiscipline.curso_id.map(Number) : []
    if (courseId && selectedDiscipline && !courseIds.includes(Number(courseId))) {
      selectDiscipline(null)
    }
  }

  function clearFilters() {
    setSelectedCourseId('')
    setSelectedType('')
    selectDiscipline(null)
  }

  function openContent(content) {
    onNavigate?.(`/conteudos/${content.id}`)
  }

  let contagem = ''
  if (isLoading) {
    contagem = 'Carregando conteúdos...'
  } else if (!result.erro && result.total > 0) {
    const nome = result.total === 1 ? 'conteúdo' : 'conteúdos'
    contagem = result.itens.length < result.total
      ? `Mostrando ${result.itens.length} de ${result.total} ${nome}`
      : `${result.total} ${nome}`
  }

  const filtros = (
        <section className="knowledge-filters" aria-label="Filtros da base de conhecimento">
          <label>
            Curso
            <select value={selectedCourseId} onChange={selectCourse}>
              <option value="">Todos os cursos</option>
              {courses.map((course) => <option key={course.id} value={course.id}>{course.nome || course.name}</option>)}
            </select>
          </label>
          <DisciplinaBusca
            cursoId={selectedCourseId}
            cursos={courses}
            value={selectedDiscipline}
            onChange={selectDiscipline}
            placeholder="Todas — busque pelo nome ou código"
          />
          <label>
            Tipo de conteúdo
            <select value={selectedType} onChange={(event) => { setSelectedType(event.target.value); setLoadMoreError(null) }}>
              {contentTypes.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
            </select>
          </label>
          <label>
            Ordenar por
            <select value={order} onChange={(event) => { setOrder(event.target.value); setLoadMoreError(null) }}>
              {ordens.map((ordem) => <option key={ordem.value} value={ordem.value}>{ordem.label}</option>)}
            </select>
          </label>
        </section>
  )

  return (
    <PageLayout
      onNavigate={onNavigate}
      eyebrow="Base de conhecimento"
      title="Aprenda com quem já passou por aqui"
      description="Resumos, dicas e materiais da comunidade. Filtre por curso, disciplina ou tipo, ou veja tudo."
      headerContent={filtros}
    >
      {coursesError && <ErrorMessage>{coursesError}</ErrorMessage>}

      <div className="knowledge-results__toolbar">
        <p className="knowledge-results__count" role="status">{contagem}</p>
        {hasFilters && <Button variant="outline" onClick={clearFilters}>Limpar filtros</Button>}
      </div>

      <section className="knowledge-results" aria-label="Conteúdos">
        {!isLoading && result.erro && <ErrorMessage>{result.erro}</ErrorMessage>}
        {!isLoading && !result.erro && result.itens.length === 0 && (
          hasFilters ? (
            <EmptyState title="Nenhum conteúdo para estes filtros">
              Tente outra combinação de filtros ou compartilhe um material sobre o assunto.
              <span className="empty-state__action">
                <Button variant="outline" onClick={clearFilters}>Limpar filtros</Button>{' '}
                <Button onClick={onContribute}>Quero contribuir</Button>
              </span>
            </EmptyState>
          ) : (
            <EmptyState title="Ainda não há conteúdos publicados">
              Seja a primeira pessoa a compartilhar um material com a comunidade.
              <span className="empty-state__action"><Button onClick={onContribute}>Quero contribuir</Button></span>
            </EmptyState>
          )
        )}
        {result.itens.length > 0 && (
          // Enquanto novos filtros carregam, a lista anterior fica esmaecida em vez de sumir.
          <div className="cards-grid" aria-busy={isLoading}>
            {result.itens.map((content) => (
              <ConteudoCard key={content.id} content={content} showDiscipline={!selectedDisciplineId} onOpen={openContent} />
            ))}
          </div>
        )}
        {!isLoading && result.itens.length < result.total && (
          <div className="knowledge-results__more">
            <Button variant="outline" onClick={loadMore} disabled={isLoadingMore}>
              {isLoadingMore ? 'Carregando...' : 'Carregar mais'}
            </Button>
          </div>
        )}
        {loadMoreError && <ErrorMessage>{loadMoreError}</ErrorMessage>}
      </section>
    </PageLayout>
  )
}

export default ConhecimentoPage
