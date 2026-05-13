import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { createInterview, updateInterviewAdmin, getCandidates, getCandidateById, getUsers, Candidate, User, Interview } from '../api';

function formatLocalDatetime(timestamp: number | undefined): string {
  if (!timestamp) return '';
  const date = new Date(timestamp * 1000);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// Всё остальное (handleSubmit, getMinDateTime и т.д.) остаётся без изменений.

interface CreateInterviewFormProps {
  onSuccess: () => void;
  onCancel: () => void;
  preselectedCandidate?: Candidate;
  initialData?: Interview;
}

export function CreateInterviewForm({ onSuccess, onCancel, preselectedCandidate, initialData }: CreateInterviewFormProps) {
  const isEdit = !!initialData;
  const [candidateId, setCandidateId] = useState(initialData?.candidate_id || preselectedCandidate?.id || '');
  const [candidateName, setCandidateName] = useState(preselectedCandidate?.full_name || '');
  const [techSpecId, setTechSpecId] = useState(initialData?.tech_spec_id || '');
  const [scheduledAt, setScheduledAt] = useState(
  initialData?.scheduled_at ? formatLocalDatetime(initialData.scheduled_at) : ''
  );

  const [zoomUrl, setZoomUrl] = useState(initialData?.zoom_url || '');
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
      if (!preselectedCandidate && !isEdit) {
        promises.push(getCandidates({ limit: 200 }));
      } else {
        promises.push(Promise.resolve({ items: [] }));
      }
      promises.push(getUsers({ role: 'TECH_SPEC', limit: 200 }));

      const [candidatesRes, usersRes] = await Promise.all(promises);
      if (!preselectedCandidate && !isEdit) setCandidates(candidatesRes.items);
      setTechSpecs(usersRes.items);

      if (isEdit && candidateId) {
        const cand = await getCandidateById(candidateId);
        setCandidateName(cand.full_name);
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
    const finalCandidateId = candidateId;
    if (!finalCandidateId) return toast.error('Кандидат не выбран');
    if (!techSpecId) return toast.error('Выберите технического специалиста');
    if (!scheduledAt) return toast.error('Укажите дату и время');

    setLoading(true);
    try {
      if (isEdit && initialData) {
        await updateInterviewAdmin(initialData.id, {
          tech_spec_id: techSpecId,
          scheduled_at: Math.floor(new Date(scheduledAt).getTime() / 1000),
          zoom_url: zoomUrl || undefined,
        });
        toast.success('Интервью обновлено');
      } else {
        await createInterview({
          candidate_id: finalCandidateId,
          tech_spec_id: techSpecId,
          scheduled_at: Math.floor(new Date(scheduledAt).getTime() / 1000),
          zoom_url: zoomUrl || undefined,
        });
        toast.success('Интервью успешно запланировано');
      }
      onSuccess();
    } catch (err: any) {
      console.error(err);
      toast.error(isEdit ? 'Ошибка обновления' : 'Ошибка при создании интервью');
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
        <h3>{isEdit ? 'Редактирование интервью' : 'Запланировать интервью'}</h3>
      </div>

      {!preselectedCandidate && !isEdit ? (
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
      ) : ((preselectedCandidate && !isEdit) || isEdit) && (
        <div className="info-box" style={{ background: '#f0fdf4', padding: '12px', borderRadius: '8px', marginBottom: '16px', border: '1px solid #bbf7d0' }}>
          <strong>Кандидат:</strong> {preselectedCandidate?.full_name || candidateName}
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
          {loading ? (isEdit ? 'Сохранение...' : 'Создание...') : (isEdit ? 'Сохранить' : 'Запланировать')}
        </button>
      </div>
    </form>
  );
}
