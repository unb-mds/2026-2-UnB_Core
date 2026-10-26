import Navigation from './Navigation'

function SiteHeader({ active = 'conhecimento', onNavigate }) {
  return <Navigation active={active} onNavigate={onNavigate} />
}

export default SiteHeader