import { useState } from 'react'
import { api, ApiError } from '../../services/api'
import ErrorMessage from '../ErrorMessage'
import Button from '../ui/Button'
import '../../pages/ContribuicaoPage.css'
import '../../pages/MinhasContribuicoesPage.css'

const contentTypes = [
  { value: 'resumo', label: 'Resumo' },
  { value: 'dica', label: 'Dica de estudo' },
  { value: 'dificuldade', label: 'Dificuldade comum' },
  { value: 'prova', label: 'Prova' },
  { value: 'implementacao', label: 'Implementação' },
  { value: 'link', label: 'Link útil' },
]

function toEditForm(contribution) {
  return {
    tipo: contribution.tipo || '',
    titulo: contribution.titulo || '',
    corpo_ou_url: contribution.corpo_ou_url || '',
    origem: contribution.origem || '',
  }
}

// Formulário de edição usado em "Minhas contribuições" e na página de cada contribuição.
function EditarContribuicaoForm({ contribution, onCancel, onSaved }) {
  const [form, setForm] = useState(() => toEditForm(contribution))
  const [error, setError] = useState(null)
  const [isSaving, setIsSaving] = useState(false)

  function updateField(event) {
    const { name, value } = event.target
    setForm((currentForm) => ({ ...currentForm, [name]: value }))
    setError(null)
  }

  async function submitEdit(event) {
    event.preventDefault()

    const missingFields = []
    if (!form.tipo) missingFields.push('tipo de conteúdo')
    if (!form.titulo.trim()) missingFields.push('título')
    if (!form.corpo_ou_url.trim()) missingFields.push('conteúdo ou URL')

    if (missingFields.length > 0) {
      setError(`Preencha os campos obrigatórios: ${missingFields.join(', ')}.`)
      return
    }

    setIsSaving(true)
    setError(null)

    try {
      const updated = await api.patch(`/contribuicoes/minhas/${contribution.id}`, {
        tipo: form.tipo,
        titulo: form.titulo.trim(),
        corpo_ou_url: form.corpo_ou_url.trim(),
        origem: form.origem.trim() || null,
      })
      onSaved(updated)
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível salvar a contribuição.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <form className="contribution-form my-contribution-card__edit" onSubmit={submitEdit} noValidate>
      <label>
        Tipo de conteúdo <span aria-hidden="true">*</span>
        <select name="tipo" value={form.tipo} onChange={updateField}>
          <option value="">Selecione um tipo</option>
          {contentTypes.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
        </select>
      </label>
      <label>
        Título <span aria-hidden="true">*</span>
        <input name="titulo" value={form.titulo} onChange={updateField} maxLength={200} />
      </label>
      <label>
        Conteúdo ou URL <span aria-hidden="true">*</span>
        <textarea name="corpo_ou_url" value={form.corpo_ou_url} onChange={updateField} rows="6" />
      </label>
      <label>
        Fonte / referência <span className="contribution-form__hint">(opcional)</span>
        <input name="origem" value={form.origem} onChange={updateField} maxLength={500} />
      </label>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      <div className="contribution-form__footer">
        <p><strong>Atenção:</strong> ao salvar, a contribuição volta para o estado pendente e passa por nova revisão.</p>
        <span className="my-contribution-card__actions">
          <Button variant="outline" onClick={onCancel} disabled={isSaving}>Cancelar</Button>
          <Button type="submit" disabled={isSaving}>{isSaving ? 'Salvando...' : 'Salvar alterações'}</Button>
        </span>
      </div>
    </form>
  )
}

export default EditarContribuicaoForm
