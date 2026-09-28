import './components.css'

function ErrorMessage({ children, title = 'Não foi possível concluir a ação.', id }) {
  if (!children) {
    return null
  }

  return (
    <div id={id} className="error-message" role="alert">
      <strong>{title}</strong>
      <span>{children}</span>
    </div>
  )
}

export default ErrorMessage