import React from 'react';

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T) => string;
  selectedIds: string[];
  onSelect: (id: string, checked: boolean) => void;
  onSelectAll: (checked: boolean) => void;
  emptyMessage?: string;
  actions?: (item: T) => React.ReactNode;
  className?: string;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  selectedIds,
  onSelect,
  onSelectAll,
  emptyMessage = 'Нет данных',
  actions,
  className = '',
}: DataTableProps<T>) {
  const allSelected = data.length > 0 && data.every(item => selectedIds.includes(keyExtractor(item)));

  return (
    <div className={`table-container ${className}`}>
      <table className="table">
        <thead>
          <tr>
            {/*{<th className="checkbox-cell">
              <input type="checkbox" onChange={(e) => onSelectAll(e.target.checked)} checked={allSelected} />
            </th>*/}
            {columns.map(col => (
              <th key={col.key} className={col.className}>{col.header}</th>
            ))}
            {actions && <th></th>}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length + (actions ? 2 : 1)} className="text-center">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map(item => {
              const id = keyExtractor(item);
              const isSelected = selectedIds.includes(id);
              return (
                <tr key={id}>
                  {/*<td className="checkbox-cell">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={e => onSelect(id, e.target.checked)}
                    />
                  </td>*/}
                  {columns.map(col => (
                    <td key={col.key} className={col.className}>
                      {col.render ? col.render(item) : (item as any)[col.key]}
                    </td>
                  ))}
                  {actions && <td>{actions(item)}</td>}
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}
