import { useEffect, useState } from 'react'
import Button from '../ui/Button'

function EntidadeFormModal({ entity, initialData, fields, onClose, onSubmit, isSubmitting = false }) {
  const [form, setForm] = useState(initialData || {})
  useEffect(() => setForm(initialData || {}), [initialData])
  if (!entity) return null

  return (
    <div className="governance-modal__overlay" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <form className="governance-modal" role="dialog" aria-modal="true" aria-labelledby="entity-title" onSubmit={(event) => { event.preventDefault(); onSubmit(form) }}>
        <h2 id="entity-title">{initialData?.id ? 'Editar' : 'Criar'} {entity}</h2>
        {fields.map((field) => (
          <label key={field.name} htmlFor={`entity-${field.name}`}>
            {field.label}
            <input id={`entity-${field.name}`} type={field.type || 'text'} value={form[field.name] || ''} required={field.required !== false} onChange={(event) => setForm({ ...form, [field.name]: event.target.value })} />
          </label>
        ))}
        <div className="governance-modal__actions">
          <Button type="button" variant="outline" onClick={onClose}>Cancelar</Button>
          <Button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Salvando...' : 'Salvar'}</Button>
        </div>
      </form>
    </div>
  )
}

export default EntidadeFormModal
