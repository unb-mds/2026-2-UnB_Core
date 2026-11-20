export function extrairCursos(response) {
  const cursos = response?.itens || response?.cursos || []
  return Array.isArray(cursos) ? cursos : []
}
