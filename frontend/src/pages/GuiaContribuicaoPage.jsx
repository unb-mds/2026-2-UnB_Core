import Button from '../components/ui/Button'
import SiteHeader from '../components/SiteHeader'
import SiteFooter from '../components/SiteFooter'
import './GuiaContribuicaoPage.css'

const contentTypes = [
  { label: 'Resumo', description: 'Síntese de um assunto específico da disciplina.' },
  { label: 'Dica de estudo', description: 'Estratégias que ajudaram você a estudar ou se organizar.' },
  { label: 'Dificuldade comum', description: 'Pontos em que a turma costuma travar, e como superar.' },
  { label: 'Implementação', description: 'Código ou exemplo prático relacionado ao conteúdo.' },
  { label: 'Link útil', description: 'Material externo (vídeo, artigo, ferramenta) que ajudou você.' },
]

const steps = [
  { title: 'Você envia', description: 'Preenche curso, disciplina, tipo de conteúdo e o material em si.' },
  { title: 'Fica pendente', description: 'Ninguém vê sua contribuição publicamente ainda — ela aguarda revisão.' },
  { title: 'Um moderador revisa', description: 'Pode aprovar, pedir ajustes (com justificativa) ou, em casos raros, rejeitar.' },
  { title: 'Publicado', description: 'Uma vez aprovada, a contribuição fica visível pra qualquer estudante na Base de Conhecimento.' },
]

function GuiaContribuicaoPage({ onNavigate }) {
  return (
    <div className="guide-shell page-shell">
      <SiteHeader active="conhecimento" onNavigate={onNavigate} />

      <main className="guide-page">
        <header className="guide-page__header">
          <p className="guide-page__eyebrow">Antes de contribuir</p>
          <h1>Guia de primeira contribuição</h1>
          <p>
            Qualquer estudante pode contribuir com a Base de Conhecimento. Este guia resume o que
            pode ser enviado, o que evitar, e como funciona a revisão — leva menos de 2 minutos.
          </p>
        </header>

        <section className="guide-section" aria-labelledby="guide-types-title">
          <h2 id="guide-types-title">O que você pode contribuir</h2>
          <div className="guide-types">
            {contentTypes.map((type) => (
              <div className="guide-types__item" key={type.label}>
                <span className="tag tag-outline">{type.label}</span>
                <p>{type.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="guide-section" aria-labelledby="guide-caution-title">
          <h2 id="guide-caution-title">Antes de enviar</h2>
          <ul className="guide-list">
            <li>Cite a fonte quando o conteúdo vier de material de terceiros.</li>
            <li>
              Não envie provas ou listas de exercícios que se repetem entre semestres — isso pode gerar
              problema com professores e não é aceito no momento.
            </li>
            <li>Seja objetivo: um bom resumo ou dica costuma valer mais do que um texto longo.</li>
            <li>Se o conteúdo for uma correção de algo já publicado, descreva o que mudou.</li>
          </ul>
        </section>

        <section className="guide-section" aria-labelledby="guide-steps-title">
          <h2 id="guide-steps-title">Como funciona a revisão</h2>
          <ol className="guide-steps">
            {steps.map((step, index) => (
              <li key={step.title}>
                <span className="guide-steps__number">{index + 1}</span>
                <div>
                  <strong>{step.title}</strong>
                  <p>{step.description}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <div className="guide-page__cta">
          <Button variant="primary" onClick={() => onNavigate?.('/contribuicao')}>
            Começar minha contribuição
          </Button>
        </div>
      </main>

      <SiteFooter />
    </div>
  )
}

export default GuiaContribuicaoPage
