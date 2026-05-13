import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { createOffer, updateOfferAdmin, getCandidates, getCandidateById, getVacancies, getVacancyById, Candidate, Vacancy, Offer } from '../api';

interface CreateOfferFormProps {
  onSuccess: () => void;
  onCancel: () => void;
  preselectedCandidate?: Candidate;
  initialData?: Offer;
}

export function CreateOfferForm({ onSuccess, onCancel, preselectedCandidate, initialData }: CreateOfferFormProps) {
  const isEdit = !!initialData;
  const [candidateId, setCandidateId] = useState(initialData?.candidate_id || preselectedCandidate?.id || '');
  const [candidateName, setCandidateName] = useState(preselectedCandidate?.full_name || '');
  const [vacancyTitle, setVacancyTitle] = useState('');
  const [salary, setSalary] = useState(initialData?.salary?.toString() || '');
  const [startDate, setStartDate] = useState(
    initialData?.start_at
      ? new Date(initialData.start_at * 1000).toISOString().split('T')[0]
      : ''
  );
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      if (!preselectedCandidate && !isEdit) {
        const candidatesRes = await getCandidates({ status: 'INTERVIEW_PASSED', limit: 100 });
        setCandidates(candidatesRes.items);
      }
      if (isEdit && candidateId) {
        const [cand, vac] = await Promise.all([
          getCandidateById(candidateId),
          getVacancyById(initialData!.vacancy_id)
        ]);
        setCandidateName(cand.full_name);
        setVacancyTitle(vac.title);
      }
      if (preselectedCandidate && !isEdit) {
        const vac = await getVacancyById(preselectedCandidate.vacancy_id);
        setVacancyTitle(vac.title);
      }
    } catch (err) {
      console.error(err);
      toast.error('Не удалось загрузить данные');
    } finally {
      setLoadingData(false);
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!candidateId) return toast.error('Выберите кандидата');
    if (!salary) return toast.error('Укажите зарплату');
    if (!startDate) return toast.error('Укажите дату выхода');

    setLoading(true);
    try {
      if (isEdit && initialData) {
        await updateOfferAdmin(initialData.id, {
          salary: Number(salary),
          start_at: Math.floor(new Date(startDate).getTime() / 1000),
        });
        toast.success('Оффер обновлён');
      } else {
        const selectedCandidate = preselectedCandidate || candidates.find(c => c.id === candidateId);
        if (!selectedCandidate) throw new Error('Кандидат не найден');
        if (!user.id) return toast.error('Не удалось определить текущего пользователя');

        await createOffer({
          candidate_id: selectedCandidate.id,
          vacancy_id: selectedCandidate.vacancy_id,
          created_by: user.id,
          salary: Number(salary),
          start_at: Math.floor(new Date(startDate).getTime() / 1000),
        });
        toast.success('Оффер успешно создан');
      }
      onSuccess();
    } catch (err: any) {
      console.error(err);
      toast.error(isEdit ? 'Ошибка обновления' : 'Ошибка при создании оффера');
    } finally {
      setLoading(false);
    }
  };

  const minDate = new Date().toISOString().split('T')[0];

  return (
    <form onSubmit={handleSubmit}>
      <div className="modal-header">
        <h3>{isEdit ? 'Редактирование оффера' : 'Новый оффер'}</h3>
        {!isEdit && <p>Кандидат уже привязан к вакансии, её не нужно выбирать</p>}
      </div>

      {(!preselectedCandidate && !isEdit) ? (
        <div className="form-group">
          <label>Кандидат *</label>
          <select value={candidateId} onChange={e => setCandidateId(e.target.value)} required disabled={loading || loadingData}>
            <option value="">Выберите кандидата</option>
            {candidates.map(c => (
              <option key={c.id} value={c.id}>{c.full_name}</option>
            ))}
          </select>
          {candidates.length === 0 && !loadingData && (
            <small style={{ color: '#eab308' }}>Нет кандидатов со статусом INTERVIEW_PASSED</small>
          )}
        </div>
      ) : (preselectedCandidate || isEdit) && (
        <div style={{ background: '#f0fdf4', padding: '12px', borderRadius: '8px', marginBottom: '16px', border: '1px solid #bbf7d0' }}>
          <div><strong>Кандидат:</strong> {preselectedCandidate?.full_name || candidateName}</div>
          <div><strong>Вакансия:</strong> {vacancyTitle || '—'}</div>
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
          {loading ? (isEdit ? 'Сохранение...' : 'Создание...') : (isEdit ? 'Сохранить' : 'Создать')}
        </button>
      </div>
    </form>
  );
}
