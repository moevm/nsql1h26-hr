import { useState } from 'react';
import { toast } from 'sonner';
import { createTestTask, Vacancy } from '../api';

interface CreateTestTaskFormProps {
  vacancies: Vacancy[];
  onSuccess: () => void;
  onCancel: () => void;
}

export function CreateTestTaskForm({ vacancies, onSuccess, onCancel }: CreateTestTaskFormProps) {
  const [title, setTitle] = useState('');
  const [testTaskUrl, setTestTaskUrl] = useState('');
  const [vacancyId, setVacancyId] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim()) {
      toast.error('Введите название задания');
      return;
    }
    
    if (!testTaskUrl.trim()) {
      toast.error('Введите ссылку на задание');
      return;
    }
    
    if (!vacancyId) {
      toast.error('Выберите вакансию');
      return;
    }

    setLoading(true);
    
    try {
      await createTestTask({
        title: title.trim(),
        test_task_url: testTaskUrl.trim(),
        vacancy_id: vacancyId,
      });
      toast.success('Тестовое задание успешно создано');
      onSuccess();
    } catch (err: any) {
      console.error(err);
      if (err.message?.includes('404')) {
        toast.error('Вакансия не найдена');
      } else {
        toast.error('Ошибка при создании задания');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="modal-header">
        <h3>Новое тестовое задание</h3>
        <p>Заполните информацию о задании</p>
      </div>
      
      <div className="form-group">
        <label htmlFor="title">Название *</label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={e => setTitle(e.target.value)}
          placeholder="Например: Frontend Developer Test"
          disabled={loading}
          required
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="url">Ссылка на задание *</label>
        <input
          id="url"
          type="url"
          value={testTaskUrl}
          onChange={e => setTestTaskUrl(e.target.value)}
          placeholder="https://docs.google.com/forms/..."
          disabled={loading}
          required
        />
        <small style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>
          Ссылка на Google Forms, GitHub или другой ресурс с заданием
        </small>
      </div>
      
      <div className="form-group">
        <label htmlFor="vacancy">Вакансия *</label>
        <select
          id="vacancy"
          value={vacancyId}
          onChange={e => setVacancyId(e.target.value)}
          disabled={loading || vacancies.length === 0}
          required
        >
          <option value="">Выберите вакансию</option>
          {vacancies.map(v => (
            <option key={v.id} value={v.id}>
              {v.title} {v.status === 'OPEN' ? '✓' : ''}
            </option>
          ))}
        </select>
        {vacancies.length === 0 && !loading && (
          <small style={{ color: '#eab308', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>
            Нет доступных вакансий. Сначала создайте вакансию.
          </small>
        )}
      </div>
      
      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel} disabled={loading}>
          Отмена
        </button>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Создание...' : 'Создать задание'}
        </button>
      </div>
    </form>
  );
}
