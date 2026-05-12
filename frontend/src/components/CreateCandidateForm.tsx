import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { createCandidate, updateCandidate, getVacancies, Vacancy, Candidate } from '../api';

interface CreateCandidateFormProps {
  onSuccess: () => void;
  onCancel: () => void;
  initialData?: Candidate;   // если передан – режим редактирования
}

export function CreateCandidateForm({ onSuccess, onCancel, initialData }: CreateCandidateFormProps) {
  const isEdit = !!initialData;
  
  const [fullName, setFullName] = useState(initialData?.full_name || '');
  const [email, setEmail] = useState(initialData?.email || '');
  const [phone, setPhone] = useState(initialData?.phone || '');
  const [resumeUrl, setResumeUrl] = useState(initialData?.resume_url || '');
  const [vacancyId, setVacancyId] = useState(initialData?.vacancy_id || '');
  const [status, setStatus] = useState(initialData?.status || 'NEW');
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingVacancies, setLoadingVacancies] = useState(true);

  useEffect(() => {
    loadVacancies();
  }, []);

  async function loadVacancies() {
    try {
      const response = await getVacancies({ limit: 200 });
      setVacancies(response.items);
    } catch (err) {
      console.error(err);
      toast.error('Не удалось загрузить список вакансий');
    } finally {
      setLoadingVacancies(false);
    }
  }

  const validatePhone = (phoneNumber: string): boolean => /^\+7\d{10}$/.test(phoneNumber);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim()) return toast.error('Введите ФИО');
    if (!email.trim()) return toast.error('Введите email');
    if (!phone.trim()) return toast.error('Введите телефон');
    if (!validatePhone(phone)) return toast.error('Телефон должен быть в формате +7XXXXXXXXXX');
    if (!vacancyId) return toast.error('Выберите вакансию');

    setLoading(true);
    try {
      if (isEdit && initialData) {
        await updateCandidate(initialData.id, {
          full_name: fullName.trim(),
          email: email.trim(),
          phone: phone.trim(),
          resume_url: resumeUrl.trim() || undefined,
          vacancy_id: vacancyId,
          status,
        });
        toast.success('Данные обновлены');
      } else {
        await createCandidate({
          full_name: fullName.trim(),
          email: email.trim(),
          phone: phone.trim(),
          resume_url: resumeUrl.trim() || undefined,
          status: 'NEW',
          vacancy_id: vacancyId,
        });
        toast.success('Кандидат создан');
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
      <div className="modal-header">
        <h3>{isEdit ? 'Редактирование кандидата' : 'Новый кандидат'}</h3>
      </div>
      <div className="form-group">
        <label>ФИО *</label>
        <input type="text" value={fullName} onChange={e => setFullName(e.target.value)} required disabled={loading} />
      </div>
      <div className="form-group">
        <label>Email *</label>
        <input type="email" value={email} onChange={e => setEmail(e.target.value)} required disabled={loading} />
      </div>
      <div className="form-group">
        <label>Телефон *</label>
        <input type="tel" value={phone} onChange={e => setPhone(e.target.value)} required disabled={loading} />
        <small>Формат: +7XXXXXXXXXX</small>
      </div>
      <div className="form-group">
        <label>Ссылка на резюме</label>
        <input type="url" value={resumeUrl} onChange={e => setResumeUrl(e.target.value)} disabled={loading} />
      </div>
      <div className="form-group">
        <label>Вакансия *</label>
        <select value={vacancyId} onChange={e => setVacancyId(e.target.value)} required disabled={loading || loadingVacancies}>
          <option value="">Выберите вакансию</option>
          {vacancies.map(v => <option key={v.id} value={v.id}>{v.title}</option>)}
        </select>
      </div>
      {isEdit && (
        <div className="form-group">
          <label>Статус</label>
          <select value={status} onChange={e => setStatus(e.target.value)} disabled={loading}>
            <option value="NEW">Новый</option><option value="TEST">Тестовое</option>
            <option value="AWAIT_INTERVIEW">Ожидает интервью</option><option value="INTERVIEW_PASSED">Интервью пройдено</option>
            <option value="OFFER">Оффер</option>
            <option value="HIRED">Нанят</option><option value="REJECTED">Отказ</option>
          </select>
        </div>
      )}
      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel} disabled={loading}>Отмена</button>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? (isEdit ? 'Сохранение...' : 'Создание...') : (isEdit ? 'Сохранить' : 'Создать')}
        </button>
      </div>
    </form>
  );
}
