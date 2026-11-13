import Button from '../ui/Button'
import EmptyState from '../ui/EmptyState'

function TabelaEntidades({ columns, rows, isLoading = false, onEdit, onDelete }) {
  if (isLoading) return <p className="governance-status">Carregando registros...</p>
  if (!rows.length) return <EmptyState title="Nenhum registro encontrado" />
  return (
    <div className="entity-table-wrap">
      <table className="entity-table">
        <thead><tr>{columns.map((column) => <th key={column.key} scope="col">{column.label}</th>)}<th scope="col">Ações</th></tr></thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              {columns.map((column) => <td key={column.key}>{column.render ? column.render(row) : row[column.key] || '—'}</td>)}
              <td className="entity-table__actions">
                {onEdit && <Button variant="outline" onClick={() => onEdit(row)}>Editar</Button>}
                {onDelete && <Button variant="outline" onClick={() => onDelete(row)}>Arquivar</Button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default TabelaEntidades
