import './ui.css'

function SearchInput({ value, onChange, placeholder, name = 'termo' }) {
  return (
    <label className="search-input">
      <span aria-hidden="true">⌕</span>
      <input
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        aria-label="Buscar"
      />
    </label>
  )
}

export default SearchInput