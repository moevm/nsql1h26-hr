import { FilterField } from '../types/filters';

interface FilterBarProps {
  fields: FilterField[];
  filters: Record<string, any>;
  onFilterChange: (key: string, value: any) => void;
  onClear: () => void;
  hasActiveFilters: boolean;
  onToggle?: () => void;
  isVisible?: boolean;
}

export function FilterBar({ fields, filters, onFilterChange, onClear, hasActiveFilters, onToggle, isVisible = true }) {
  if (!isVisible) return null;

  return (
    <div className="filter-card">
      <div className="filter-header">
        <h3>Фильтры</h3>
        {hasActiveFilters && <button className="btn btn-sm" onClick={onClear}>✖ Очистить</button>}
      </div>
      <div className="filter-grid">
        {fields.map(field => (
          <div key={field.key} className="filter-item">
            <label>{field.label}</label>
            {field.type === 'text' && (
              <input
                type="text"
                placeholder={field.placeholder}
                value={filters[field.key] || ''}
                onChange={e => onFilterChange(field.key, e.target.value)}
              />
            )}
            {field.type === 'select' && (
              <select value={filters[field.key] || 'all'} onChange={e => onFilterChange(field.key, e.target.value)}>
                <option value="all">Все</option>
                {field.options?.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
              </select>
            )}
            {field.type === 'date' && (
              <input type="date" value={filters[field.key] || ''} onChange={e => onFilterChange(field.key, e.target.value)} />
            )}
            {field.type === 'datetime-local' && (
              <input type="datetime-local" value={filters[field.key] || ''} onChange={e => onFilterChange(field.key, e.target.value)} />
            )}
            {field.type === 'number' && (
  <input
    type="number"
    placeholder={field.placeholder}
    value={filters[field.key] || ''}
    onChange={e => onFilterChange(field.key, e.target.value)}
  />
)}
          </div>
        ))}
      </div>
    </div>
  );
}
