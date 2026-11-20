import ConteudoCorpo, { TextoOuLink } from './ConteudoCorpo'
import { formatarData, rotuloDisciplinaDoConteudo, rotuloTipo } from './formatacao'
import './conteudos.css'

/**
 * Detalhe de um conteúdo publicado.
 * - Painel lateral (padrão): mostra o botão de fechar e, com `onOpenPage`, o link para a página.
 * - Página (`isPage`): vira um <article> com <h1> e sem botão de fechar.
 */
function ConteudoDetalhe({ content, onClose, onOpenPage, isPage = false }) {
  if (!content) {
    return null
  }

  const Container = isPage ? 'article' : 'aside'

  return (
    // Na página, o título fica no cabeçalho do PageLayout (h1); aqui só o tipo.
    <Container className="content-detail" aria-labelledby={isPage ? undefined : 'content-detail-title'} aria-label={isPage ? content.titulo : undefined}>
      <div className="content-detail__heading">
        <div>
          <span className="badge badge-category">{rotuloTipo(content.tipo)}</span>
          {!isPage && <h2 id="content-detail-title">{content.titulo}</h2>}
        </div>
        {!isPage && onClose && (
          <button type="button" className="content-detail__close" onClick={onClose} aria-label="Fechar detalhes">
            ×
          </button>
        )}
      </div>
      <dl className="content-detail__metadata">
        <div>
          <dt>Disciplina</dt>
          <dd>{rotuloDisciplinaDoConteudo(content)}</dd>
        </div>
        <div>
          <dt>Autoria</dt>
          <dd>{content.autor_nome || content.autoria || 'Colaborador'}</dd>
        </div>
        <div>
          <dt>Atualizado em</dt>
          <dd>{formatarData(content.atualizado_em || content.data_atualizacao)}</dd>
        </div>
        {content.origem && (
          <div>
            <dt>Origem</dt>
            <dd><TextoOuLink texto={content.origem} /></dd>
          </div>
        )}
      </dl>
      <div className="content-detail__body">
        {content.nao_pesquisavel && (
          <div className="content-warning" role="note">
            <strong>Documento não pesquisável.</strong>
            <p>Consulte o documento original pelo link oficial para acessar o conteúdo completo.</p>
            {content.orientacao_link_oficial && <a href={content.orientacao_link_oficial} target="_blank" rel="noreferrer">Abrir documento oficial</a>}
          </div>
        )}
        {/* A API envia o texto em corpo_ou_url; os outros nomes ficam por compatibilidade. */}
        <ConteudoCorpo texto={content.corpo_ou_url || content.conteudo || content.descricao || content.resumo} />
      </div>
      {content.url && <a href={content.url} target="_blank" rel="noreferrer">Abrir material original</a>}
      {!isPage && onOpenPage && content.id && (
        <a
          href={`/conteudos/${content.id}`}
          onClick={(event) => {
            event.preventDefault()
            onOpenPage(content)
          }}
        >
          Abrir página do conteúdo
        </a>
      )}
    </Container>
  )
}

export default ConteudoDetalhe
