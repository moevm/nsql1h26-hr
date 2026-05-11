import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  getCandidateById,
  getInterviews,
  getOffers,
  getVacancies,
  deleteCandidate,
  Candidate,
  Interview,
  Offer,
  Vacancy,
} from '../api';
import { usePermissions } from '../hooks/usePermissions';
import { CreateCandidateForm } from '../components/CreateCandidateForm';
import { CreateInterviewForm } from '../components/CreateInterviewForm';
import { CreateOfferForm } from '../components/CreateOfferForm';

export function CandidateDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const permissions = usePermissions(user?.role);

  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showInterviewModal, setShowInterviewModal] = useState(false);
  const [showOfferModal, setShowOfferModal] = useState(false);

  useEffect(() => {
    loadData();
  }, [id]);

  async function loadData() {
    if (!id) return;
    setLoading(true);
    try {
      const [cand, inters, offs, vacs] = await Promise.all([
        getCandidateById(id),
        getInterviews({ candidate_id: id, limit: 100 }),
        getOffers({ candidate_id: id, limit: 100 }),
        getVacancies({ limit: 200 }),
      ]);
      setCandidate(cand);
      setInterviews(inters.items);
      setOffers(offs.items);
      setVacancies(vacs.items);
    } catch (err) {
      toast.error('Ошибка загрузки');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete() {
    if (!permissions.canDeleteCandidate) {
      toast.error('Нет прав');
      return;
    }
    if (!confirm('Удалить кандидата?')) return;
    try {
      await deleteCandidate(id!);
      toast.success('Кандидат удалён');
      navigate('/candidates');
    } catch (err) {
      toast.error('Ошибка удаления');
    }
  }

  const getStatusLabel = (status: string) => {
    const map: Record<string, string> = {
      NEW: 'Новый',
      TEST: 'Тестовое',
      AWAIT_INTERVIEW: 'Ожидает интервью',
      INTERVIEW_PASSED: 'Интервью пройдено',
      OFFER: 'Оффер',
      REJECTED: 'Отказ',
      HIRED: 'Нанят',
    };
    return map[status] || status;
  };

  if (loading) return <div className="content">Загрузка...</div>;
  if (!candidate) return <div className="content">Кандидат не найден</div>;

  const vacancyTitle = vacancies.find(v => v.id === candidate.vacancy_id)?.title || '—';

  return (
    <div className="content">
      <div className="detail-page">
        <div className="detail-header">
          <h2>{candidate.full_name}</h2>
          <div className="detail-actions">
            {permissions.canEditCandidate && (
              <button className="btn btn-primary" onClick={() => setShowEditModal(true)}>✏️ Редактировать</button>
            )}
            {permissions.canCreateInterview && (
              <button className="btn" onClick={() => setShowInterviewModal(true)}>📅 Назначить интервью</button>
            )}
            {permissions.canCreateOffer && (
              <button className="btn" onClick={() => setShowOfferModal(true)}>💰 Создать оффер</button>
            )}
            {permissions.canDeleteCandidate 
            	/* && (
              <button className="btn btn-danger" onClick={handleDelete}>🗑️ Удалить</button>
            	) */
            }
            <button className="btn" onClick={() => navigate('/candidates')}>← Назад</button>
          </div>
        </div>

        <div className="detail-section">
          <h3>Информация о кандидате</h3>
          <div className="info-grid">
            <div className="info-item">
              <strong>Email</strong>
              <span>{candidate.email}</span>
            </div>
            <div className="info-item">
              <strong>Телефон</strong>
              <span>{candidate.phone}</span>
            </div>
            <div className="info-item">
              <strong>Резюме</strong>
              {candidate.resume_url ? (
                <a href={candidate.resume_url} target="_blank" rel="noopener noreferrer">{candidate.resume_url}</a>
              ) : <span>—</span>}
            </div>
            <div className="info-item">
              <strong>Статус</strong>
              <span className={`status-badge badge-${candidate.status === 'HIRED' ? 'success' : candidate.status === 'REJECTED' ? 'danger' : 'warning'}`}>
                {getStatusLabel(candidate.status)}
              </span>
            </div>
            <div className="info-item">
              <strong>Вакансия</strong>
              <span>
                {vacancyTitle}
                <button className="btn btn-sm" style={{ marginLeft: '0.5rem' }} onClick={() => navigate(`/vacancies/${candidate.vacancy_id}`)}>👁️</button>
              </span>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>📝 Интервью</h3>
          {interviews.length === 0 && <div className="list-item">Нет интервью</div>}
          <div className="list-card">
            {interviews.map(i => (
              <div key={i.id} className="list-item">
                <div className="list-item-content">
                  <div className="list-item-title">
                    {new Date(i.scheduled_at * 1000).toLocaleString()}
                  </div>
                  <div className="list-item-subtitle">
                    Результат: {i.result === 'AWAIT_INTERVIEW' ? 'Ожидается' : i.result === 'INTERVIEW_PASSED' ? 'Пройдено' : 'Не пройдено'}
                  </div>
                </div>
                <div className="list-item-actions">
                  <button className="btn btn-sm" onClick={() => navigate(`/interviews/${i.id}`)}>👁️</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="detail-section">
          <h3>💼 Офферы</h3>
          {offers.length === 0 && <div className="list-item">Нет офферов</div>}
          <div className="list-card">
            {offers.map(o => (
              <div key={o.id} className="list-item">
                <div className="list-item-content">
                  <div className="list-item-title">{o.salary.toLocaleString()} ₽</div>
                  <div className="list-item-subtitle">Статус: {o.status}</div>
                </div>
                <div className="list-item-actions">
                  <button className="btn btn-sm" onClick={() => navigate(`/offers/${o.id}`)}>👁️</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {showEditModal && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <CreateCandidateForm
              initialData={candidate}
              onSuccess={() => { setShowEditModal(false); loadData(); }}
              onCancel={() => setShowEditModal(false)}
            />
          </div>
        </div>
      )}

      {showInterviewModal && (
	  <div className="modal-overlay" onClick={() => setShowInterviewModal(false)}>
		<div className="modal" onClick={e => e.stopPropagation()}>
		  <CreateInterviewForm
			  preselectedCandidate={candidate}
			  onSuccess={() => { setShowInterviewModal(false); loadData(); }}
			  onCancel={() => setShowInterviewModal(false)}
			/>
		</div>
	  </div>
	)}

	{showOfferModal && (
	  <div className="modal-overlay" onClick={() => setShowOfferModal(false)}>
		<div className="modal" onClick={e => e.stopPropagation()}>
		  <CreateOfferForm
			  preselectedCandidate={candidate}
			  preselectedVacancy={vacancies.find(v => v.id === candidate.vacancy_id)}
			  onSuccess={() => { setShowOfferModal(false); loadData(); }}
			  onCancel={() => setShowOfferModal(false)}
			/>
		</div>
	  </div>
	)}
    </div>
  );
}
