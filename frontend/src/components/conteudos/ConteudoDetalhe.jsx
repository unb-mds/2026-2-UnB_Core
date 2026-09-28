import './conteudos.css'

function formatDate(value) {
  if (!value) {
    return 'Data não informada'
  }

  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat('pt-BR', { dateStyle: 'long' }).format(date)
}

function ConteudoDetalhe({ content, onClose }) {
  if (!content) {
    return null
  }

  return (
    <aside className="content-detail" aria-labelledby="content-detail-title">
      <div className="content-detail__heading">
        <div>
          <span className="badge badge-category">{content.tipo || 'Conteúdo'}</span>
          <h2 id="content-detail-title">{content.titulo}</h2>
        </div>
        <button type="button" className="content-detail__close" onClick={onClose} aria-label="Fechar detalhes">
          ×
        </button>
      </div>
      <dl className="content-detail__metadata">
        <div>
          <dt>Disciplina</dt>
          <dd>{content.disciplina_nome || content.disciplina || 'Não informada'}</dd>
        </div>
        <div>
          <dt>Autoria</dt>
          <dd>{content.autor_nome || content.autoria || 'Colaborador'}</dd>
        </div>
        <div>
          <dt>Atualizado em</dt>
          <dd>{formatDate(content.atualizado_em || content.data_atualizacao)}</dd>
        </div>
        {content.origem && (
          <div>
            <dt>Origem</dt>
            <dd>{content.origem}</dd>
          </div>
        )}
      </dl>
      <div className="content-detail__body">
        <p>{content.conteudo || content.descricao || content.resumo || 'Este conteúdo não possui texto disponível.'}</p>
      </div>
      {content.url && <a href={content.url} target="_blank" rel="noreferrer">Abrir material original</a>}
    </aside>
  )
}

export default ConteudoDetalhe