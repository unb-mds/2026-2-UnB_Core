function PublicacaoLinkOficial({ url }) {
  if (!url) {
    return (
      <p className="publication-detail__warning">
        O link oficial não está disponível. Consulte a unidade responsável antes de utilizar esta informação.
      </p>
    )
  }

  return (
    <div className="publication-detail__disclaimer">
      <span aria-hidden="true">i</span>
      <p>Em caso de divergência, a informação do canal oficial prevalece.</p>
    </div>
  )
}

export default PublicacaoLinkOficial