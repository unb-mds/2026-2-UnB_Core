import { useEffect, useState } from 'react'
import Button from '../ui/Button'
import JustificativaInput from './JustificativaInput'

const actions = [
  { value: 'aprovar', label: 'Aprovar' },
  { value: 'ajustes', label: 'Solicitar ajustes' },
  { value: 'rejeitar', label: 'Rejeitar' },
  { value: 'arquivar', label: 'Arquivar' },
]

function DecisaoModal({ item, onClose, onSubmit, isSubmitting = false }) {
  const [decisao, setDecisao] = useState('aprovar')
  const [justificativa, setJustificativa] = useState('')
  const needsJustification = ['ajustes', 'rejeitar'].includes(decisao)

  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!item) return null

  function submit(event) {
    event.preventDefault()
    if (needsJustification && !justificativa.trim()) return
    onSubmit({ decisao, justificativa: justificativa.trim() || undefined })
  }

  return (
    <div className="governance-modal__overlay" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <form className="governance-modal" role="dialog" aria-modal="true" aria-labelledby="decision-title" onSubmit={submit}>
        <h2 id="decision-title">Decidir contribuição</h2>
        <p>{item.titulo || 'Contribuição sem título'}</p>
        <label htmlFor="decision-action">Decisão</label>
        <select id="decision-action" value={decisao} onChange={(event) => setDecisao(event.target.value)}>
          {actions.map((action) => <option key={action.value} value={action.value}>{action.label}</option>)}
        </select>
        <JustificativaInput value={justificativa} onChange={setJustificativa} required={needsJustification} />
        <div className="governance-modal__actions">
          <Button type="button" variant="outline" onClick={onClose}>Cancelar</Button>
          <Button type="submit" disabled={isSubmitting || (needsJustification && !justificativa.trim())}>{isSubmitting ? 'Enviando...' : 'Confirmar decisão'}</Button>
        </div>
      </form>
    </div>
  )
}

export default DecisaoModal
