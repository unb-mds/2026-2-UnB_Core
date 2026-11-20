import Navigation from './Navigation'

// O item aceso no menu vem do endereço da página (ver secaoAtiva em Navigation.jsx).
// A prop `active` que as páginas ainda passam é ignorada e pode ser removida aos poucos.
function SiteHeader({ onNavigate }) {
  return <Navigation onNavigate={onNavigate} />
}

export default SiteHeader
