import Button from '../ui/Button'
import { classeTipo, ehLink, formatarData, rotuloDisciplinaDoConteudo } from './formatacao'
import TipoBadge from './TipoBadge'
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

// Clique normal abre pelo onOpen (painel ou navegação interna). Ctrl/Cmd/Shift ou botão
// do meio deixam o navegador abrir o link em outra aba, como em qualquer link.
function abrirSemRecarregar(event, content, onOpen) {
  if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return
  event.preventDefault()
  onOpen(content)
}

function ConteudoCard({ content, onOpen, showDiscipline = false, headingLevel = 2 }) {
  const Titulo = headingLevel === 3 ? 'h3' : 'h2'

  return (
    <article className={`knowledge-card ${classeTipo(content.tipo)}`.trim()}>
      <div className="knowledge-card__topline">
        <TipoBadge tipo={content.tipo} />
        <span>{formatarData(content.atualizado_em || content.data_atualizacao, 'medium')}</span>
      </div>
      <Titulo className="knowledge-card__title">
        {content.id ? (
          <a href={`/conteudos/${content.id}`} onClick={(event) => abrirSemRecarregar(event, content, onOpen)}>
            {content.titulo}
          </a>
        ) : content.titulo}
      </Titulo>
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
