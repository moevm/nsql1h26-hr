import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DataTable, Column } from '../components/DataTable';
import { CreateVacancyForm } from '../components/CreateVacancyForm';
import { FilterBar } from '../components/FilterBar';
import { useFilters } from '../hooks/useFilters';
import { FilterField } from '../types/filters';
import { toast } from 'sonner';
import { getVacancies, deleteVacancy, Vacancy } from '../api';
import { usePermissions } from '../hooks/usePermissions';
import '../styles/App.css';

const filterFields: FilterField[] = [
  { key: 'title', label: 'Название', type: 'text', placeholder: 'Название' },
  { key: 'description', label: 'Описание', type: 'text', placeholder: 'Ключевые слова' },
  { key: 'status', label: 'Статус', type: 'select', options: [{ value: 'OPEN', label: 'Открыта' }, { value: 'CLOSED', label: 'Закрыта' }] },
  { key: 'createdFrom', label: 'Создана с', type: 'date' },
  { key: 'createdTo', label: 'Создана по', type: 'date' },
];

export function Vacancies() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const permissions = usePermissions(user?.role);

  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [pagination, setPagination] = useState({ limit: 20, offset: 0 });
  const [showFilters, setShowFilters] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedVacancies, setSelectedVacancies] = useState<string[]>([]);

  const { filters, updateFilter, clearFilters, hasActiveFilters } = useFilters({
    title: '',
    description: '',
    status: 'all',
    createdFrom: '',
    createdTo: '',
  });

  useEffect(() => {
    loadVacancies();
  }, [filters, pagination]);

  async function loadVacancies() {
    setLoading(true);
    try {
      const params: any = {
        limit: pagination.limit,
        offset: pagination.offset,
      };
      if (filters.title) params.title = filters.title;
      if (filters.description) params.description_contains = filters.description;
      if (filters.status !== 'all') params.status = filters.status;
      if (filters.createdFrom) {
        params.created_at_from = Math.floor(new Date(filters.createdFrom).getTime() / 1000);
      }
      if (filters.createdTo) {
        params.created_at_to = Math.floor(new Date(filters.createdTo).getTime() / 1000);
      }
      const response = await getVacancies(params);
      setVacancies(response.items);
      setTotal(response.total);
    } catch (err) {
      toast.error('Ошибка загрузки вакансий');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleFilterChange = (key: string, value: any) => {
    updateFilter(key, value);
    setPagination(prev => ({ ...prev, offset: 0 }));
  };

  const handleClearFilters = () => {
    clearFilters();
    setPagination({ limit: 20, offset: 0 });
  };

  const handleSelectAll = (checked: boolean) => {
    setSelectedVacancies(checked ? vacancies.map(v => v.id) : []);
  };

  const handleSelectOne = (id: string, checked: boolean) => {
    setSelectedVacancies(prev => (checked ? [...prev, id] : prev.filter(x => x !== id)));
  };

  const handleBulkDelete = async () => {
    if (!permissions.canDeleteVacancy) {
      toast.error('У вас нет прав на удаление вакансий');
      return;
    }
    if (!window.confirm(`Удалить ${selectedVacancies.length} вакансий?`)) return;
    try {
      await Promise.all(selectedVacancies.map(id => deleteVacancy(id)));
      toast.success('Вакансии удалены');
      setSelectedVacancies([]);
      loadVacancies();
    } catch (err) {
      toast.error('Ошибка при удалении');
    }
  };

  const columns: Column<Vacancy>[] = [
    { key: 'title', header: 'Название' },
    { 
      key: 'description', 
      header: 'Описание', 
      render: v => v.description.length > 100 ? v.description.slice(0, 100) + '…' : v.description, 
      className: 'max-w-xs' 
    },
    { 
      key: 'status', 
      header: 'Статус', 
      render: v => (
        <span className={`badge ${v.status === 'OPEN' ? 'badge-success' : 'badge-danger'}`}>
          {v.status === 'OPEN' ? 'Открыта' : 'Закрыта'}
        </span>
      )
    },
    { 
      key: 'created_at', 
      header: 'Создана', 
      render: v => new Date(v.created_at * 1000).toLocaleDateString('ru-RU') 
    },
    { 
      key: 'closed_at', 
      header: 'Закрыта', 
      render: v => v.closed_at ? new Date(v.closed_at * 1000).toLocaleDateString('ru-RU') : '—' 
    }
  ];

  const totalPages = Math.ceil(total / pagination.limit);
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;

  return (
    <div className="content">
      <div className="page-header">
        <h2>Вакансии {total > 0 && `(${total})`}</h2>
        <div className="btn-group">
          {selectedVacancies.length > 0 && permissions.canDeleteVacancy && (
            <button className="btn btn-danger" onClick={handleBulkDelete}>
              🗑️ Удалить ({selectedVacancies.length})
            </button>)}
          <button className="btn" onClick={() => setShowFilters(!showFilters)}>
            🔍 Фильтры {hasActiveFilters && '●'}
          </button>
          {permissions.canCreateVacancy && (
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
              ➕ Создать вакансию
            </button>
          )}
        </div>
      </div>

      <FilterBar 
        fields={filterFields} 
        filters={filters} 
        onFilterChange={handleFilterChange} 
        onClear={handleClearFilters} 
        hasActiveFilters={hasActiveFilters} 
        isVisible={showFilters} 
      />

      {loading ? (
        <div>Загрузка...</div>
      ) : (
        <>
          <DataTable
            columns={columns}
            data={vacancies}
            keyExtractor={v => v.id}
            selectedIds={selectedVacancies}
            onSelect={handleSelectOne}
            onSelectAll={handleSelectAll}
            emptyMessage="Нет вакансий"
            actions={v => (
			  <button className="btn btn-sm" onClick={() => navigate(`/vacancies/${v.id}`)} title="Просмотр деталей">
				👁️
			  </button>
			)}
          />
          {totalPages > 1 && (
            <div className="pagination" style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1rem' }}>
              <button 
                className="btn btn-sm"
                disabled={pagination.offset === 0}
                onClick={() => setPagination(prev => ({ ...prev, offset: prev.offset - prev.limit }))}
              >
                ← Назад
              </button>
              <span style={{ padding: '0.25rem 0.5rem' }}>
                Страница {currentPage} из {totalPages}
              </span>
              <button 
                className="btn btn-sm"
                disabled={pagination.offset + pagination.limit >= total}
                onClick={() => setPagination(prev => ({ ...prev, offset: prev.offset + prev.limit }))}
              >
                Вперёд →
              </button>
            </div>
          )}
        </>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <CreateVacancyForm 
              onSuccess={() => { 
                setShowModal(false); 
                setPagination({ limit: 20, offset: 0 });
                loadVacancies(); 
              }} 
              onCancel={() => setShowModal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
