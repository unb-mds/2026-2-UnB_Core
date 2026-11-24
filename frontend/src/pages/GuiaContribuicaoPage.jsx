import Button from '../components/ui/Button'
import PageLayout, { AsideCard } from '../components/layout/PageLayout'
import TipoBadge from '../components/conteudos/TipoBadge'
import { classeTipo } from '../components/conteudos/formatacao'
import './GuiaContribuicaoPage.css'

const contentTypes = [
  { tipo: 'resumo', description: 'Síntese de um assunto específico da disciplina.' },
  { tipo: 'dica', description: 'Estratégias que ajudaram você a estudar ou se organizar.' },
  { tipo: 'dificuldade', description: 'Pontos em que a turma costuma travar, e como superar.' },
  { tipo: 'implementacao', description: 'Código ou exemplo prático relacionado ao conteúdo.' },
  { tipo: 'link', description: 'Material externo (vídeo, artigo, ferramenta) que ajudou você.' },
]

const steps = [
  { title: 'Você envia', description: 'Preenche curso, disciplina, tipo de conteúdo e o material em si.' },
  { title: 'Fica pendente', description: 'Ninguém vê sua contribuição publicamente ainda — ela aguarda revisão.' },
  { title: 'Um moderador revisa', description: 'Pode aprovar, pedir ajustes (com justificativa) ou, em casos raros, rejeitar.' },
  { title: 'Publicado', description: 'Uma vez aprovada, a contribuição fica visível pra qualquer estudante na Base de Conhecimento.' },
]

function GuiaContribuicaoPage({ onNavigate }) {
  const aside = (
    <AsideCard title="Pronto para contribuir?">
      <p>Leva poucos minutos. Você pode editar a contribuição enquanto ela estiver em revisão.</p>
      <Button variant="primary" onClick={() => onNavigate?.('/contribuicao')}>
        Começar minha contribuição
      </Button>
    </AsideCard>
  )

  return (
    <PageLayout
      onNavigate={onNavigate}
      eyebrow="Antes de contribuir"
      title="Guia de primeira contribuição"
      description="Qualquer estudante pode contribuir com a Base de Conhecimento. Este guia resume o que pode ser enviado, o que evitar e como funciona a revisão. Leva menos de 2 minutos."
      aside={aside}
      asideLabel="Começar a contribuir"
    >
      <section className="guide-section" aria-labelledby="guide-types-title">
        <h2 id="guide-types-title">O que você pode contribuir</h2>
        <div className="guide-types">
          {contentTypes.map((type) => (
            <div className={`guide-types__item ${classeTipo(type.tipo)}`} key={type.tipo}>
              <TipoBadge tipo={type.tipo} />
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

    </PageLayout>
  )
}

export default GuiaContribuicaoPage
