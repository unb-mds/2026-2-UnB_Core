// O projeto atende somente o campus do Gama. No SIGAA, os cursos desse campus
// pertencem à unidade "FCTE - CAMPUS UNB GAMA", que o crawler salva como sigla.
// Cursos com o mesmo nome em outros campi (ex.: Ceilândia - FCTS) ficam de fora.
export const SIGLA_CAMPUS_GAMA = 'FCTE'

export function filtrarCursosDoCampus(cursos) {
  if (!Array.isArray(cursos)) return []
  return cursos.filter((curso) => String(curso?.sigla || '').trim().toUpperCase() === SIGLA_CAMPUS_GAMA)
}

export function extrairCursos(response) {
  return filtrarCursosDoCampus(response?.itens || response?.cursos || [])
}
