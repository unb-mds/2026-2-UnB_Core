import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { extrairCursos } from '../services/cursos'
import { useAuth } from '../state/auth'
import Button from '../components/ui/Button'
import EmptyState from '../components/ui/EmptyState'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import ConteudoCard from '../components/conteudos/ConteudoCard'
import DisciplinaBusca from '../components/conteudos/DisciplinaBusca'
import './ConhecimentoPage.css'
import './HomePage.css'

const QUANTIDADE_RECENTES = 6

const tiposDeConteudo = ['Resumos', 'Dicas de estudo', 'Dificuldades comuns', 'Provas', 'Implementações', 'Links úteis']

const passos = [
  {
    titulo: 'Encontre a disciplina',
    descricao: 'Busque pelo nome ou pelo código. Não precisa escolher o curso: a mesma disciplina reúne o material de todos os cursos que a oferecem.',
  },
  {
    titulo: 'Estude com o material da comunidade',
    descricao: 'Veja o que outros estudantes já compartilharam sobre a disciplina.',
    tipos: true,
  },
  {
    titulo: 'Contribua com o que você sabe',
    descricao: 'Envie o seu material. A moderação revisa antes de publicar, e você acompanha o andamento em Minhas contribuições.',
  },
]

function HomePage({ onNavigate }) {
  const { isAuthenticated } = useAuth()
  const [courses, setCourses] = useState([])
  const [recentes, setRecentes] = useState({ status: 'carregando', itens: [] })

  useEffect(() => {
    const controller = new AbortController()

    api
      .get('/cursos', { signal: controller.signal })
      .then((response) => setCourses(extrairCursos(response)))
      .catch(() => {})

    api
      .get(`/conteudos?limite=${QUANTIDADE_RECENTES}`, { signal: controller.signal })
      .then((response) => setRecentes({ status: 'pronto', itens: response?.itens || [] }))
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') setRecentes({ status: 'erro', itens: [] })
      })

    return () => controller.abort()
  }, [])

  function goTo(path) {
    return (event) => {
      event?.preventDefault()
      onNavigate?.(path)
    }
  }

  function openDiscipline(discipline) {
    if (discipline) onNavigate?.('/base-de-conhecimentos', { disciplina: discipline })
  }

  return (
    <div className="knowledge-shell page-shell">
      <SiteHeader active="inicio" onNavigate={onNavigate} />
      <main className="home-page">
        <section className="home-hero" aria-labelledby="home-title">
          <div className="home-hero__content">
            <p className="home-hero__eyebrow">FCTE · Campus Gama</p>
            <h1 id="home-title">O conhecimento da FCTE, organizado por disciplina</h1>
            <p className="home-hero__lead">
              Resumos, dicas, provas e materiais compartilhados por estudantes e revisados antes de serem publicados.
            </p>
            <div className="home-hero__search">
              <DisciplinaBusca
                label="Qual disciplina você quer estudar?"
                cursos={courses}
                value={null}
                onChange={openDiscipline}
                placeholder="Ex.: Cálculo 1 ou FGA0003"
              />
            </div>
            <div className="home-hero__actions">
              <Button variant="outline" onClick={goTo('/base-de-conhecimentos')}>Explorar a base de conhecimento</Button>
              <Button variant="outline" onClick={goTo('/contribuicao')}>Enviar uma contribuição</Button>
            </div>
          </div>
        </section>

        <section className="home-section" aria-labelledby="home-recent-title">
          <div className="home-section__heading">
            <h2 id="home-recent-title">Publicados recentemente</h2>
            <a href="/base-de-conhecimentos" onClick={goTo('/base-de-conhecimentos')}>Ver a base completa</a>
          </div>
          {recentes.status === 'carregando' && <p className="home-section__status">Carregando conteúdos...</p>}
          {recentes.status === 'erro' && (
            <p className="home-section__status">Não foi possível carregar os conteúdos agora.</p>
          )}
          {recentes.status === 'pronto' && recentes.itens.length === 0 && (
            <EmptyState title="Ainda não há conteúdos publicados">
              Seja a primeira pessoa a compartilhar um material com a comunidade.
              <span className="knowledge-results__action"><Button onClick={goTo('/contribuicao')}>Quero contribuir</Button></span>
            </EmptyState>
          )}
          {recentes.itens.length > 0 && (
            <div className="knowledge-grid">
              {recentes.itens.map((content) => (
                <ConteudoCard
                  key={content.id}
                  content={content}
                  showDiscipline
                  headingLevel={3}
                  onOpen={(item) => onNavigate?.(`/conteudos/${item.id}`)}
                />
              ))}
            </div>
          )}
        </section>

        <section className="home-section" aria-labelledby="home-how-title">
          <div className="home-section__heading">
            <h2 id="home-how-title">Como funciona</h2>
            <a href="/guia-de-contribuicao" onClick={goTo('/guia-de-contribuicao')}>Guia de contribuição</a>
          </div>
          <ol className="home-steps">
            {passos.map((passo, index) => (
              <li key={passo.titulo} className="home-steps__item">
                <span className="home-steps__number" aria-hidden="true">{index + 1}</span>
                <h3>{passo.titulo}</h3>
                <p>{passo.descricao}</p>
                {passo.tipos && (
                  <ul className="home-steps__types" aria-label="Tipos de conteúdo">
                    {tiposDeConteudo.map((tipo) => <li key={tipo}>{tipo}</li>)}
                  </ul>
                )}
              </li>
            ))}
          </ol>
        </section>

        <section className="home-cta" aria-labelledby="home-cta-title">
          {isAuthenticated ? (
            <>
              <div>
                <h2 id="home-cta-title">Compartilhe o que você aprendeu</h2>
                <p>Um resumo bem feito pode ajudar a próxima turma inteira.</p>
              </div>
              <div className="home-cta__actions">
                <Button onClick={goTo('/contribuicao')}>Enviar contribuição</Button>
                <Button variant="outline" onClick={goTo('/minhas-contribuicoes')}>Minhas contribuições</Button>
              </div>
            </>
          ) : (
            <>
              <div>
                <h2 id="home-cta-title">Faça parte da comunidade</h2>
                <p>Crie uma conta para enviar materiais e acompanhar a revisão das suas contribuições.</p>
              </div>
              <div className="home-cta__actions">
                <Button onClick={goTo('/cadastro')}>Criar conta</Button>
                <Button variant="outline" onClick={goTo('/login')}>Entrar</Button>
              </div>
            </>
          )}
        </section>
      </main>
      <SiteFooter />
    </div>
  )
}

export default HomePage
