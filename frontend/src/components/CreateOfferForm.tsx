import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { createOffer, getCandidates, getVacancies, Candidate, Vacancy } from '../api';

interface CreateOfferFormProps {
  onSuccess: () => void;
  onCancel: () => void;
  preselectedCandidate?: Candidate; // если передан – кандидат фиксирован, выбор скрыт
}

export function CreateOfferForm({ onSuccess, onCancel, preselectedCandidate }: CreateOfferFormProps) {
  const [candidateId, setCandidateId] = useState(preselectedCandidate?.id || '');
  const [salary, setSalary] = useState('');
  const [startDate, setStartDate] = useState('');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    if (!preselectedCandidate) {
      loadCandidates();
    } else {
      setLoadingData(false);
    }
  }, []);

  async function loadCandidates() {
    try {
      const candidatesRes = await getCandidates({ status: 'INTERVIEW_PASSED', limit: 100 });
      setCandidates(candidatesRes.items);
    } catch (err) {
      console.error(err);
      toast.error('Не удалось загрузить кандидатов');
    } finally {
      setLoadingData(false);
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!candidateId) return toast.error('Выберите кандидата');
    if (!salary) return toast.error('Укажите зарплату');
    if (!startDate) return toast.error('Укажите дату выхода');
    if (!user.id) return toast.error('Не удалось определить текущего пользователя');

    setLoading(true);
    try {
      const selectedCandidate = preselectedCandidate || candidates.find(c => c.id === candidateId);
      if (!selectedCandidate) throw new Error('Кандидат не найден');

      await createOffer({
        candidate_id: selectedCandidate.id,
        vacancy_id: selectedCandidate.vacancy_id, // берём вакансию из кандидата
        created_by: user.id,
        salary: Number(salary),
        start_at: Math.floor(new Date(startDate).getTime() / 1000),
      });
      toast.success('Оффер успешно создан');
      onSuccess();
    } catch (err: any) {
      console.error(err);
      toast.error('Ошибка при создании оффера');
    } finally {
      setLoading(false);
    }
  };

  const minDate = new Date().toISOString().split('T')[0];

  return (
    <form onSubmit={handleSubmit}>
      <div className="modal-header">
        <h3>Новый оффер</h3>
        <p>Кандидат уже привязан к вакансии, её не нужно выбирать</p>
      </div>

      {preselectedCandidate ? (
        <div style={{ background: '#f0fdf4', padding: '12px', borderRadius: '8px', marginBottom: '16px', border: '1px solid #bbf7d0' }}>
          <div><strong>Кандидат:</strong> {preselectedCandidate.full_name}</div>
          <div><strong>Вакансия:</strong> {preselectedCandidate.vacancy_id} (ID)</div>
        </div>
      ) : (
        <div className="form-group">
          <label>Кандидат *</label>
          <select value={candidateId} onChange={e => setCandidateId(e.target.value)} required disabled={loading || loadingData}>
            <option value="">Выберите кандидата</option>
            {candidates.map(c => (
              <option key={c.id} value={c.id}>
                {c.full_name}
              </option>
            ))}
          </select>
          {candidates.length === 0 && !loadingData && (
            <small style={{ color: '#eab308' }}>Нет кандидатов со статусом INTERVIEW_PASSED</small>
          )}
        </div>
      )}

      <div className="form-group">
        <label>Зарплата (₽) *</label>
        <input type="number" value={salary} onChange={e => setSalary(e.target.value)} required disabled={loading} min="0" step="1000" placeholder="100000" />
      </div>

      <div className="form-group">
        <label>Дата выхода *</label>
        <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} required disabled={loading} min={minDate} />
      </div>

      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel} disabled={loading}>Отмена</button>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Создание...' : 'Создать оффер'}
        </button>
      </div>
    </form>
  );
}
