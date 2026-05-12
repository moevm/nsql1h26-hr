import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { DataTable, Column } from '../components/DataTable';
import { CreateOfferForm } from '../components/CreateOfferForm';
import { FilterBar } from '../components/FilterBar';
import { useFilters } from '../hooks/useFilters';
import { FilterField } from '../types/filters';
import { toast } from 'sonner';
import { getOffers, deleteOffer, getCandidates, getVacancies, Offer, Candidate, Vacancy } from '../api';
import { usePermissions } from '../hooks/usePermissions';
import '../styles/App.css';

export function Offers() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const permissions = usePermissions(user?.role);

  const [offers, setOffers] = useState<Offer[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [pagination, setPagination] = useState({ limit: 20, offset: 0 });
  const [showFilters, setShowFilters] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedOffers, setSelectedOffers] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<string>('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const { filters, updateFilter, clearFilters, hasActiveFilters } = useFilters({
    candidate_id: 'all',
    vacancy_id: 'all',
    status: 'all',
    salaryFrom: '',
    salaryTo: '',
    createdFrom: '',
    createdTo: '',
  });

  useEffect(() => {
    loadReferenceData();
  }, []);

  useEffect(() => {
    loadOffers();
  }, [filters, pagination, sortBy, sortOrder]);

  async function loadReferenceData() {
    try {
      const [candidatesRes, vacanciesRes] = await Promise.all([
        getCandidates({ limit: 200 }),
        getVacancies({ limit: 200 }),
      ]);
      setCandidates(candidatesRes.items);
      setVacancies(vacanciesRes.items);
    } catch (err) {
      console.error('Failed to load reference data:', err);
    }
  }

  async function loadOffers() {
    setLoading(true);
    try {
      const params: any = {
        limit: pagination.limit,
        offset: pagination.offset,
      };
      if (filters.candidate_id !== 'all') params.candidate_id = filters.candidate_id;
      if (filters.vacancy_id !== 'all') params.vacancy_id = filters.vacancy_id;
      if (filters.status !== 'all') params.status = filters.status;
      if (filters.salaryFrom) params.salary_from = Number(filters.salaryFrom);
      if (filters.salaryTo) params.salary_to = Number(filters.salaryTo);
      if (filters.createdFrom) {
        params.created_at_from = Math.floor(new Date(filters.createdFrom).getTime() / 1000);
      }
      if (filters.createdTo) {
        params.created_at_to = Math.floor(new Date(filters.createdTo).getTime() / 1000);
      }
      if (sortBy) {
        params.sort_by = sortBy;
        params.sort_order = sortOrder;
      }
      const response = await getOffers(params);
      setOffers(response.items);
      setTotal(response.total);
    } catch (err) {
      toast.error('Ошибка загрузки офферов');
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

  const handleSortChange = (newSortBy: string, newSortOrder: 'asc' | 'desc') => {
    setSortBy(newSortBy);
    setSortOrder(newSortOrder);
    setPagination(prev => ({ ...prev, offset: 0 }));
  };

  const handleSelectAll = (checked: boolean) => {
    setSelectedOffers(checked ? offers.map(o => o.id) : []);
  };

  const handleSelectOne = (id: string, checked: boolean) => {
    setSelectedOffers(prev => (checked ? [...prev, id] : prev.filter(x => x !== id)));
  };

  const handleBulkDelete = async () => {
    if (!permissions.canDeleteOffer) {
      toast.error('У вас нет прав на удаление офферов');
      return;
    }
    if (!window.confirm(`Удалить ${selectedOffers.length} офферов?`)) return;
    try {
      await Promise.all(selectedOffers.map(id => deleteOffer(id)));
      toast.success('Офферы удалены');
      setSelectedOffers([]);
      loadOffers();
    } catch (err) {
      toast.error('Ошибка при удалении');
    }
  };

  const filterFields: FilterField[] = useMemo(() => {
    const candidateOptions = candidates.map(c => ({ value: c.id, label: c.full_name }));
    const vacancyOptions = vacancies.map(v => ({ value: v.id, label: v.title }));
    return [
      { key: 'candidate_id', label: 'Кандидат', type: 'select', options: candidateOptions },
      { key: 'vacancy_id', label: 'Вакансия', type: 'select', options: vacancyOptions },
      { key: 'status', label: 'Статус', type: 'select', options: [
        { value: 'PENDING', label: 'Ожидает' },
        { value: 'APPROVED_MNG', label: 'Согласован менеджером' },
        { value: 'REJECTED_MNG', label: 'Отклонён менеджером' },
        { value: 'APPROVED_CND', label: 'Принят кандидатом' },
        { value: 'REJECTED_CNF', label: 'Отклонён кандидатом' },
      ] },
      { key: 'salaryFrom', label: 'Зарплата от', type: 'number', placeholder: '0' },
      { key: 'salaryTo', label: 'Зарплата до', type: 'number', placeholder: '0' },
      { key: 'createdFrom', label: 'Создан с', type: 'date' },
      { key: 'createdTo', label: 'Создан по', type: 'date' },
    ];
  }, [candidates, vacancies]);

  const sortableFields = [
    { value: 'salary', label: 'Зарплата' },
    { value: 'start_at', label: 'Дата выхода' },
    { value: 'status', label: 'Статус' },
    { value: 'created_at', label: 'Дата создания' },
    { value: 'candidate_name', label: 'Кандидат' },
    { value: 'vacancy_title', label: 'Вакансия' },
  ];

  const getStatusLabel = (status: string): string => {
    const statusMap: Record<string, string> = {
      PENDING: 'Ожидает',
      APPROVED_MNG: 'Согласован менеджером',
      REJECTED_MNG: 'Отклонён менеджером',
      APPROVED_CND: 'Принят кандидатом',
      REJECTED_CNF: 'Отклонён кандидатом',
    };
    return statusMap[status] || status;
  };

  const getStatusBadgeClass = (status: string): string => {
    const classMap: Record<string, string> = {
      PENDING: 'badge-warning',
      APPROVED_MNG: 'badge-success',
      REJECTED_MNG: 'badge-danger',
      APPROVED_CND: 'badge-success',
      REJECTED_CNF: 'badge-danger',
    };
    return classMap[status] || 'badge';
  };

  const columns: Column<Offer>[] = [
    { key: 'candidate_id', header: 'Кандидат', render: o => candidates.find(c => c.id === o.candidate_id)?.full_name || '—' },
    { key: 'vacancy_id', header: 'Вакансия', render: o => vacancies.find(v => v.id === o.vacancy_id)?.title || '—' },
    { key: 'salary', header: 'Зарплата', render: o => `${o.salary.toLocaleString('ru-RU')} ₽` },
    { key: 'start_at', header: 'Дата выхода', render: o => new Date(o.start_at * 1000).toLocaleDateString('ru-RU') },
    { key: 'status', header: 'Статус', render: o => <span className={`badge ${getStatusBadgeClass(o.status)}`}>{getStatusLabel(o.status)}</span> },
    { key: 'created_at', header: 'Создан', render: o => o.created_at ? new Date(o.created_at * 1000).toLocaleDateString('ru-RU') : '—' },
  ];

  const totalPages = Math.ceil(total / pagination.limit);
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;

  return (
    <div className="content">
      <div className="page-header">
        <h2>Офферы {total > 0 && `(${total})`}</h2>
        <div className="btn-group">
          {selectedOffers.length > 0 && permissions.canDeleteOffer && (
            <button className="btn btn-danger" onClick={handleBulkDelete}>
              🗑️ Удалить ({selectedOffers.length})
            </button>
          )}
          <button className="btn" onClick={() => setShowFilters(!showFilters)}>
            🔍 Фильтры {hasActiveFilters && '●'}
          </button>
          {permissions.canCreateOffer && (
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
              ➕ Создать оффер
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
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={handleSortChange}
        sortableFields={sortableFields}
      />

      {loading ? (
        <div>Загрузка...</div>
      ) : (
        <>
          <DataTable
            columns={columns}
            data={offers}
            keyExtractor={o => o.id}
            selectedIds={selectedOffers}
            onSelect={handleSelectOne}
            onSelectAll={handleSelectAll}
            emptyMessage="Нет офферов"
            actions={o => (
              <button className="btn btn-sm" onClick={() => navigate(`/offers/${o.id}`)} title="Просмотр деталей">
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
            <CreateOfferForm
              onSuccess={() => {
                setShowModal(false);
                setPagination({ limit: 20, offset: 0 });
                loadOffers();
              }}
              onCancel={() => setShowModal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
