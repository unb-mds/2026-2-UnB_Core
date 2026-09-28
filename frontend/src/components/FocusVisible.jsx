import './components.css'

function FocusVisible({ children, className = '', ...props }) {
  return (
    <div className={`focus-visible ${className}`.trim()} {...props}>
      {children}
    </div>
  )
}

export default FocusVisible