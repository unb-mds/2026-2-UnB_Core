// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../services/api'
import ConhecimentoPage from './ConhecimentoPage'

vi.mock('../services/api', async (importOriginal) => ({
  ...(await importOriginal()),
  api: { get: vi.fn() },
}))

function conteudo(id, titulo, extra = {}) {
  return {
    id,
    disciplina_id: 3,
    disciplina_codigo: 'FGA0003',
    disciplina_nome: 'COMPILADORES 1',
    tipo: 'resumo',
    titulo,
    corpo_ou_url: 'texto',
    autor_id: 1,
    autor_nome: 'Ana Souza',
    origem: null,
    atualizado_em: '2026-11-20T12:00:00Z',
    ...extra,
  }
}

// Simula a API: 13 conteúdos no total, 12 por página.
const todos = Array.from({ length: 13 }, (_, indice) => conteudo(indice + 1, `Conteúdo ${indice + 1}`))

function respostas({ itens = todos, porPagina = 12 } = {}) {
  api.get.mockImplementation((path) => {
    if (path.startsWith('/cursos')) {
      return Promise.resolve({ itens: [{ id: 33, nome: 'ENGENHARIA DE SOFTWARE', sigla: 'FCTE' }] })
    }
    if (path.startsWith('/conteudos?')) {
      const pagina = Number(new URLSearchParams(path.split('?')[1]).get('pagina') || 1)
      const inicio = (pagina - 1) * porPagina
      return Promise.resolve({ itens: itens.slice(inicio, inicio + porPagina), total: itens.length })
    }
    return Promise.resolve({ itens: [] })
  })
}

function ultimaConsulta() {
  const chamadas = api.get.mock.calls.map(([path]) => path).filter((path) => path.startsWith('/conteudos?'))
  return new URLSearchParams(chamadas.at(-1).split('?')[1])
}

beforeEach(() => {
  window.history.replaceState({}, '', '/base-de-conhecimentos')
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('ConhecimentoPage', () => {
  it('mostra os conteúdos sem precisar escolher curso ou disciplina', async () => {
    respostas()

    render(<ConhecimentoPage onNavigate={() => {}} />)

    expect(await screen.findByText('Conteúdo 1')).toBeInTheDocument()
    expect(screen.getByText('Mostrando 12 de 13 conteúdos')).toBeInTheDocument()
    // Sem disciplina escolhida, cada card mostra a disciplina.
    expect(screen.getAllByText('FGA0003 - COMPILADORES 1')).toHaveLength(12)

    const consulta = ultimaConsulta()
    expect(consulta.get('ordem')).toBe('recentes')
    expect(consulta.get('pagina')).toBe('1')
    expect(consulta.has('curso_id')).toBe(false)
    expect(consulta.has('disciplina_id')).toBe(false)
  })

  it('carrega a próxima página com "Carregar mais"', async () => {
    respostas()

    render(<ConhecimentoPage onNavigate={() => {}} />)

    fireEvent.click(await screen.findByRole('button', { name: 'Carregar mais' }))

    expect(await screen.findByText('Conteúdo 13')).toBeInTheDocument()
    expect(screen.getByText('13 conteúdos')).toBeInTheDocument()
    expect(ultimaConsulta().get('pagina')).toBe('2')
    expect(screen.queryByRole('button', { name: 'Carregar mais' })).not.toBeInTheDocument()
  })

  it('filtra por tipo e curso, ordena e limpa os filtros', async () => {
    respostas()

    render(<ConhecimentoPage onNavigate={() => {}} />)
    await screen.findByText('Conteúdo 1')

    fireEvent.change(screen.getByRole('combobox', { name: 'Tipo de conteúdo' }), { target: { value: 'prova' } })
    await waitFor(() => expect(ultimaConsulta().get('tipo')).toBe('prova'))

    fireEvent.change(screen.getByRole('combobox', { name: 'Curso' }), { target: { value: '33' } })
    await waitFor(() => expect(ultimaConsulta().get('curso_id')).toBe('33'))

    fireEvent.change(screen.getByRole('combobox', { name: 'Ordenar por' }), { target: { value: 'antigos' } })
    await waitFor(() => expect(ultimaConsulta().get('ordem')).toBe('antigos'))

    fireEvent.click(screen.getByRole('button', { name: 'Limpar filtros' }))
    await waitFor(() => {
      const consulta = ultimaConsulta()
      expect(consulta.has('tipo')).toBe(false)
      expect(consulta.has('curso_id')).toBe(false)
    })
    // A ordem escolhida não é um filtro e continua valendo.
    expect(ultimaConsulta().get('ordem')).toBe('antigos')
  })

  it('avisa quando os filtros não encontram nada e quando ainda não há conteúdos', async () => {
    respostas({ itens: [] })

    render(<ConhecimentoPage onNavigate={() => {}} />)
    expect(await screen.findByText('Ainda não há conteúdos publicados')).toBeInTheDocument()

    fireEvent.change(screen.getByRole('combobox', { name: 'Tipo de conteúdo' }), { target: { value: 'dica' } })
    expect(await screen.findByText('Nenhum conteúdo para estes filtros')).toBeInTheDocument()
  })

  it('abre a página do conteúdo ao clicar no card', async () => {
    respostas()
    const onNavigate = vi.fn()

    render(<ConhecimentoPage onNavigate={onNavigate} />)

    fireEvent.click((await screen.findAllByRole('button', { name: 'Ver conteúdo' }))[0])
    expect(onNavigate).toHaveBeenCalledWith('/conteudos/1')
  })
})
