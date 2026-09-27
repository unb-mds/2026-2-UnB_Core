function PublicacaoFonte({ publicacao }) {
  const fonte = publicacao?.fonte || publicacao?.fonte_oficial
  const nome = fonte?.nome || publicacao?.unidade_responsavel || 'Fonte oficial da UnB'
  const url = fonte?.url || publicacao?.url_oficial

  return (
    <section className="publication-detail__block" aria-labelledby="publication-source-title">
      <h2 id="publication-source-title">Origem da publicação</h2>
      <p>{nome}</p>
      {url && <a href={url} target="_blank" rel="noreferrer">Consultar fonte oficial</a>}
    </section>
  )
}

export default PublicacaoFonte