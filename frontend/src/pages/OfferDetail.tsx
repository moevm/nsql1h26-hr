import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import {
  getOfferById,
  updateOfferStatus,
  deleteOffer,
  getCandidates,
  getVacancies,
  Offer,
  Candidate,
  Vacancy,
} from '../api';
import { CreateOfferForm } from '../components/CreateOfferForm';
import { usePermissions } from '../hooks/usePermissions';

export function OfferDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const permissions = usePermissions(user?.role);

  const [offer, setOffer] = useState<Offer | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);

  useEffect(() => {
    loadData();
  }, [id]);

  async function loadData() {
    if (!id) return;
    setLoading(true);
    try {
      const [off, cands, vacs] = await Promise.all([
        getOfferById(id),
        getCandidates({ limit: 200 }),
        getVacancies({ limit: 200 }),
      ]);
      setOffer(off);
      setCandidates(cands.items);
      setVacancies(vacs.items);
    } catch (err) {
      toast.error('Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove(by: 'manager' | 'candidate') {
    if (!offer) return;
    let newStatus: 'APPROVED_MNG' | 'APPROVED_CND' | null = null;
    if (by === 'manager') {
      if (offer.status !== 'PENDING') {
        toast.error('Оффер уже обработан');
        return;
      }
      newStatus = 'APPROVED_MNG';
    } else if (by === 'candidate') {
      if (offer.status !== 'APPROVED_MNG') {
        toast.error('Сначала оффер должен быть одобрен менеджером');
        return;
      }
      newStatus = 'APPROVED_CND';
    }
    if (!newStatus) return;
    try {
      const updated = await updateOfferStatus(offer.id, newStatus);
      setOffer(updated);
      toast.success('Статус обновлён');
      loadData();
    } catch (err) {
      toast.error('Ошибка обновления');
    }
  }

  async function handleReject(by: 'manager' | 'candidate') {
    if (!offer) return;
    let newStatus: 'REJECTED_MNG' | 'REJECTED_CNF' | null = null;
    if (by === 'manager') {
      if (offer.status !== 'PENDING') {
        toast.error('Оффер уже обработан');
        return;
      }
      newStatus = 'REJECTED_MNG';
    } else if (by === 'candidate') {
      if (offer.status !== 'APPROVED_MNG') {
        toast.error('Сначала оффер должен быть одобрен менеджером');
        return;
      }
      newStatus = 'REJECTED_CNF';
    }
    if (!newStatus) return;
    try {
      const updated = await updateOfferStatus(offer.id, newStatus);
      setOffer(updated);
      toast.success('Статус обновлён');
      loadData();
    } catch (err) {
      toast.error('Ошибка обновления');
    }
  }

  async function handleDelete() {
    if (!permissions.canDeleteOffer) {
      toast.error('Нет прав');
      return;
    }
    if (!confirm('Удалить оффер?')) return;
    try {
      await deleteOffer(offer!.id);
      toast.success('Оффер удалён');
      navigate('/offers');
    } catch (err) {
      toast.error('Ошибка удаления');
    }
  }

  if (loading) return <div className="content">Загрузка...</div>;
  if (!offer) return <div className="content">Оффер не найден</div>;

  const candidate = candidates.find(c => c.id === offer.candidate_id);
  const vacancy = vacancies.find(v => v.id === offer.vacancy_id);

  const getStatusLabel = (status: string) => {
    const map: Record<string, string> = {
      PENDING: 'Ожидает',
      APPROVED_MNG: 'Согласован менеджером',
      REJECTED_MNG: 'Отклонён менеджером',
      APPROVED_CND: 'Принят кандидатом',
      REJECTED_CNF: 'Отклонён кандидатом',
    };
    return map[status] || status;
  };

  const canEditOffer = permissions.canEditVacancy; // HR/ADMIN могут редактировать

  return (
    <div className="content">
      <div className="detail-page">
        <div className="detail-header">
          <h2>Оффер</h2>
          <div className="detail-actions">
            {canEditOffer && offer.status === 'PENDING' && (
              <button className="btn btn-primary" onClick={() => setShowEditModal(true)}>✏️ Редактировать</button>
            )}
            {/*permissions.canDeleteOffer && (
              <button className="btn btn-danger" onClick={handleDelete}>🗑️ Удалить</button>
            )*/}
            <button className="btn" onClick={() => navigate('/offers')}>← Назад</button>
          </div>
        </div>

        <div className="detail-section">
          <h3>Информация</h3>
          <div className="info-grid">
            <div className="info-item">
              <strong>Кандидат</strong>
              <span>
                {candidate?.full_name || '—'}
                <button className="btn btn-sm" style={{ marginLeft: '0.5rem' }} onClick={() => navigate(`/candidates/${offer.candidate_id}`)}>👁️</button>
              </span>
            </div>
            <div className="info-item">
              <strong>Вакансия</strong>
              <span>
                {vacancy?.title || '—'}
                <button className="btn btn-sm" style={{ marginLeft: '0.5rem' }} onClick={() => navigate(`/vacancies/${offer.vacancy_id}`)}>👁️</button>
              </span>
            </div>
            <div className="info-item">
              <strong>Зарплата</strong>
              <span>{offer.salary.toLocaleString()} ₽</span>
            </div>
            <div className="info-item">
              <strong>Дата выхода</strong>
              <span>{new Date(offer.start_at * 1000).toLocaleDateString()}</span>
            </div>
            <div className="info-item">
              <strong>Статус</strong>
              <span className={`status-badge ${offer.status === 'APPROVED_CND' ? 'badge-success' : offer.status.includes('REJECTED') ? 'badge-danger' : 'badge-warning'}`}>
                {getStatusLabel(offer.status)}
              </span>
            </div>
            <div className="info-item">
              <strong>Создатель (ID)</strong>
              <span>{offer.created_by}</span>
            </div>
            <div className="info-item">
              <strong>Создан</strong>
              <span>{offer.created_at ? new Date(offer.created_at * 1000).toLocaleString() : '—'}</span>
            </div>
          </div>
        </div>

        {(offer.status === 'PENDING' || offer.status === 'APPROVED_MNG') && permissions.canEditOfferStatus && (
          <div className="detail-section">
            <h3>⚙️ Действия</h3>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              {offer.status === 'PENDING' && (
                <>
                  <button className="btn btn-success" onClick={() => handleApprove('manager')}>✅ Одобрить (менеджер)</button>
                  <button className="btn btn-danger" onClick={() => handleReject('manager')}>❌ Отклонить (менеджер)</button>
                </>
              )}
              {offer.status === 'APPROVED_MNG' && (
                <>
                  <button className="btn btn-success" onClick={() => handleApprove('candidate')}>✅ Принять (кандидат)</button>
                  <button className="btn btn-danger" onClick={() => handleReject('candidate')}>❌ Отказаться (кандидат)</button>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {showEditModal && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <CreateOfferForm
              initialData={offer}
              onSuccess={() => { setShowEditModal(false); loadData(); }}
              onCancel={() => setShowEditModal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
