function PublicacaoLinkOficial({ url }) {
  if (!url) {
    return (
      <p className="publication-detail__warning">
        O link oficial não está disponível. Consulte a unidade responsável antes de utilizar esta informação.
      </p>
    )
  }

  return (
    <p className="publication-detail__disclaimer">
      <span aria-hidden="true">ⓘ</span> O UNB CORE é um agregador e não substitui o canal oficial da UnB. Em caso de divergência, a fonte oficial sempre prevalece.
    </p>
  )
}

export default PublicacaoLinkOficial