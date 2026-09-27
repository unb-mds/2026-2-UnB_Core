import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import ConteudoCard from '../components/conteudos/ConteudoCard'
import ConteudoDetalhe from '../components/conteudos/ConteudoDetalhe'
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

function ConhecimentoPage({ courses = [{ id: '1', nome: 'Engenharia de Software' }], onContribute = () => {}, onNavigate }) {
  const [selectedCourseId, setSelectedCourseId] = useState('')
  const [selectedDisciplineId, setSelectedDisciplineId] = useState('')
  const [selectedType, setSelectedType] = useState('')
  const [disciplines, setDisciplines] = useState([])
  const [contents, setContents] = useState([])
  const [selectedContent, setSelectedContent] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!selectedCourseId) {
      return undefined
    }

    const controller = new AbortController()

    api
      .get(`/cursos/${selectedCourseId}/disciplinas`, { signal: controller.signal })
      .then((response) => setDisciplines(response?.itens || response?.disciplinas || []))
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') {
          setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível carregar as disciplinas.')
        }
      })
      .finally(() => setIsLoading(false))

    return () => controller.abort()
  }, [selectedCourseId])

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
    setSelectedCourseId(event.target.value)
    setSelectedDisciplineId('')
    setDisciplines([])
    setContents([])
    setSelectedContent(null)
    setError(null)
    setIsLoading(Boolean(event.target.value))
  }

  function selectDiscipline(event) {
    setSelectedDisciplineId(event.target.value)
    setContents([])
    setSelectedContent(null)
    setError(null)
    setSelectedContent(null)
    setIsLoading(Boolean(event.target.value))
  }

  function selectType(event) {
    setSelectedType(event.target.value)
    setError(null)
    setIsLoading(Boolean(selectedDisciplineId))
  }

  return (
    <div className="knowledge-shell">
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
              <option value="">Selecione um curso</option>
              {courses.map((course) => <option key={course.id} value={course.id}>{course.nome || course.name}</option>)}
            </select>
          </label>
          <label>
            Disciplina
            <select value={selectedDisciplineId} onChange={selectDiscipline} disabled={!selectedCourseId}>
              <option value="">Selecione uma disciplina</option>
              {disciplines.map((discipline) => <option key={discipline.id} value={discipline.id}>{discipline.nome || discipline.name}</option>)}
            </select>
          </label>
          <label>
            Tipo de conteúdo
            <select value={selectedType} onChange={selectType} disabled={!selectedDisciplineId}>
              {contentTypes.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
            </select>
          </label>
        </section>

        <section className="knowledge-results" aria-live="polite">
          {!selectedCourseId && (
            <EmptyState title="Escolha um curso para começar">
              Selecione um curso e uma disciplina para consultar os conteúdos publicados.
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