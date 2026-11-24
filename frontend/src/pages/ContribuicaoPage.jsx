import { useEffect, useState } from 'react'
import { api, ApiError } from '../services/api'
import { extrairCursos } from '../services/cursos'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import PageLayout, { AsideCard } from '../components/layout/PageLayout'
import DisciplinaBusca from '../components/conteudos/DisciplinaBusca'
import { IconeTipo } from '../components/conteudos/TipoBadge'
import { classeTipo } from '../components/conteudos/formatacao'
import './ContribuicaoPage.css'

const contentTypes = [
  { value: 'resumo', label: 'Resumo' },
  { value: 'dica', label: 'Dica de estudo' },
  { value: 'dificuldade', label: 'Dificuldade comum' },
  { value: 'implementacao', label: 'Implementação' },
  { value: 'link', label: 'Link útil' },
]

const initialForm = {
  curso_id: '',
  disciplina_id: '',
  tipo: '',
  titulo: '',
  conteudo: '',
  url: '',
}

function ContribuicaoPage({ courses = [], onNavigate }) {
  const { isAuthenticated } = useAuth()
  const [form, setForm] = useState(initialForm)
  const [selectedDiscipline, setSelectedDiscipline] = useState(null)
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [availableCourses, setAvailableCourses] = useState(courses)

  useEffect(() => {
    api.get('/cursos')
      .then((response) => setAvailableCourses(extrairCursos(response)))
      .catch(() => {})
  }, [])

  function updateField(event) {
    const { name, value } = event.target
    setForm((currentForm) => ({ ...currentForm, [name]: value }))
    setError(null)
  }

  function selectDiscipline(discipline) {
    setSelectedDiscipline(discipline)
    setForm((currentForm) => ({ ...currentForm, disciplina_id: discipline?.id || '' }))
    setError(null)
  }

  function selectCourse(event) {
    updateField(event)
    // O curso só filtra a busca: a disciplina continua se o curso também a oferece.
    const courseId = event.target.value
    const courseIds = Array.isArray(selectedDiscipline?.curso_id) ? selectedDiscipline.curso_id.map(Number) : []
    if (courseId && selectedDiscipline && !courseIds.includes(Number(courseId))) {
      selectDiscipline(null)
    }
  }

  function validateForm() {
    const missingFields = []

    if (!form.disciplina_id) missingFields.push('disciplina')
    if (!form.tipo) missingFields.push('tipo de conteúdo')
    if (!form.titulo.trim()) missingFields.push('título')
    if (!form.conteudo.trim() && !form.url.trim()) missingFields.push('conteúdo ou URL')

    return missingFields.length > 0
      ? `Preencha os campos obrigatórios: ${missingFields.join(', ')}.`
      : null
  }

  async function submitContribution(event) {
    event.preventDefault()

    if (!isAuthenticated) {
      setError('Entre na sua conta para enviar uma contribuição.')
      return
    }

    const validationError = validateForm()

    if (validationError) {
      setError(validationError)
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      await api.post('/contribuicoes', {
        disciplina_id: form.disciplina_id,
        tipo: form.tipo,
        titulo: form.titulo.trim(),
        corpo_ou_url: form.conteudo.trim() || form.url.trim(),
        origem: form.url.trim() || undefined,
      })
      setSubmitted(true)
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível enviar sua contribuição.')
    } finally {
      setIsSubmitting(false)
    }
  }

  function goTo(path) {
    return (event) => {
      event?.preventDefault()
      onNavigate?.(path)
    }
  }

  if (submitted) {
    return (
      <PageLayout onNavigate={onNavigate} eyebrow="Colaboração acadêmica" title="Contribuição enviada" width="narrow">
        <EmptyState title="Recebemos a sua contribuição">
          Ela foi registrada como pendente e será analisada pela moderação. Você acompanha o andamento em Minhas contribuições.
          <span className="empty-state__action">
            <Button onClick={goTo('/minhas-contribuicoes')}>Acompanhar em Minhas contribuições</Button>
            <Button variant="outline" onClick={() => { setForm(initialForm); setSelectedDiscipline(null); setSubmitted(false) }}>Enviar outra</Button>
            <Button variant="outline" onClick={goTo('/base-de-conhecimentos')}>Voltar para a base</Button>
          </span>
        </EmptyState>
      </PageLayout>
    )
  }

  const aside = (
    <>
      <AsideCard title="Antes de enviar">
        <ul>
          <li>Cite a fonte quando o material vier de terceiros.</li>
          <li>Seja objetivo: um bom resumo vale mais que um texto longo.</li>
          <li>Se for uma correção de algo publicado, diga o que mudou.</li>
        </ul>
        <a href="/guia-de-contribuicao" onClick={goTo('/guia-de-contribuicao')}>Ler o guia de primeira contribuição</a>
      </AsideCard>
      <AsideCard title="Depois do envio">
        <p>A contribuição fica pendente até a moderação revisar. Você acompanha tudo em Minhas contribuições.</p>
      </AsideCard>
    </>
  )

  return (
    <PageLayout
      onNavigate={onNavigate}
      eyebrow="Colaboração acadêmica"
      title="Envie uma contribuição"
      description="Compartilhe um material útil. A publicação acontece somente após a revisão da equipe."
      aside={aside}
      asideLabel="Dicas para contribuir"
    >
      {!isAuthenticated && (
        <div className="contribution-page__tip">
          <p>Você pode preencher e conhecer o fluxo sem login. Para enviar, <a href="/login" onClick={goTo('/login')}>entre na sua conta</a>.</p>
        </div>
      )}
      <form className="contribution-form" onSubmit={submitContribution} noValidate>
        <div className="contribution-form__grid">
          <label>
            Curso <span className="contribution-form__hint">(opcional, filtra as disciplinas)</span>
            <select name="curso_id" value={form.curso_id} onChange={selectCourse}>
              <option value="">Todos os cursos</option>
              {availableCourses.map((course) => <option key={course.id} value={course.id}>{course.nome || course.name}</option>)}
            </select>
          </label>
          <DisciplinaBusca
            label={<>Disciplina <span aria-hidden="true">*</span></>}
            cursoId={form.curso_id}
            cursos={availableCourses}
            value={selectedDiscipline}
            onChange={selectDiscipline}
          />
        </div>
        <fieldset className="contribution-form__type">
          <legend>Tipo de conteúdo <span aria-hidden="true">*</span></legend>
          <div className="contribution-form__type-options">
            {contentTypes.map((type) => (
              <button
                key={type.value}
                type="button"
                className={`tag-toggle tag-toggle--tipo ${classeTipo(type.value)} ${form.tipo === type.value ? 'tag-toggle--active' : ''}`}
                aria-pressed={form.tipo === type.value}
                onClick={() => updateField({ target: { name: 'tipo', value: type.value } })}
              >
                <IconeTipo tipo={type.value} />
                {type.label}
              </button>
            ))}
          </div>
        </fieldset>
        <label>
          Título <span aria-hidden="true">*</span>
          <input name="titulo" value={form.titulo} onChange={updateField} placeholder="Ex.: Resumo da unidade 1" />
        </label>
        <label>
          Conteúdo
          <textarea name="conteudo" value={form.conteudo} onChange={updateField} rows="8" placeholder="Escreva ou cole o conteúdo aqui..." />
        </label>
        <label>
          Fonte / referência <span className="contribution-form__hint">(opcional, ou preencha a URL do material)</span>
          <input name="url" type="url" value={form.url} onChange={updateField} placeholder="Link ou nome da referência usada" />
        </label>
        {error && <ErrorMessage>{error}</ErrorMessage>}
        <div className="contribution-form__footer">
          <p><strong>Revisão:</strong> novas contribuições começam com estado pendente.</p>
          <Button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Enviando...' : 'Enviar contribuição'}</Button>
        </div>
      </form>
    </PageLayout>
  )
}

export default ContribuicaoPage