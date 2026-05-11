import { useState } from 'react';
import { toast } from 'sonner';
import { createTestTask, Vacancy, TestTask } from '../api';

interface CreateTestTaskFormProps {
  vacancies: Vacancy[];
  onSuccess: () => void;
  onCancel: () => void;
  initialData?: TestTask;
  preselectedVacancy?: Vacancy; // если передана – вакансия фиксирована
}

export function CreateTestTaskForm({ vacancies, onSuccess, onCancel, initialData, preselectedVacancy }: CreateTestTaskFormProps) {
  const isEdit = !!initialData;
  const [title, setTitle] = useState(initialData?.title || '');
  const [testTaskUrl, setTestTaskUrl] = useState(initialData?.test_task_url || '');
  const [vacancyId, setVacancyId] = useState(initialData?.vacancy_id || preselectedVacancy?.id || '');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return toast.error('Введите название');
    if (!testTaskUrl.trim()) return toast.error('Введите ссылку');
    if (!vacancyId) return toast.error('Выберите вакансию');

    setLoading(true);
    try {
      if (isEdit && initialData) {
        await updateTestTask(initialData.id, { title: title.trim(), test_task_url: testTaskUrl.trim() });
        toast.success('Тестовое задание обновлено');
      } else {
        await createTestTask({ title: title.trim(), test_task_url: testTaskUrl.trim(), vacancy_id: vacancyId });
        toast.success('Тестовое задание создано');
      }
      onSuccess();
    } catch (err) {
      toast.error(isEdit ? 'Ошибка обновления' : 'Ошибка создания');
    } finally {
      setLoading(false);
    }
  };

  // Определяем, нужно ли показывать выбор вакансии
  const showVacancySelect = !preselectedVacancy && !isEdit;

  return (
    <form onSubmit={handleSubmit}>
      <div className="modal-header">
        <h3>{isEdit ? 'Редактирование тестового задания' : 'Новое тестовое задание'}</h3>
      </div>

      {/* Если передана preselectedVacancy, показываем информационный блок */}
      {preselectedVacancy && (
        <div className="info-box" style={{ background: '#f0fdf4', padding: '12px', borderRadius: '8px', marginBottom: '16px', border: '1px solid #bbf7d0' }}>
          <strong>Вакансия:</strong> {preselectedVacancy.title}
        </div>
      )}

      <div className="form-group">
        <label>Название</label>
        <input type="text" value={title} onChange={e => setTitle(e.target.value)} required disabled={loading} />
      </div>
      <div className="form-group">
        <label>Ссылка</label>
        <input type="url" value={testTaskUrl} onChange={e => setTestTaskUrl(e.target.value)} required disabled={loading} />
      </div>

      {showVacancySelect && (
        <div className="form-group">
          <label>Вакансия</label>
          <select value={vacancyId} onChange={e => setVacancyId(e.target.value)} required disabled={loading}>
            <option value="">Выберите вакансию</option>
            {vacancies.map(v => <option key={v.id} value={v.id}>{v.title}</option>)}
          </select>
        </div>
      )}

      {isEdit && <small>Вакансию изменить нельзя</small>}

      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel} disabled={loading}>Отмена</button>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? (isEdit ? 'Сохранение...' : 'Создание...') : (isEdit ? 'Сохранить' : 'Создать')}
        </button>
      </div>
    </form>
  );
}
