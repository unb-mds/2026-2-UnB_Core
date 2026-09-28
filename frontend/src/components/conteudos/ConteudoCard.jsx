import Button from '../ui/Button'
import './conteudos.css'

function formatDate(value) {
  if (!value) {
    return 'Data não informada'
  }

  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium' }).format(date)
}

function ConteudoCard({ content, onOpen }) {
  return (
    <article className="knowledge-card">
      <div className="knowledge-card__topline">
        <span className="badge badge-category">{content.tipo || 'Conteúdo'}</span>
        <span>{formatDate(content.atualizado_em || content.data_atualizacao)}</span>
      </div>
      <h2>{content.titulo}</h2>
      <p>{content.resumo || content.descricao || 'Conteúdo acadêmico publicado pela comunidade.'}</p>
      <div className="knowledge-card__footer">
        <span>Por {content.autor_nome || content.autoria || 'colaborador'}</span>
        <Button variant="outline" onClick={() => onOpen(content)}>Ver conteúdo</Button>
      </div>
    </article>
  )
}

export default ConteudoCard