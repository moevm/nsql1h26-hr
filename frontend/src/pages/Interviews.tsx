import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { DataTable, Column } from '../components/DataTable';
import { CreateInterviewForm } from '../components/CreateInterviewForm';
import { FilterBar } from '../components/FilterBar';
import { useFilters } from '../hooks/useFilters';
import { FilterField } from '../types/filters';
import { toast } from 'sonner';
import { getInterviews, deleteInterview, getCandidates, getVacancies, getUsers, Interview, Candidate, Vacancy, User } from '../api';
import { usePermissions } from '../hooks/usePermissions';
import '../styles/App.css';

export function Interviews() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const permissions = usePermissions(user?.role);

  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [techSpecs, setTechSpecs] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [pagination, setPagination] = useState({ limit: 20, offset: 0 });
  const [showFilters, setShowFilters] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedInterviews, setSelectedInterviews] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<string>('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const { filters, updateFilter, clearFilters, hasActiveFilters } = useFilters({
    candidate_id: 'all',
    vacancy_id: 'all',
    tech_spec_id: 'all',
    dateFrom: '',
    dateTo: '',
    result: 'all',
  });

  useEffect(() => {
    loadReferenceData();
  }, []);

  useEffect(() => {
    loadInterviews();
  }, [filters, pagination, sortBy, sortOrder]);

  async function loadReferenceData() {
    try {
      const [candidatesRes, vacanciesRes, usersRes] = await Promise.all([
        getCandidates({ limit: 200 }),
        getVacancies({ limit: 200 }),
        getUsers({ role: 'TECH_SPEC', limit: 200 }),
      ]);
      setCandidates(candidatesRes.items);
      setVacancies(vacanciesRes.items);
      setTechSpecs(usersRes.items);
    } catch (err) {
      console.error('Failed to load reference data:', err);
    }
  }

  async function loadInterviews() {
    setLoading(true);
    try {
      const params: any = {
        limit: pagination.limit,
        offset: pagination.offset,
      };
      if (filters.candidate_id !== 'all') params.candidate_id = filters.candidate_id;
      if (filters.vacancy_id !== 'all') params.vacancy_id = filters.vacancy_id;
      if (filters.tech_spec_id !== 'all') params.tech_spec_id = filters.tech_spec_id;
      if (filters.dateFrom) {
        params.scheduled_at_from = Math.floor(new Date(filters.dateFrom).getTime() / 1000);
      }
      if (filters.dateTo) {
        params.scheduled_at_to = Math.floor(new Date(filters.dateTo).getTime() / 1000);
      }
      if (filters.result !== 'all') params.result = filters.result;
      if (sortBy) {
        params.sort_by = sortBy;
        params.sort_order = sortOrder;
      }
      const response = await getInterviews(params);
      setInterviews(response.items);
      setTotal(response.total);
    } catch (err) {
      toast.error('Ошибка загрузки интервью');
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
    setSelectedInterviews(checked ? interviews.map(i => i.id) : []);
  };

  const handleSelectOne = (id: string, checked: boolean) => {
    setSelectedInterviews(prev => (checked ? [...prev, id] : prev.filter(x => x !== id)));
  };

  const handleBulkDelete = async () => {
    if (!permissions.canDeleteInterview) {
      toast.error('У вас нет прав на удаление интервью');
      return;
    }
    if (!window.confirm(`Удалить ${selectedInterviews.length} интервью?`)) return;
    try {
      await Promise.all(selectedInterviews.map(id => deleteInterview(id)));
      toast.success('Интервью удалены');
      setSelectedInterviews([]);
      loadInterviews();
    } catch (err) {
      toast.error('Ошибка при удалении');
    }
  };

  const filterFields: FilterField[] = useMemo(() => {
    const candidateOptions = candidates.map(c => ({ value: c.id, label: c.full_name }));
    const vacancyOptions = vacancies.map(v => ({ value: v.id, label: v.title }));
    const techSpecOptions = techSpecs.map(t => ({ value: t.id, label: t.full_name }));
    return [
      { key: 'candidate_id', label: 'Кандидат', type: 'select', options: candidateOptions },
      { key: 'vacancy_id', label: 'Вакансия', type: 'select', options: vacancyOptions },
      { key: 'tech_spec_id', label: 'Интервьюер', type: 'select', options: techSpecOptions },
      { key: 'dateFrom', label: 'Дата с', type: 'datetime-local' },
      { key: 'dateTo', label: 'Дата по', type: 'datetime-local' },
      { key: 'result', label: 'Результат', type: 'select', options: [
        { value: 'AWAIT_INTERVIEW', label: 'Ожидает' },
        { value: 'INTERVIEW_PASSED', label: 'Пройдено' },
        { value: 'INTERVIEW_FAILED', label: 'Не пройдено' },
      ] },
    ];
  }, [candidates, vacancies, techSpecs]);

  const sortableFields = [
    { value: 'scheduled_at', label: 'Дата интервью' },
    { value: 'result', label: 'Результат' },
    { value: 'candidate_name', label: 'Кандидат' },
    { value: 'tech_spec_name', label: 'Интервьюер' },
  ];

  const getResultLabel = (result: string): string => {
    const resultMap: Record<string, string> = {
      AWAIT_INTERVIEW: 'Ожидается',
      INTERVIEW_PASSED: 'Пройдено',
      INTERVIEW_FAILED: 'Не пройдено',
    };
    return resultMap[result] || result;
  };

  const getResultBadgeClass = (result: string): string => {
    const classMap: Record<string, string> = {
      AWAIT_INTERVIEW: 'badge-warning',
      INTERVIEW_PASSED: 'badge-success',
      INTERVIEW_FAILED: 'badge-danger',
    };
    return classMap[result] || 'badge';
  };

  const columns: Column<Interview>[] = [
    { key: 'candidate_id', header: 'Кандидат', render: i => candidates.find(c => c.id === i.candidate_id)?.full_name || '—' },
    {
      key: 'vacancy_id',
      header: 'Вакансия',
      render: i => {
        const candidate = candidates.find(c => c.id === i.candidate_id);
        const vacancy = candidate && vacancies.find(v => v.id === candidate.vacancy_id);
        return vacancy?.title || '—';
      },
    },
    { key: 'tech_spec_id', header: 'Интервьюер', render: i => techSpecs.find(t => t.id === i.tech_spec_id)?.full_name || '—' },
    { key: 'scheduled_at', header: 'Дата и время', render: i => new Date(i.scheduled_at * 1000).toLocaleString('ru-RU') },
    { key: 'result', header: 'Результат', render: i => <span className={`badge ${getResultBadgeClass(i.result)}`}>{getResultLabel(i.result)}</span> },
    { key: 'feedback', header: 'Фидбек', render: i => i.feedback ? (i.feedback.length > 100 ? i.feedback.slice(0, 100) + '…' : i.feedback) : '—', className: 'max-w-xs' },
  ];

  const totalPages = Math.ceil(total / pagination.limit);
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;

  return (
    <div className="content">
      <div className="page-header">
        <h2>Интервью {total > 0 && `(${total})`}</h2>
        <div className="btn-group">
          {selectedInterviews.length > 0 && permissions.canDeleteInterview && (
            <button className="btn btn-danger" onClick={handleBulkDelete}>
              🗑️ Удалить ({selectedInterviews.length})
            </button>
          )}
          <button className="btn" onClick={() => setShowFilters(!showFilters)}>
            🔍 Фильтры {hasActiveFilters && '●'}
          </button>
          {permissions.canCreateInterview && (
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
              ➕ Запланировать интервью
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
            data={interviews}
            keyExtractor={i => i.id}
            selectedIds={selectedInterviews}
            onSelect={handleSelectOne}
            onSelectAll={handleSelectAll}
            emptyMessage="Нет интервью"
            actions={i => (
              <button className="btn btn-sm" onClick={() => navigate(`/interviews/${i.id}`)} title="Просмотр деталей">
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
            <CreateInterviewForm
              onSuccess={() => {
                setShowModal(false);
                setPagination({ limit: 20, offset: 0 });
                loadInterviews();
              }}
              onCancel={() => setShowModal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
