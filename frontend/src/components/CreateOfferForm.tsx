import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { createOffer, getCandidates, getVacancies, Candidate, Vacancy } from '../api';

interface CreateOfferFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export function CreateOfferForm({ onSuccess, onCancel }: CreateOfferFormProps) {
  const [candidateId, setCandidateId] = useState('');
  const [vacancyId, setVacancyId] = useState('');
  const [salary, setSalary] = useState('');
  const [startDate, setStartDate] = useState('');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);

  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [candidatesRes, vacanciesRes] = await Promise.all([
        getCandidates({ status: 'INTERVIEW', limit: 100 }),
        getVacancies({ status: 'OPEN', limit: 100 }),
      ]);
      setCandidates(candidatesRes.items);
      setVacancies(vacanciesRes.items);
    } catch (err) {
      console.error('Failed to load data:', err);
      toast.error('Не удалось загрузить данные');
    } finally {
      setLoadingData(false);
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!candidateId) {
      toast.error('Выберите кандидата');
      return;
    }
    if (!vacancyId) {
      toast.error('Выберите вакансию');
      return;
    }
    if (!salary) {
      toast.error('Укажите зарплату');
      return;
    }
    if (!startDate) {
      toast.error('Укажите дату выхода');
      return;
    }
    if (!user.id) {
      toast.error('Не удалось определить текущего пользователя');
      return;
    }

    setLoading(true);
    
    try {
      await createOffer({
        candidate_id: candidateId,
        vacancy_id: vacancyId,
        created_by: user.id,
        salary: Number(salary),
        start_at: Math.floor(new Date(startDate).getTime() / 1000),
      });
      toast.success('Оффер успешно создан');
      onSuccess();
    } catch (err: any) {
      console.error(err);
      if (err.message?.includes('400')) {
        toast.error('Кандидат не в статусе INTERVIEW или уже есть активный оффер');
      } else if (err.message?.includes('404')) {
        toast.error('Кандидат или вакансия не найдены');
      } else {
        toast.error('Ошибка при создании оффера');
      }
    } finally {
      setLoading(false);
    }
  };

  const selectedCandidate = candidates.find(c => c.id === candidateId);
  const selectedVacancy = vacancies.find(v => v.id === vacancyId);

  // Минимальная дата выхода — сегодня
  const minDate = new Date().toISOString().split('T')[0];

  return (
    <form onSubmit={handleSubmit}>
      <div className="modal-header">
        <h3>Новый оффер</h3>
        <p>Заполните данные оффера</p>
      </div>

      <div className="form-group">
        <label>Кандидат *</label>
        <select 
          value={candidateId} 
          onChange={e => setCandidateId(e.target.value)} 
          required 
          disabled={loading || loadingData}
        >
          <option value="">Выберите кандидата</option>
          {candidates.map(c => (
            <option key={c.id} value={c.id}>
              {c.full_name} — {c.status}
            </option>
          ))}
        </select>
        {loadingData && <small>Загрузка кандидатов...</small>}
        {candidates.length === 0 && !loadingData && (
          <small style={{ color: '#eab308' }}>
            Нет кандидатов в статусе INTERVIEW
          </small>
        )}
      </div>

      <div className="form-group">
        <label>Вакансия *</label>
        <select 
          value={vacancyId} 
          onChange={e => setVacancyId(e.target.value)} 
          required 
          disabled={loading || loadingData}
        >
          <option value="">Выберите вакансию</option>
          {vacancies.map(v => (
            <option key={v.id} value={v.id}>
              {v.title} — {v.status === 'OPEN' ? 'Открыта' : 'Закрыта'}
            </option>
          ))}
        </select>
        {vacancies.length === 0 && !loadingData && (
          <small style={{ color: '#eab308' }}>
            Нет открытых вакансий
          </small>
        )}
      </div>

      <div className="form-group">
        <label>Зарплата (₽) *</label>
        <input 
          type="number" 
          value={salary} 
          onChange={e => setSalary(e.target.value)} 
          required 
          disabled={loading}
          min="0"
          step="1000"
          placeholder="100000"
        />
      </div>

      <div className="form-group">
        <label>Дата выхода *</label>
        <input 
          type="date" 
          value={startDate} 
          onChange={e => setStartDate(e.target.value)} 
          required 
          disabled={loading}
          min={minDate}
        />
      </div>
      
      {selectedCandidate && selectedVacancy && (
        <div className="info-box" style={{ 
          background: '#f0fdf4', 
          padding: '12px', 
          borderRadius: '8px', 
          marginTop: '12px',
          border: '1px solid #bbf7d0'
        }}>
          <small style={{ color: '#166534' }}>
            📋 Создание оффера для <strong>{selectedCandidate.full_name}</strong> на позицию <strong>{selectedVacancy.title}</strong>
          </small>
        </div>
      )}
      
      <div className="form-actions" style={{ marginTop: '20px' }}>
        <button type="button" className="btn" onClick={onCancel} disabled={loading}>
          Отмена
        </button>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Создание...' : 'Создать оффер'}
        </button>
      </div>
    </form>
  );
}
