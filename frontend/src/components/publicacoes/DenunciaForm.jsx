import { useState } from 'react'
import { api, ApiError } from '../../services/api'
import { useAuth } from '../../state/auth'
import Button from '../ui/Button'
import ErrorMessage from '../ErrorMessage'

const reasons = [
  { value: 'conteudo_inadequado', label: 'Conteúdo inadequado' },
  { value: 'spam', label: 'Spam' },
  { value: 'violacao_direitos_autorais', label: 'Violação de direitos autorais' },
  { value: 'informacao_incorreta', label: 'Informação incorreta' },
]

function DenunciaForm({ publicacaoId, onClose, onSuccess }) {
  const { isAuthenticated } = useAuth()
  const [motivo, setMotivo] = useState('')
  const [descricao, setDescricao] = useState('')
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function submit(event) {
    event.preventDefault()
    if (!isAuthenticated) {
      setError('Entre na sua conta para denunciar uma publicação.')
      return
    }
    if (!motivo || !descricao.trim()) {
      setError('Selecione um motivo e descreva o problema.')
      return
    }
    setIsSubmitting(true)
    setError(null)
    try {
      await api.post(`/publicacoes/${publicacaoId}/denuncias`, { motivo, descricao: descricao.trim() })
      setMotivo('')
      setDescricao('')
      onSuccess?.()
      onClose?.()
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : 'Não foi possível registrar a denúncia.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form className="governance-form" onSubmit={submit} noValidate aria-labelledby="report-title">
      <h2 id="report-title">Denunciar publicação</h2>
      {error && <ErrorMessage>{error}</ErrorMessage>}
      <label htmlFor="report-reason">Motivo *</label>
      <select id="report-reason" value={motivo} onChange={(event) => setMotivo(event.target.value)} aria-required="true">
        <option value="">Selecione um motivo</option>
        {reasons.map((reason) => <option key={reason.value} value={reason.value}>{reason.label}</option>)}
      </select>
      <label htmlFor="report-description">Detalhes *</label>
      <textarea id="report-description" value={descricao} onChange={(event) => setDescricao(event.target.value)} rows="5" required aria-required="true" />
      <div className="governance-modal__actions">
        {onClose && <Button type="button" variant="outline" onClick={onClose}>Cancelar</Button>}
        <Button type="submit" disabled={isSubmitting || !isAuthenticated}>{isSubmitting ? 'Enviando...' : 'Enviar denúncia'}</Button>
      </div>
    </form>
  )
}

export default DenunciaForm
