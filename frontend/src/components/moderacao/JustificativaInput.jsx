function JustificativaInput({ value, onChange, required = false, id = 'justificativa', error }) {
  return (
    <label htmlFor={id}>
      Justificativa{required ? ' *' : ''}
      <textarea id={id} value={value} onChange={(event) => onChange(event.target.value)} rows="4" maxLength="1000" required={required} aria-invalid={Boolean(error)} aria-describedby={`${id}-count`} />
      <small id={`${id}-count`}>{value.length}/1000 caracteres</small>
      {error && <span role="alert">{error}</span>}
    </label>
  )
}

export default JustificativaInput
