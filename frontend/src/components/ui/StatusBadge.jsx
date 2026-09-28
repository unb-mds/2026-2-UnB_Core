import './ui.css'

const statusLabels = {
  ativa: 'Ativo',
  encerrada: 'Encerrado',
  arquivada: 'Arquivado',
  pendente: 'Pendente',
  aprovada: 'Aprovada',
  ajustes: 'Ajustes solicitados',
  rejeitada: 'Rejeitada',
}

function StatusBadge({ status, variant = 'status' }) {
  const label = statusLabels[status] || status || 'Não informado'
  const tone = status || 'unknown'

  return <span className={`badge badge-${variant} badge-${tone}`}>{label}</span>
}

export default StatusBadge