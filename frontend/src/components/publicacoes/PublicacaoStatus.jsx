import StatusBadge from '../ui/StatusBadge'

function PublicacaoStatus({ publicacao }) {
  const isVerified = Boolean(publicacao?.ultima_verificacao)
  const statusMessage = isVerified
    ? 'Informações verificadas na data indicada.'
    : 'Esta publicação ainda não foi verificada.'

  return (
    <section className="publication-detail__block" aria-labelledby="publication-status-title">
      <h2 id="publication-status-title">Estado</h2>
      <StatusBadge status={publicacao?.estado} />
      <p className={!isVerified ? 'publication-detail__warning' : ''}>{statusMessage}</p>
    </section>
  )
}

export default PublicacaoStatus