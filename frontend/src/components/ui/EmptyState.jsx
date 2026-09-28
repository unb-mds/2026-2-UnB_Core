import './ui.css'

function EmptyState({ title, children }) {
  return (
    <div className="empty-state">
      <h2>{title}</h2>
      {children && <p>{children}</p>}
    </div>
  )
}

export default EmptyState