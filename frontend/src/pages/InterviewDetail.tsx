import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  getInterviewById,
  updateInterview,
  deleteInterview,
  getCandidates,
  getVacancies,
  getUsers,
  Interview,
  Candidate,
  Vacancy,
  User,
} from '../api';
import { usePermissions } from '../hooks/usePermissions';

export function InterviewDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const permissions = usePermissions(user?.role);

  const [interview, setInterview] = useState<Interview | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [techSpecs, setTechSpecs] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState('');
  const [result, setResult] = useState<'INTERVIEW_PASSED' | 'INTERVIEW_FAILED'>('INTERVIEW_PASSED');

  useEffect(() => {
    loadData();
  }, [id]);

  async function loadData() {
    if (!id) return;
    setLoading(true);
    try {
      const [interv, cands, vacs, specs] = await Promise.all([
        getInterviewById(id),
        getCandidates({ limit: 200 }),
        getVacancies({ limit: 200 }),
        getUsers({ role: 'TECH_SPEC', limit: 200 }),
      ]);
      setInterview(interv);
      setCandidates(cands.items);
      setVacancies(vacs.items);
      setTechSpecs(specs.items);
      if (interv.feedback) setFeedback(interv.feedback);
      if (interv.result !== 'AWAIT_INTERVIEW') setResult(interv.result as any);
    } catch (err) {
      toast.error('Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveFeedback() {
    if (!interview) return;
    if (!permissions.canEditInterview) {
      toast.error('Нет прав на изменение интервью');
      return;
    }
    try {
      await updateInterview(interview.id, { feedback, result });
      toast.success('Фидбек сохранён');
      loadData();
    } catch (err) {
      toast.error('Ошибка сохранения');
    }
  }

  async function handleDelete() {
    if (!permissions.canDeleteInterview) {
      toast.error('Нет прав');
      return;
    }
    if (!confirm('Удалить интервью?')) return;
    try {
      await deleteInterview(interview!.id);
      toast.success('Удалено');
      navigate('/interviews');
    } catch (err) {
      toast.error('Ошибка удаления');
    }
  }

  if (loading) return <div className="content">Загрузка...</div>;
  if (!interview) return <div className="content">Интервью не найдено</div>;

  const candidate = candidates.find(c => c.id === interview.candidate_id);
  const vacancy = vacancies.find(v => v.id === candidate.vacancy_id);
  const techSpec = techSpecs.find(t => t.id === interview.tech_spec_id);

  return (
    <div className="content">
      <div className="detail-page">
        <div className="detail-header">
          <h2>Интервью</h2>
          <div className="detail-actions">
            {/* permissions.canDeleteInterview && (
              <button className="btn btn-danger" onClick={handleDelete}>🗑️ Удалить</button>
            )*/}
            <button className="btn" onClick={() => navigate('/interviews')}>← Назад</button>
          </div>
        </div>

        <div className="detail-section">
          <h3>Информация</h3>
          <div className="info-grid">
            <div className="info-item">
              <strong>Кандидат</strong>
              <span>
                {candidate?.full_name || '—'}
                <button className="btn btn-sm" style={{ marginLeft: '0.5rem' }} onClick={() => navigate(`/candidates/${interview.candidate_id}`)}>👁️</button>
              </span>
            </div>
            <div className="info-item">
              <strong>Вакансия</strong>
              <span>
                {vacancy?.title || '—'}
                <button className="btn btn-sm" style={{ marginLeft: '0.5rem' }} onClick={() => navigate(`/vacancies/${candidate.vacancy_id}`)}>👁️</button>
              </span>
            </div>
            <div className="info-item">
              <strong>Интервьюер</strong>
              <span>{techSpec?.full_name || '—'}</span>
            </div>
            <div className="info-item">
              <strong>Дата и время</strong>
              <span>{new Date(interview.scheduled_at * 1000).toLocaleString()}</span>
            </div>
            <div className="info-item">
              <strong>Ссылка на встречу</strong>
              {interview.zoom_url ? <a href={interview.zoom_url} target="_blank">{interview.zoom_url}</a> : <span>—</span>}
            </div>
            <div className="info-item">
              <strong>Текущий результат</strong>
              <span>{interview.result === 'AWAIT_INTERVIEW' ? 'Ожидается' : interview.result === 'INTERVIEW_PASSED' ? 'Пройдено' : 'Не пройдено'}</span>
            </div>
          </div>
        </div>

        {(permissions.canEditInterview || interview.feedback) && (
          <div className="detail-section">
            <h3>📝 Фидбек и результат</h3>
            <div className="feedback-form">
              <div className="form-group">
                <label>Результат интервью</label>
                <select value={result} onChange={e => setResult(e.target.value as any)} disabled={!permissions.canEditInterview}>
                  <option value="INTERVIEW_PASSED">Пройдено</option>
                  <option value="INTERVIEW_FAILED">Не пройдено</option>
                </select>
              </div>
              <div className="form-group">
                <label>Отзыв (feedback)</label>
                <textarea
                  rows={5}
                  value={feedback}
                  onChange={e => setFeedback(e.target.value)}
                  disabled={!permissions.canEditInterview}
                  placeholder="Введите фидбек по интервью..."
                />
              </div>
              {permissions.canEditInterview && (
                <button className="btn btn-primary" onClick={handleSaveFeedback}>Сохранить фидбек</button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
