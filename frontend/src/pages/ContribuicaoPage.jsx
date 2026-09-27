import { useState } from 'react'
import { api, ApiError } from '../services/api'
import { useAuth } from '../state/auth'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/ui/EmptyState'
import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import './ContribuicaoPage.css'

const contentTypes = [
  { value: '', label: 'Selecione um tipo' },
  { value: 'resumo', label: 'Resumo' },
  { value: 'dica', label: 'Dica' },
  { value: 'dificuldade', label: 'Dificuldade comum' },
  { value: 'prova', label: 'Prova' },
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

function ContribuicaoPage({ courses = [], disciplines = [], onNavigate }) {
  const { isAuthenticated } = useAuth()
  const [form, setForm] = useState(initialForm)
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  function updateField(event) {
    const { name, value } = event.target
    setForm((currentForm) => ({ ...currentForm, [name]: value }))
    setError(null)
  }

  function validateForm() {
    const missingFields = []

    if (!form.curso_id) missingFields.push('curso')
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
    const validationError = validateForm()

    if (validationError) {
      setError(validationError)
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      await api.post('/contribuicoes', {
        curso_id: form.curso_id,
        disciplina_id: form.disciplina_id,
        tipo: form.tipo,
        titulo: form.titulo.trim(),
        conteudo: form.conteudo.trim() || undefined,
        url: form.url.trim() || undefined,
      })
      setSubmitted(true)
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível enviar sua contribuição.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="contribution-shell">
        <SiteHeader active="conhecimento" onNavigate={onNavigate} />
        <main className="contribution-page">
          <EmptyState title="Entre para contribuir">
            É necessário estar autenticado para enviar uma contribuição.
            <span className="contribution-page__action"><Button onClick={() => onNavigate('/login')}>Entrar</Button></span>
          </EmptyState>
        </main>
        <SiteFooter />
      </div>
    )
  }

  if (submitted) {
    return (
      <div className="contribution-shell">
        <SiteHeader active="conhecimento" onNavigate={onNavigate} />
        <main className="contribution-page">
          <EmptyState title="Contribuição enviada">
            Sua contribuição foi registrada como pendente e será analisada pela moderação.
            <span className="contribution-page__action"><Button variant="outline" onClick={() => onNavigate('/base-de-conhecimentos')}>Voltar para a base</Button></span>
          </EmptyState>
        </main>
        <SiteFooter />
      </div>
    )
  }

  return (
    <div className="contribution-shell">
      <SiteHeader active="conhecimento" onNavigate={onNavigate} />
      <main className="contribution-page">
        <header className="contribution-page__header">
          <p className="contribution-page__eyebrow">Colaboração acadêmica</p>
          <h1>Envie uma contribuição</h1>
          <p>Compartilhe um material útil. A publicação acontece somente após a revisão da equipe.</p>
        </header>
        <form className="contribution-form" onSubmit={submitContribution} noValidate>
          <div className="contribution-form__grid">
            <label>
              Curso <span aria-hidden="true">*</span>
              {courses.length > 0 ? (
                <select name="curso_id" value={form.curso_id} onChange={updateField}>
                  <option value="">Selecione um curso</option>
                  {courses.map((course) => <option key={course.id} value={course.id}>{course.nome || course.name}</option>)}
                </select>
              ) : <input name="curso_id" value={form.curso_id} onChange={updateField} placeholder="Código do curso" />}
            </label>
            <label>
              Disciplina <span aria-hidden="true">*</span>
              {disciplines.length > 0 ? (
                <select name="disciplina_id" value={form.disciplina_id} onChange={updateField}>
                  <option value="">Selecione uma disciplina</option>
                  {disciplines.map((discipline) => <option key={discipline.id} value={discipline.id}>{discipline.nome || discipline.name}</option>)}
                </select>
              ) : <input name="disciplina_id" value={form.disciplina_id} onChange={updateField} placeholder="Código da disciplina" />}
            </label>
          </div>
          <div className="contribution-form__grid">
            <label>
              Tipo de conteúdo <span aria-hidden="true">*</span>
              <select name="tipo" value={form.tipo} onChange={updateField}>
                {contentTypes.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
              </select>
            </label>
            <label>
              Título <span aria-hidden="true">*</span>
              <input name="titulo" value={form.titulo} onChange={updateField} placeholder="Ex.: Resumo da unidade 1" />
            </label>
          </div>
          <label>
            Conteúdo
            <textarea name="conteudo" value={form.conteudo} onChange={updateField} rows="8" placeholder="Escreva o conteúdo da contribuição" />
          </label>
          <label>
            URL do material <span className="contribution-form__hint">(preencha o conteúdo ou a URL)</span>
            <input name="url" type="url" value={form.url} onChange={updateField} placeholder="https://..." />
          </label>
          {error && <ErrorMessage>{error}</ErrorMessage>}
          <div className="contribution-form__footer">
            <p><strong>Revisão:</strong> novas contribuições começam com estado pendente.</p>
            <Button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Enviando...' : 'Enviar contribuição'}</Button>
          </div>
        </form>
      </main>
      <SiteFooter />
    </div>
  )
}

export default ContribuicaoPage