// CreateVacancyForm.tsx
import { useState } from 'react';
import { toast } from 'sonner';
import { createVacancy, updateVacancy, Vacancy } from '../api';

interface CreateVacancyFormProps {
  onSuccess: () => void;
  onCancel: () => void;
  initialData?: Vacancy;
}

export function CreateVacancyForm({ onSuccess, onCancel, initialData }: CreateVacancyFormProps) {
  const isEdit = !!initialData;
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [status, setStatus] = useState<'OPEN' | 'CLOSED'>(initialData?.status || 'OPEN');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isEdit && initialData) {
        await updateVacancy(initialData.id, { title, description, status });
        toast.success('Вакансия обновлена');
      } else {
        await createVacancy({ title, description });
        toast.success('Вакансия создана');
      }
      onSuccess();
    } catch (err) {
      toast.error(isEdit ? 'Ошибка обновления' : 'Ошибка создания');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label>Название</label>
        <input type="text" value={title} onChange={e => setTitle(e.target.value)} required disabled={loading} />
      </div>
      <div className="form-group">
        <label>Описание</label>
        <textarea rows={4} value={description} onChange={e => setDescription(e.target.value)} required disabled={loading} />
      </div>
      <div className="form-group">
        <label>Статус</label>
        <select value={status} onChange={e => setStatus(e.target.value as any)} disabled={loading}>
          <option value="OPEN">Открыта</option>
          <option value="CLOSED">Закрыта</option>
        </select>
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
