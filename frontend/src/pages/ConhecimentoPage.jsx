import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { extrairCursos } from '../services/cursos'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import ConteudoCard from '../components/conteudos/ConteudoCard'
import ConteudoDetalhe from '../components/conteudos/ConteudoDetalhe'
import DisciplinaBusca from '../components/conteudos/DisciplinaBusca'
import './ConhecimentoPage.css'

const contentTypes = [
  { value: '', label: 'Todos os tipos' },
  { value: 'resumo', label: 'Resumos' },
  { value: 'dica', label: 'Dicas' },
  { value: 'dificuldade', label: 'Dificuldades comuns' },
  { value: 'prova', label: 'Provas' },
  { value: 'implementacao', label: 'Implementações' },
  { value: 'link', label: 'Links úteis' },
]

function ConhecimentoPage({ onContribute = () => {}, onNavigate }) {
  const [courses, setCourses] = useState([])
  const [selectedCourseId, setSelectedCourseId] = useState('')
  const [selectedDiscipline, setSelectedDiscipline] = useState(null)
  const [selectedType, setSelectedType] = useState('')
  const [contents, setContents] = useState([])
  const [selectedContent, setSelectedContent] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const selectedDisciplineId = selectedDiscipline?.id || ''

  useEffect(() => {
    const controller = new AbortController()

    api
      .get('/cursos', { signal: controller.signal })
      .then((response) => setCourses(extrairCursos(response)))
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') {
          setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível carregar os cursos.')
        }
      })

    return () => controller.abort()
  }, [])

  useEffect(() => {
    if (!selectedDisciplineId) {
      return undefined
    }

    const controller = new AbortController()
    const query = selectedType ? `?tipo=${encodeURIComponent(selectedType)}` : ''

    api
      .get(`/disciplinas/${selectedDisciplineId}/conteudos${query}`, { signal: controller.signal })
      .then((response) => setContents(response?.itens || response?.conteudos || []))
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') {
          setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível carregar os conteúdos.')
        }
      })
      .finally(() => setIsLoading(false))

    return () => controller.abort()
  }, [selectedDisciplineId, selectedType])

  function selectCourse(event) {
    const courseId = event.target.value
    setSelectedCourseId(courseId)
    setError(null)

    // O curso é só um filtro: a disciplina escolhida continua se o novo curso também a oferece.
    const courseIds = Array.isArray(selectedDiscipline?.curso_id) ? selectedDiscipline.curso_id.map(Number) : []
    if (courseId && selectedDiscipline && !courseIds.includes(Number(courseId))) {
      selectDiscipline(null)
    }
  }

  function selectDiscipline(discipline) {
    setSelectedDiscipline(discipline)
    setContents([])
    setSelectedContent(null)
    setError(null)
    setIsLoading(Boolean(discipline))
  }

  function selectType(event) {
    setSelectedType(event.target.value)
    setError(null)
    setIsLoading(Boolean(selectedDisciplineId))
  }

  return (
    <div className="knowledge-shell page-shell">
      <SiteHeader active="conhecimento" onNavigate={onNavigate} />
      <main className="knowledge-page">
        <header className="knowledge-page__header">
          <p className="knowledge-page__eyebrow">Base de conhecimento</p>
          <h1>Aprenda com quem já passou por aqui</h1>
          <p>Resumos, dicas e materiais organizados por curso e disciplina.</p>
        </header>

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
          />
          <label>
            Tipo de conteúdo
            <select value={selectedType} onChange={selectType} disabled={!selectedDisciplineId}>
              {contentTypes.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
            </select>
          </label>
        </section>

        <section className="knowledge-results" aria-live="polite">
          {!selectedDisciplineId && (
            <EmptyState title="Escolha uma disciplina para começar">
              Busque a disciplina pelo nome ou código. Se quiser, filtre antes pelo curso.
            </EmptyState>
          )}
          {isLoading && <p className="knowledge-results__status">Carregando conteúdos...</p>}
          {error && <ErrorMessage>{error}</ErrorMessage>}
          {!isLoading && !error && selectedDisciplineId && contents.length === 0 && (
            <EmptyState title="Nenhum conteúdo encontrado">
              Ainda não há conteúdo para este filtro. Você pode contribuir com a comunidade.
              <span className="knowledge-results__action"><Button variant="accent" onClick={onContribute}>Quero contribuir</Button></span>
            </EmptyState>
          )}
          {!isLoading && !error && contents.length > 0 && (
            <div className="knowledge-grid">
              {contents.map((content) => <ConteudoCard key={content.id} content={content} onOpen={setSelectedContent} />)}
            </div>
          )}
          <ConteudoDetalhe content={selectedContent} onClose={() => setSelectedContent(null)} />
        </section>
      </main>
      <SiteFooter />
    </div>
  )
}

export default ConhecimentoPage