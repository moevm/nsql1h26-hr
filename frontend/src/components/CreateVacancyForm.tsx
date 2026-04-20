import { useState } from 'react';
import { toast } from 'sonner';
import { createVacancy } from '../api';

export function CreateVacancyForm({ onSuccess }: { onSuccess: () => void }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<'OPEN' | 'CLOSED'>('OPEN');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await createVacancy({ title, description });
      toast.success('Вакансия успешно создана');
      onSuccess();
    } catch (err) {
      toast.error('Ошибка при создании вакансии');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label>Название</label>
        <input 
          type="text" 
          value={title} 
          onChange={e => setTitle(e.target.value)} 
          required 
          disabled={loading}
        />
      </div>
      <div className="form-group">
        <label>Описание</label>
        <textarea 
          rows={3} 
          value={description} 
          onChange={e => setDescription(e.target.value)} 
          required
          disabled={loading}
        />
      </div>
      <div className="form-group">
        <label>Статус</label>
        <select 
          value={status} 
          onChange={e => setStatus(e.target.value as 'OPEN' | 'CLOSED')}
          disabled={loading}
        >
          <option value="OPEN">Открыта</option>
          <option value="CLOSED">Закрыта</option>
        </select>
      </div>
      <div className="form-actions">
        <button type="button" className="btn" onClick={onSuccess} disabled={loading}>
          Отмена
        </button>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Создание...' : 'Создать'}
        </button>
      </div>
    </form>
  );
}
