function formatDate(value) {
  if (!value) {
    return 'Não informado'
  }

  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat('pt-BR', { dateStyle: 'long' }).format(date)
}

function PublicacaoDatas({ publicacao }) {
  return (
    <section className="publication-detail__block" aria-labelledby="publication-dates-title">
      <h2 id="publication-dates-title">Datas importantes</h2>
      <dl className="publication-detail__dates">
        <div>
          <dt>Publicado em</dt>
          <dd>{formatDate(publicacao?.data_publicacao)}</dd>
        </div>
        <div>
          <dt>Prazo</dt>
          <dd>{formatDate(publicacao?.prazo)}</dd>
        </div>
        <div>
          <dt>Última verificação</dt>
          <dd>{formatDate(publicacao?.ultima_verificacao)}</dd>
        </div>
      </dl>
    </section>
  )
}

export default PublicacaoDatas