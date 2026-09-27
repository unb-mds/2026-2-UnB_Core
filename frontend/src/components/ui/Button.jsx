import './ui.css'

function Button({ children, variant = 'primary', className = '', type = 'button', ...props }) {
  return (
    <button className={`btn btn-${variant} ${className}`.trim()} type={type} {...props}>
      {children}
    </button>
  )
}

export default Button