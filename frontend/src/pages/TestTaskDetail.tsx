import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  getTestTaskById,
  updateTestTask,
  deleteTestTask,
  getVacancyById,
  TestTask,
  Vacancy,
} from '../api';
import { usePermissions } from '../hooks/usePermissions';
import { CreateTestTaskForm } from '../components/CreateTestTaskForm';

export function TestTaskDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const permissions = usePermissions(user?.role);

  const [testTask, setTestTask] = useState<TestTask | null>(null);
  const [vacancy, setVacancy] = useState<Vacancy | null>(null);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);

  useEffect(() => {
    loadData();
  }, [id]);

  async function loadData() {
    if (!id) return;
    setLoading(true);
    try {
      const task = await getTestTaskById(id);
      setTestTask(task);
      
      const vac = await getVacancyById(task.vacancy_id);
      setVacancy(vac);
    } catch (err) {
      toast.error('Ошибка загрузки данных');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete() {
    if (!permissions.canDeleteTestTask) {
      toast.error('Нет прав на удаление');
      return;
    }
    if (!confirm('Удалить тестовое задание?')) return;
    try {
      await deleteTestTask(testTask!.id);
      toast.success('Тестовое задание удалено');
      navigate('/test-tasks');
    } catch (err) {
      toast.error('Ошибка удаления');
    }
  }

  if (loading) return <div className="content">Загрузка...</div>;
  if (!testTask) return <div className="content">Тестовое задание не найдено</div>;

  return (
    <div className="content">
      <div className="detail-page">
        <div className="detail-header">
          <h2>{testTask.title}</h2>
          <div className="detail-actions">
            {permissions.canEditTestTask && (
              <button className="btn btn-primary" onClick={() => setShowEditModal(true)}>
                ✏️ Редактировать
              </button>
            )}
            {/*permissions.canDeleteTestTask && (
              <button className="btn btn-danger" onClick={handleDelete}>🗑️ Удалить</button>
            )*/}
            <button className="btn" onClick={() => navigate('/test-tasks')}>← Назад</button>
          </div>
        </div>

        <div className="detail-section">
          <h3>Информация</h3>
          <div className="info-grid">
            <div className="info-item">
              <strong>Название</strong>
              <span>{testTask.title}</span>
            </div>
            <div className="info-item">
              <strong>Ссылка</strong>
              {testTask.test_task_url ? (
                <a href={testTask.test_task_url} target="_blank" rel="noopener noreferrer">
                  Открыть
                </a>
              ) : <span>—</span>}
            </div>
            <div className="info-item">
              <strong>Вакансия</strong>
              <span>
                {vacancy?.title || '—'}
                <button
                  className="btn btn-sm"
                  style={{ marginLeft: '0.5rem' }}
                  onClick={() => navigate(`/vacancies/${testTask.vacancy_id}`)}
                >
                  👁️
                </button>
              </span>
            </div>
          </div>
        </div>
      </div>

      {showEditModal && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <CreateTestTaskForm
              initialData={testTask}
              vacancies={vacancy ? [vacancy] : []}
              onSuccess={() => {
                setShowEditModal(false);
                loadData();
              }}
              onCancel={() => setShowEditModal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
