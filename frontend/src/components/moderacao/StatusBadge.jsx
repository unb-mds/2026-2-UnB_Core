import '../../components/ui/ui.css'

const labels = {
  pendente: 'Pendente',
  aprovada: 'Aprovada',
  ajustes: 'Ajustes solicitados',
  rejeitada: 'Rejeitada',
  arquivada: 'Arquivada',
  deferida: 'Deferida',
  indeferida: 'Indeferida',
}

function StatusBadge({ status }) {
  const normalizedStatus = String(status || '').toLowerCase()
  return (
    <span className={`badge badge-status badge-${normalizedStatus || 'unknown'}`}>
      {labels[normalizedStatus] || status || 'Não informado'}
    </span>
  )
}

export default StatusBadge
