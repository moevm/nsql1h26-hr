import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { DataTable, Column } from '../components/DataTable';
import { CreateCandidateForm } from '../components/CreateCandidateForm';
import { FilterBar } from '../components/FilterBar';
import { useFilters } from '../hooks/useFilters';
import { FilterField } from '../types/filters';
import { toast } from 'sonner';
import { getCandidates, deleteCandidate, getVacancies, Candidate, Vacancy } from '../api';
import { usePermissions } from '../hooks/usePermissions';
import '../styles/App.css';

export function Candidates() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const permissions = usePermissions(user?.role);

  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [pagination, setPagination] = useState({ limit: 20, offset: 0 });
  const [showFilters, setShowFilters] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedCandidates, setSelectedCandidates] = useState<string[]>([]);

  const { filters, updateFilter, clearFilters, hasActiveFilters } = useFilters({
    full_name: '',
    email: '',
    phone: '',
    resume_url: '',
    status: 'all',
    vacancy_id: 'all',
    createdFrom: '',
    createdTo: '',
  });

  useEffect(() => {
    loadVacanciesForFilter();
  }, []);

  useEffect(() => {
    loadCandidates();
  }, [filters, pagination]);

  async function loadVacanciesForFilter() {
    try {
      const response = await getVacancies({ limit: 200 });
      setVacancies(response.items);
    } catch (err) {
      console.error('Failed to load vacancies for filter:', err);
    }
  }

  async function loadCandidates() {
    setLoading(true);
    try {
      const params: any = {
        limit: pagination.limit,
        offset: pagination.offset,
      };
      if (filters.full_name) params.full_name = filters.full_name;
      if (filters.email) params.email = filters.email;
      if (filters.phone) params.phone = filters.phone;
      if (filters.resume_url) params.resume_url_contains = filters.resume_url;
      if (filters.status !== 'all') params.status = filters.status;
      if (filters.vacancy_id !== 'all') params.vacancy_id = filters.vacancy_id;
      if (filters.createdFrom) {
        params.created_at_from = Math.floor(new Date(filters.createdFrom).getTime() / 1000);
      }
      if (filters.createdTo) {
        params.created_at_to = Math.floor(new Date(filters.createdTo).getTime() / 1000);
      }
      const response = await getCandidates(params);
      setCandidates(response.items);
      setTotal(response.total);
    } catch (err) {
      toast.error('Ошибка загрузки кандидатов');
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
    setSelectedCandidates(checked ? candidates.map(c => c.id) : []);
  };

  const handleSelectOne = (id: string, checked: boolean) => {
    setSelectedCandidates(prev => (checked ? [...prev, id] : prev.filter(x => x !== id)));
  };

  const handleBulkDelete = async () => {
    if (!permissions.canDeleteCandidate) {
      toast.error('У вас нет прав на удаление кандидатов');
      return;
    }
    if (!window.confirm(`Удалить ${selectedCandidates.length} кандидата(ов)?`)) return;
    try {
      await Promise.all(selectedCandidates.map(id => deleteCandidate(id)));
      toast.success('Кандидаты удалены');
      setSelectedCandidates([]);
      loadCandidates();
    } catch (err) {
      toast.error('Ошибка при удалении');
    }
  };

  const filterFields: FilterField[] = useMemo(() => {
    const vacancyOptions = vacancies.map(v => ({ value: v.id, label: v.title }));
    return [
      { key: 'full_name', label: 'ФИО', type: 'text', placeholder: 'Иванов' },
      { key: 'email', label: 'Email', type: 'text', placeholder: 'example@mail.com' },
      { key: 'phone', label: 'Телефон', type: 'text', placeholder: '+7999...' },
      { key: 'resume_url', label: 'Ссылка на резюме', type: 'text', placeholder: 'https://' },
      {
        key: 'status',
        label: 'Статус',
        type: 'select',
        options: [
          { value: 'NEW', label: 'Новый' },
          { value: 'TEST', label: 'Тестовое задание' },
          { value: 'INTERVIEW', label: 'Интервью' },
          { value: 'OFFER', label: 'Оффер' },
          { value: 'HIRED', label: 'Нанят' },
          { value: 'REJECTED', label: 'Отказ' },
        ],
      },
      { key: 'vacancy_id', label: 'Вакансия', type: 'select', options: vacancyOptions },
      { key: 'createdFrom', label: 'Создан с', type: 'date' },
      { key: 'createdTo', label: 'Создан по', type: 'date' },
    ];
  }, [vacancies]);

  const getStatusLabel = (status: string): string => {
    const statusMap: Record<string, string> = {
      'NEW': 'Новый',
      'TEST': 'Тестовое задание',
      'INTERVIEW': 'Интервью',
      'OFFER': 'Оффер',
      'HIRED': 'Нанят',
      'REJECTED': 'Отказ',
    };
    return statusMap[status] || status;
  };

  const getStatusBadgeClass = (status: string): string => {
    const classMap: Record<string, string> = {
      'NEW': 'badge',
      'TEST': 'badge-warning',
      'INTERVIEW': 'badge-info',
      'OFFER': 'badge-primary',
      'HIRED': 'badge-success',
      'REJECTED': 'badge-danger',
    };
    return classMap[status] || 'badge';
  };

  const columns: Column<Candidate>[] = [
    { key: 'id', header: 'ID' },
    { key: 'full_name', header: 'ФИО' },
    { key: 'email', header: 'Email' },
    { key: 'phone', header: 'Телефон' },
    {
      key: 'status',
      header: 'Статус',
      render: c => <span className={`badge ${getStatusBadgeClass(c.status)}`}>{getStatusLabel(c.status)}</span>,
    },
    {
      key: 'vacancy_id',
      header: 'Вакансия',
      render: c => vacancies.find(v => v.id === c.vacancy_id)?.title || '—',
    },
    {
      key: 'created_at',
      header: 'Создан',
      render: c => c.created_at ? new Date(c.created_at * 1000).toLocaleDateString('ru-RU') : '—',
    },
  ];

  const totalPages = Math.ceil(total / pagination.limit);
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;

  return (
    <div className="content">
      <div className="page-header">
        <h2>Кандидаты {total > 0 && `(${total})`}</h2>
        <div className="btn-group">
          {selectedCandidates.length > 0 && permissions.canDeleteCandidate && (
            <button className="btn btn-danger" onClick={handleBulkDelete}>
              🗑️ Удалить ({selectedCandidates.length})
            </button>
          )}
          <button className="btn" onClick={() => setShowFilters(!showFilters)}>
            🔍 Фильтры {hasActiveFilters && '●'}
          </button>
          {permissions.canCreateCandidate && (
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
              ➕ Добавить кандидата
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
            data={candidates}
            keyExtractor={c => c.id}
            selectedIds={selectedCandidates}
            onSelect={handleSelectOne}
            onSelectAll={handleSelectAll}
            emptyMessage="Нет кандидатов"
            actions={c => (
              <button className="btn btn-sm" onClick={() => {}} title="Просмотр деталей">
                👁️
              </button>
            )}
          />
          {totalPages > 1 && (
            <div className="pagination" style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1rem' }}>
              <button className="btn btn-sm" disabled={pagination.offset === 0} onClick={() => setPagination(prev => ({ ...prev, offset: prev.offset - prev.limit }))}>
                ← Назад
              </button>
              <span style={{ padding: '0.25rem 0.5rem' }}>Страница {currentPage} из {totalPages}</span>
              <button className="btn btn-sm" disabled={pagination.offset + pagination.limit >= total} onClick={() => setPagination(prev => ({ ...prev, offset: prev.offset + prev.limit }))}>
                Вперёд →
              </button>
            </div>
          )}
        </>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <CreateCandidateForm 
              onSuccess={() => { setShowModal(false); setPagination({ limit: 20, offset: 0 }); loadCandidates(); }} 
              onCancel={() => setShowModal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
