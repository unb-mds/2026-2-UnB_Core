import { classeTipo, rotuloTipo } from './formatacao'
import '../ui/ui.css'

// Traços dos ícones, desenhados numa grade de 24x24.
const TRACOS = {
  resumo: (
    <>
      <rect x="5" y="3" width="14" height="18" rx="2" />
      <path d="M9 8h6M9 12h6M9 16h4" />
    </>
  ),
  dica: (
    <>
      <path d="M9 18h6M10 21h4" />
      <path d="M12 3a6 6 0 0 0-3.6 10.8c.6.5 1.1 1.3 1.1 2.2h5c0-.9.5-1.7 1.1-2.2A6 6 0 0 0 12 3z" />
    </>
  ),
  dificuldade: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6M12 17.5h.01" />
    </>
  ),
  prova: (
    <>
      <rect x="6" y="4" width="12" height="17" rx="2" />
      <path d="M9 4V3h6v1M9 13l2 2 4-4" />
    </>
  ),
  implementacao: <path d="M8 8l-4 4 4 4M16 8l4 4-4 4M13.5 6l-3 12" />,
  link: (
    <>
      <path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1" />
      <path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1" />
    </>
  ),
}

// Ícone decorativo: o nome do tipo sempre aparece escrito ao lado.
export function IconeTipo({ tipo }) {
  if (!TRACOS[tipo]) return null
  return (
    <svg className="icone-tipo" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">
      {TRACOS[tipo]}
    </svg>
  )
}

function TipoBadge({ tipo, rotulo }) {
  return (
    <span className={`badge badge-tipo ${classeTipo(tipo)}`.trim()}>
      <IconeTipo tipo={tipo} />
      {rotulo || rotuloTipo(tipo)}
    </span>
  )
}

export default TipoBadge
