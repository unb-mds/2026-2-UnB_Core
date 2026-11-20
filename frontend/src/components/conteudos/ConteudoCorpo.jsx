import { ehLink } from './formatacao'

// Mostra o campo corpo_ou_url: texto corrido ou, se for uma URL, um link.
function ConteudoCorpo({ texto }) {
  const valor = String(texto || '').trim()

  if (!valor) {
    return <p>Este conteúdo não possui texto disponível.</p>
  }

  if (ehLink(valor)) {
    return (
      <p>
        <a href={valor} target="_blank" rel="noreferrer">Abrir material</a>
        <span className="content-detail__url">{valor}</span>
      </p>
    )
  }

  return <p>{valor}</p>
}

export function TextoOuLink({ texto }) {
  const valor = String(texto || '').trim()
  return ehLink(valor) ? <a href={valor} target="_blank" rel="noreferrer">{valor}</a> : valor
}

export default ConteudoCorpo
