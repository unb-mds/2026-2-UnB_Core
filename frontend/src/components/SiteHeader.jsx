import Navigation from './Navigation'

function SiteHeader({ active = 'editais', onNavigate }) {
  return <Navigation active={active} onNavigate={onNavigate} />
}

export default SiteHeader