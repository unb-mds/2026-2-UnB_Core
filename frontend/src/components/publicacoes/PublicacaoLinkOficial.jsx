import Button from '../ui/Button'

function PublicacaoLinkOficial({ url }) {
  if (!url) {
    return (
      <p className="publication-detail__warning">
        O link oficial não está disponível. Consulte a unidade responsável antes de utilizar esta informação.
      </p>
    )
  }

  return (
    <div className="publication-detail__official-link">
      <div>
        <strong>Canal oficial</strong>
        <p>Em caso de divergência, a informação do canal oficial prevalece.</p>
      </div>
      <Button variant="accent" onClick={() => window.open(url, '_blank', 'noopener,noreferrer')}>
        Abrir fonte oficial
      </Button>
    </div>
  )
}

export default PublicacaoLinkOficial