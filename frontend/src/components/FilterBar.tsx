import { FilterField } from '../types/filters';

interface FilterBarProps {
  fields: FilterField[];
  filters: Record<string, any>;
  onFilterChange: (key: string, value: any) => void;
  onClear: () => void;
  hasActiveFilters: boolean;
  onToggle?: () => void;
  isVisible?: boolean;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  onSortChange?: (sortBy: string, sortOrder: 'asc' | 'desc') => void;
  sortableFields?: { value: string; label: string }[];
}

export function FilterBar({
  fields,
  filters,
  onFilterChange,
  onClear,
  hasActiveFilters,
  isVisible = true,
  sortBy,
  sortOrder,
  onSortChange,
  sortableFields = []
}) {
  if (!isVisible) return null;

  const handleSortFieldChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newSortBy = e.target.value;
    if (onSortChange) onSortChange(newSortBy, sortOrder || 'asc');
  };

  const handleSortOrderToggle = () => {
    if (onSortChange && sortBy) {
      const newOrder = sortOrder === 'asc' ? 'desc' : 'asc';
      onSortChange(sortBy, newOrder);
    }
  };

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
        {sortableFields.length > 0 && onSortChange && (
          <div className="filter-item">
            <label>Сортировать по</label>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <select value={sortBy || ''} onChange={handleSortFieldChange} style={{ flex: 1 }}>
                <option value="">Без сортировки</option>
                {sortableFields.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
              {sortBy && (
                <button type="button" className="btn btn-sm" onClick={handleSortOrderToggle}>
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
