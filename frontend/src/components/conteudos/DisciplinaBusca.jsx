import { useEffect, useId, useMemo, useState } from 'react'
import { api, ApiError } from '../../services/api'
import './DisciplinaBusca.css'

const MIN_CARACTERES = 2
const ATRASO_BUSCA_MS = 300
const MAX_RESULTADOS_DO_CURSO = 50

export function rotuloDisciplina(disciplina) {
  if (!disciplina) return ''
  return [disciplina.codigo, disciplina.nome || disciplina.name].filter(Boolean).join(' - ')
}

function normalizar(texto) {
  return String(texto || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim()
}

// Mesma regra da API: cada termo precisa ser o começo de uma palavra do código ou do nome.
function combina(disciplina, termos) {
  const palavras = normalizar(`${disciplina.codigo || ''} ${disciplina.nome || disciplina.name || ''}`).split(/\s+/)
  return termos.every((termo) => palavras.some((palavra) => palavra.startsWith(termo)))
}

function nomesDosCursos(disciplina, cursos) {
  const ids = Array.isArray(disciplina.curso_id) ? disciplina.curso_id : []
  const nomes = ids
    .map((id) => cursos.find((curso) => Number(curso.id) === Number(id)))
    .filter(Boolean)
    .map((curso) => curso.nome || curso.name)
  if (nomes.length <= 2) return nomes.join(', ')
  return `${nomes.slice(0, 2).join(', ')} +${nomes.length - 2}`
}

/**
 * Campo de busca de disciplina.
 * - Com `cursoId`: lista as disciplinas do curso e filtra enquanto a pessoa digita.
 * - Sem `cursoId`: busca em todas as disciplinas pela API (`GET /disciplinas?busca=`).
 */
function DisciplinaBusca({ label = 'Disciplina', cursoId = '', cursos = [], value = null, onChange = () => {}, placeholder }) {
  const inputId = useId()
  const listId = useId()
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const [courseDisciplines, setCourseDisciplines] = useState({ cursoId: '', itens: [] })
  const [remote, setRemote] = useState({ termo: '', itens: [], erro: null })

  const termo = normalizar(query)

  useEffect(() => {
    if (!cursoId) return undefined

    const controller = new AbortController()
    api.get(`/cursos/${cursoId}/disciplinas`, { signal: controller.signal })
      .then((response) => setCourseDisciplines({ cursoId, itens: response?.itens || response?.disciplinas || [] }))
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') setCourseDisciplines({ cursoId, itens: [] })
      })

    return () => controller.abort()
  }, [cursoId])

  useEffect(() => {
    if (cursoId || value || termo.length < MIN_CARACTERES) return undefined

    const controller = new AbortController()
    const timer = setTimeout(() => {
      api.get(`/disciplinas?busca=${encodeURIComponent(termo)}`, { signal: controller.signal })
        .then((response) => setRemote({ termo, itens: response?.itens || [], erro: null }))
        .catch((requestError) => {
          if (requestError.name === 'AbortError') return
          const mensagem = requestError instanceof ApiError ? requestError.message : 'Não foi possível buscar as disciplinas.'
          setRemote({ termo, itens: [], erro: mensagem })
        })
    }, ATRASO_BUSCA_MS)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [cursoId, value, termo])

  const isCourseLoading = Boolean(cursoId) && courseDisciplines.cursoId !== cursoId
  const isSearching = !cursoId && termo.length >= MIN_CARACTERES && remote.termo !== termo

  const results = useMemo(() => {
    if (cursoId) {
      if (courseDisciplines.cursoId !== cursoId) return []
      const termos = termo ? termo.split(/\s+/) : []
      const filtradas = termos.length ? courseDisciplines.itens.filter((disciplina) => combina(disciplina, termos)) : courseDisciplines.itens
      return filtradas.slice(0, MAX_RESULTADOS_DO_CURSO)
    }
    if (termo.length < MIN_CARACTERES || remote.termo !== termo) return []
    return remote.itens
  }, [cursoId, courseDisciplines, termo, remote])

  let status = null
  if (cursoId && isCourseLoading) status = 'Carregando as disciplinas do curso...'
  else if (!cursoId && termo.length < MIN_CARACTERES) status = `Digite pelo menos ${MIN_CARACTERES} letras do nome ou o código.`
  else if (isSearching) status = 'Buscando disciplinas...'
  else if (!cursoId && remote.erro) status = remote.erro
  else if (results.length === 0) status = 'Nenhuma disciplina encontrada.'

  const inputValue = value ? rotuloDisciplina(value) : query
  const showList = isOpen && !value

  function select(disciplina) {
    onChange(disciplina)
    setQuery('')
    setIsOpen(false)
    setActiveIndex(-1)
  }

  function clear() {
    onChange(null)
    setQuery('')
    setIsOpen(true)
    setActiveIndex(-1)
  }

  function handleInput(event) {
    if (value) onChange(null)
    setQuery(event.target.value)
    setIsOpen(true)
    setActiveIndex(-1)
  }

  function handleKeyDown(event) {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setIsOpen(true)
      setActiveIndex((index) => Math.min(index + 1, results.length - 1))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActiveIndex((index) => Math.max(index - 1, 0))
    } else if (event.key === 'Enter' && showList) {
      // Evita enviar o formulário ao escolher uma opção com Enter.
      event.preventDefault()
      if (results[activeIndex]) select(results[activeIndex])
    } else if (event.key === 'Escape') {
      setIsOpen(false)
    }
  }

  return (
    <div className="discipline-search">
      <label htmlFor={inputId} className="discipline-search__label">{label}</label>
      <div className="discipline-search__control">
        <input
          id={inputId}
          className="discipline-search__input"
          type="search"
          role="combobox"
          aria-expanded={showList}
          aria-controls={listId}
          aria-autocomplete="list"
          aria-activedescendant={showList && activeIndex >= 0 ? `${listId}-${activeIndex}` : undefined}
          autoComplete="off"
          value={inputValue}
          placeholder={placeholder || (cursoId ? 'Filtre pelo nome ou código' : 'Busque pelo nome ou código')}
          onChange={handleInput}
          onFocus={() => setIsOpen(true)}
          onBlur={() => setIsOpen(false)}
          onKeyDown={handleKeyDown}
        />
        {(value || query) && (
          <button type="button" className="discipline-search__clear" onClick={clear} aria-label="Limpar disciplina">
            ×
          </button>
        )}
        {showList && (
          <div className="discipline-search__popover">
            {status && <p className="discipline-search__status" role="status">{status}</p>}
            {results.length > 0 && (
              <ul id={listId} className="discipline-search__list" role="listbox" aria-label="Disciplinas encontradas">
                {results.map((disciplina, index) => {
                  const cursosDaDisciplina = !cursoId ? nomesDosCursos(disciplina, cursos) : ''
                  return (
                    <li
                      key={disciplina.id}
                      id={`${listId}-${index}`}
                      role="option"
                      aria-selected={index === activeIndex}
                      className={`discipline-search__option ${index === activeIndex ? 'discipline-search__option--active' : ''}`}
                      // onMouseDown roda antes do blur do campo, que fecharia a lista.
                      onMouseDown={(event) => {
                        event.preventDefault()
                        select(disciplina)
                      }}
                      onMouseEnter={() => setActiveIndex(index)}
                    >
                      <span className="discipline-search__name">{rotuloDisciplina(disciplina)}</span>
                      {cursosDaDisciplina && <span className="discipline-search__courses">{cursosDaDisciplina}</span>}
                    </li>
                  )
                })}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default DisciplinaBusca
