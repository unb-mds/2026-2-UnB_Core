const ROTULOS_TIPO = {
  resumo: 'Resumo',
  dica: 'Dica de estudo',
  dificuldade: 'Dificuldade comum',
  prova: 'Prova',
  implementacao: 'Implementação',
  link: 'Link útil',
}

export function rotuloTipo(tipo) {
  return ROTULOS_TIPO[tipo] || tipo || 'Conteúdo'
}

// Classe com as cores do tipo (definidas em ui.css). Tipo desconhecido fica sem classe e usa o azul do site.
export function classeTipo(tipo) {
  return ROTULOS_TIPO[tipo] ? `tipo-${tipo}` : ''
}

export function formatarData(valor, estilo = 'long') {
  if (!valor) return 'Data não informada'
  const data = new Date(valor)
  return Number.isNaN(data.getTime())
    ? valor
    : new Intl.DateTimeFormat('pt-BR', { dateStyle: estilo }).format(data)
}

// Só links http(s) viram <a>, para não abrir esquemas como "javascript:".
export function ehLink(texto) {
  return /^https?:\/\/\S+$/i.test(String(texto || '').trim())
}

export function rotuloDisciplinaDoConteudo(item) {
  if (item?.disciplina_nome) {
    return [item.disciplina_codigo, item.disciplina_nome].filter(Boolean).join(' - ')
  }
  return item?.disciplina || 'Não informada'
}

// Começo de um texto longo, para cards e listas. Links viram uma frase curta.
export function trecho(texto, tamanho = 220) {
  const valor = String(texto || '').trim()
  if (!valor) return ''
  if (ehLink(valor)) return 'Link para um material externo.'
  return valor.length > tamanho ? `${valor.slice(0, tamanho).trimEnd()}…` : valor
}
