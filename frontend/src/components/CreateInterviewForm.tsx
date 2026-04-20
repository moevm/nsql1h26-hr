import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { createInterview, getCandidates, getVacancies, getUsers, Candidate, Vacancy, User } from '../api';

interface CreateInterviewFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export function CreateInterviewForm({ onSuccess, onCancel }: CreateInterviewFormProps) {
  const [candidateId, setCandidateId] = useState('');
  const [vacancyId, setVacancyId] = useState('');
  const [techSpecId, setTechSpecId] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [zoomUrl, setZoomUrl] = useState('');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [techSpecs, setTechSpecs] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [candidatesRes, vacanciesRes, usersRes] = await Promise.all([
        getCandidates({ status: 'TEST', limit: 100 }), // Только кандидаты в статусе TEST
        getVacancies({ status: 'OPEN', limit: 100 }), // Только открытые вакансии
        getUsers({ role: 'TECH_SPEC', limit: 100 }),
      ]);
      setCandidates(candidatesRes.items);
      setVacancies(vacanciesRes.items);
      setTechSpecs(usersRes.items);
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
    if (!techSpecId) {
      toast.error('Выберите технического специалиста');
      return;
    }
    if (!scheduledAt) {
      toast.error('Укажите дату и время интервью');
      return;
    }

    setLoading(true);
    
    try {
      await createInterview({
        candidate_id: candidateId,
        tech_spec_id: techSpecId,
        scheduled_at: Math.floor(new Date(scheduledAt).getTime() / 1000),
        zoom_url: zoomUrl || undefined,
      });
      toast.success('Интервью успешно запланировано');
      onSuccess();
    } catch (err: any) {
      console.error(err);
      if (err.message?.includes('400')) {
        toast.error('Кандидат не в статусе TEST или технический специалист не найден');
      } else {
        toast.error('Ошибка при создании интервью');
      }
    } finally {
      setLoading(false);
    }
  };

  const selectedCandidate = candidates.find(c => c.id === candidateId);
  const selectedVacancy = vacancies.find(v => v.id === vacancyId);

  // Минимальная дата и время — сейчас + 1 час
  const getMinDateTime = () => {
    const now = new Date();
    now.setHours(now.getHours() + 1);
    return now.toISOString().slice(0, 16);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="modal-header">
        <h3>Запланировать интервью</h3>
        <p>Выберите кандидата, вакансию и интервьюера</p>
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
            Нет кандидатов в статусе TEST
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
              {v.title}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Технический специалист *</label>
        <select 
          value={techSpecId} 
          onChange={e => setTechSpecId(e.target.value)} 
          required 
          disabled={loading || loadingData}
        >
          <option value="">Выберите специалиста</option>
          {techSpecs.map(t => (
            <option key={t.id} value={t.id}>{t.full_name} — {t.email}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Дата и время *</label>
        <input 
          type="datetime-local" 
          value={scheduledAt} 
          onChange={e => setScheduledAt(e.target.value)} 
          required 
          disabled={loading}
          min={getMinDateTime()}
        />
        <small style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>
          Время указано по местному времени
        </small>
      </div>

      <div className="form-group">
        <label>Ссылка на Zoom (опционально)</label>
        <input 
          type="url" 
          value={zoomUrl} 
          onChange={e => setZoomUrl(e.target.value)} 
          placeholder="https://zoom.us/j/..."
          disabled={loading}
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
            📋 Интервью для <strong>{selectedCandidate.full_name}</strong> на позицию <strong>{selectedVacancy.title}</strong>
          </small>
        </div>
      )}
      
      <div className="form-actions" style={{ marginTop: '20px' }}>
        <button type="button" className="btn" onClick={onCancel} disabled={loading}>
          Отмена
        </button>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Создание...' : 'Запланировать интервью'}
        </button>
      </div>
    </form>
  );
}
