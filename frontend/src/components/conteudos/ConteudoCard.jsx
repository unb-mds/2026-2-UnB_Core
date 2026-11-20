import Button from '../ui/Button'
import { ehLink, formatarData, rotuloDisciplinaDoConteudo, rotuloTipo } from './formatacao'
import './conteudos.css'

const TAMANHO_TRECHO = 160

// Trecho do texto do conteúdo para o card. A API envia o texto em corpo_ou_url.
function resumoDoConteudo(content) {
  const resumo = content.resumo || content.descricao
  if (resumo) return resumo

  const corpo = String(content.corpo_ou_url || '').trim()
  if (!corpo) return 'Conteúdo acadêmico publicado pela comunidade.'
  if (ehLink(corpo)) return 'Link para um material externo.'
  return corpo.length > TAMANHO_TRECHO ? `${corpo.slice(0, TAMANHO_TRECHO).trimEnd()}…` : corpo
}

function ConteudoCard({ content, onOpen, showDiscipline = false }) {
  return (
    <article className="knowledge-card">
      <div className="knowledge-card__topline">
        <span className="badge badge-category">{rotuloTipo(content.tipo)}</span>
        <span>{formatarData(content.atualizado_em || content.data_atualizacao, 'medium')}</span>
      </div>
      <h2>{content.titulo}</h2>
      {showDiscipline && <p className="knowledge-card__discipline">{rotuloDisciplinaDoConteudo(content)}</p>}
      <p>{resumoDoConteudo(content)}</p>
      {content.nao_pesquisavel && (
        <div className="content-warning" role="note">
          <strong>Documento não pesquisável.</strong>
          {content.orientacao_link_oficial && <a href={content.orientacao_link_oficial} target="_blank" rel="noreferrer">Consulte o documento original</a>}
        </div>
      )}
      <div className="knowledge-card__footer">
        <span>Por {content.autor_nome || content.autoria || 'colaborador'}</span>
        <Button variant="outline" onClick={() => onOpen(content)}>Ver conteúdo</Button>
      </div>
    </article>
  )
}

export default ConteudoCard
