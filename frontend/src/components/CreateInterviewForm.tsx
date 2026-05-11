import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { createInterview, getCandidates, getUsers, Candidate, User } from '../api';

interface CreateInterviewFormProps {
  onSuccess: () => void;
  onCancel: () => void;
  preselectedCandidate?: Candidate; // если передан – кандидат фиксирован
}

export function CreateInterviewForm({ onSuccess, onCancel, preselectedCandidate }: CreateInterviewFormProps) {
  const [candidateId, setCandidateId] = useState(preselectedCandidate?.id || '');
  const [techSpecId, setTechSpecId] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [zoomUrl, setZoomUrl] = useState('');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [techSpecs, setTechSpecs] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const promises = [];
      if (!preselectedCandidate) {
        promises.push(getCandidates({ limit: 200 }));
      } else {
        promises.push(Promise.resolve({ items: [] }));
      }
      promises.push(getUsers({ role: 'TECH_SPEC', limit: 200 }));

      const [candidatesRes, usersRes] = await Promise.all(promises);
      if (!preselectedCandidate) setCandidates(candidatesRes.items);
      setTechSpecs(usersRes.items);
    } catch (err) {
      console.error(err);
      toast.error('Не удалось загрузить данные');
    } finally {
      setLoadingData(false);
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const finalCandidateId = preselectedCandidate?.id || candidateId;
    if (!finalCandidateId) return toast.error('Выберите кандидата');
    if (!techSpecId) return toast.error('Выберите технического специалиста');
    if (!scheduledAt) return toast.error('Укажите дату и время');

    setLoading(true);
    try {
      await createInterview({
        candidate_id: finalCandidateId,
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

  const getMinDateTime = () => {
    const now = new Date();
    now.setHours(now.getHours() + 1);
    return now.toISOString().slice(0, 16);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="modal-header">
        <h3>Запланировать интервью</h3>
      </div>

      {/* Блок выбора/информации о кандидате */}
      {!preselectedCandidate ? (
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
              <option key={c.id} value={c.id}>{c.full_name}</option>
            ))}
          </select>
          {loadingData && <small>Загрузка кандидатов...</small>}
        </div>
      ) : (
        <div className="info-box" style={{ background: '#f0fdf4', padding: '12px', borderRadius: '8px', marginBottom: '16px', border: '1px solid #bbf7d0' }}>
          <strong>Кандидат:</strong> {preselectedCandidate.full_name}
        </div>
      )}

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

      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel} disabled={loading}>Отмена</button>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Создание...' : 'Запланировать интервью'}
        </button>
      </div>
    </form>
  );
}
