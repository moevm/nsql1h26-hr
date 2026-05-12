import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  getVacancyById,
  getTestTasks,
  deleteTestTask,
  getCandidates,
  Vacancy,
  TestTask,
  Candidate,
} from '../api';
import { usePermissions } from '../hooks/usePermissions';
import { CreateVacancyForm } from '../components/CreateVacancyForm';
import { CreateTestTaskForm } from '../components/CreateTestTaskForm';

export function VacancyDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const permissions = usePermissions(user?.role);

  const [vacancy, setVacancy] = useState<Vacancy | null>(null);
  const [testTasks, setTestTasks] = useState<TestTask[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showAddTestModal, setShowAddTestModal] = useState(false);
  const [editingTestTask, setEditingTestTask] = useState<TestTask | null>(null);

  useEffect(() => {
    loadData();
  }, [id]);

  async function loadData() {
    if (!id) return;
    setLoading(true);
    try {
      const [vac, tasks, cand] = await Promise.all([
        getVacancyById(id),
        getTestTasks({ vacancy_id: id, limit: 100 }),
        getCandidates({ vacancy_id: id, limit: 100 }),
      ]);
      setVacancy(vac);
      setTestTasks(tasks.items);
      setCandidates(cand.items);
    } catch (err) {
      toast.error('Ошибка загрузки данных');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteTestTask(taskId: string) {
    if (!confirm('Удалить тестовое задание?')) return;
    try {
      await deleteTestTask(taskId);
      toast.success('Удалено');
      loadData();
    } catch (err) {
      toast.error('Ошибка удаления');
    }
  }

  if (loading) return <div className="content">Загрузка...</div>;
  if (!vacancy) return <div className="content">Вакансия не найдена</div>;

  return (
    <div className="content">
      <div className="detail-page">
        <div className="detail-header">
          <h2>{vacancy.title}</h2>
          <div className="detail-actions">
            {permissions.canEditVacancy && (
              <button className="btn btn-primary" onClick={() => setShowEditModal(true)}>✏️ Редактировать</button>
            )}
            {permissions.canCreateTestTask && (
              <button className="btn" onClick={() => setShowAddTestModal(true)}>📎 Прикрепить тестовое</button>
            )}
            <button className="btn" onClick={() => navigate('/vacancies')}>← Назад</button>
          </div>
        </div>

        <div className="detail-section">
          <h3>Описание</h3>
          <div className="info-grid">
            <div className="info-item">
              <strong>Описание</strong>
              <span>{vacancy.description}</span>
            </div>
            <div className="info-item">
              <strong>Статус</strong>
              <span className={`status-badge ${vacancy.status === 'OPEN' ? 'badge-success' : 'badge-danger'}`}>
                {vacancy.status === 'OPEN' ? 'Открыта' : 'Закрыта'}
              </span>
            </div>
            <div className="info-item">
              <strong>Создана</strong>
              <span>{new Date(vacancy.created_at * 1000).toLocaleDateString()}</span>
            </div>
            {vacancy.closed_at && (
              <div className="info-item">
                <strong>Закрыта</strong>
                <span>{new Date(vacancy.closed_at * 1000).toLocaleDateString()}</span>
              </div>
            )}
          </div>
        </div>

        <div className="detail-section">
          <h3>📋 Тестовые задания</h3>
          {testTasks.length === 0 && <div className="list-item">Нет прикреплённых тестовых заданий</div>}
          <div className="list-card">
            {testTasks.map(task => (
              <div key={task.id} className="list-item">
                <div className="list-item-content">
                  <a href={task.test_task_url} target="_blank" rel="noopener noreferrer" className="test-task-link">
                    {task.title}
                  </a>
                </div>
                <div className="list-item-actions">
                  {permissions.canEditTestTask && (
                    <button className="btn btn-sm" onClick={() => setEditingTestTask(task)}>✏️</button>
                  )}
                  {/*permissions.canDeleteTestTask && (
                    <button className="btn btn-sm btn-danger" onClick={() => handleDeleteTestTask(task.id)}>🗑️</button>
                  )*/}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="detail-section">
          <h3>👥 Кандидаты на вакансию</h3>
          {candidates.length === 0 && <div className="list-item">Нет кандидатов</div>}
          <div className="list-card">
            {candidates.map(c => (
              <div key={c.id} className="list-item">
                <div className="list-item-content">
                  <div className="list-item-title">{c.full_name}</div>
                  <div className="list-item-subtitle">{c.email} • {c.phone}</div>
                </div>
                <div className="list-item-actions">
                  <button className="btn btn-sm" onClick={() => navigate(`/candidates/${c.id}`)}>👁️</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {showEditModal && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <CreateVacancyForm
              initialData={vacancy}
              onSuccess={() => { setShowEditModal(false); loadData(); }}
              onCancel={() => setShowEditModal(false)}
            />
          </div>
        </div>
      )}

      {showAddTestModal && (
        <div className="modal-overlay" onClick={() => setShowAddTestModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <CreateTestTaskForm
              vacancies={[vacancy]}
              preselectedVacancy={vacancy}
              onSuccess={() => { setShowAddTestModal(false); loadData(); }}
              onCancel={() => setShowAddTestModal(false)}
            />
          </div>
        </div>
      )}

      {editingTestTask && (
        <div className="modal-overlay" onClick={() => setEditingTestTask(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <CreateTestTaskForm
              vacancies={[vacancy]}
              initialData={editingTestTask}
              onSuccess={() => { setEditingTestTask(null); loadData(); }}
              onCancel={() => setEditingTestTask(null)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
