import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { createCandidate, getVacancies, Vacancy } from '../api';

interface CreateCandidateFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export function CreateCandidateForm({ onSuccess, onCancel }: CreateCandidateFormProps) {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [resumeUrl, setResumeUrl] = useState('');
  const [vacancyId, setVacancyId] = useState('');
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingVacancies, setLoadingVacancies] = useState(true);

  useEffect(() => {
    loadVacancies();
  }, []);

  async function loadVacancies() {
    try {
      const response = await getVacancies({ status: 'OPEN', limit: 100 });
      setVacancies(response.items);
    } catch (err) {
      console.error('Failed to load vacancies:', err);
      toast.error('Не удалось загрузить список вакансий');
    } finally {
      setLoadingVacancies(false);
    }
  }

  const validatePhone = (phoneNumber: string): boolean => {
    const phoneRegex = /^\+7\d{10}$/;
    return phoneRegex.test(phoneNumber);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!fullName.trim()) {
      toast.error('Введите ФИО кандидата');
      return;
    }
    if (!email.trim()) {
      toast.error('Введите email кандидата');
      return;
    }
    if (!phone.trim()) {
      toast.error('Введите телефон кандидата');
      return;
    }
    if (!validatePhone(phone)) {
      toast.error('Телефон должен быть в формате +7XXXXXXXXXX (10 цифр после +7)');
      return;
    }
    if (!vacancyId) {
      toast.error('Выберите вакансию');
      return;
    }

    setLoading(true);
    
    try {
      await createCandidate({
        full_name: fullName.trim(),
        email: email.trim(),
        phone: phone.trim(),
        resume_url: resumeUrl.trim() || undefined,
        status: 'NEW',
        vacancy_id: vacancyId,
      });
      toast.success('Кандидат успешно создан');
      onSuccess();
    } catch (err: any) {
      console.error(err);
      if (err.message?.includes('400')) {
        toast.error('Вакансия не найдена или данные неверны');
      } else if (err.message?.includes('409')) {
        toast.error('Кандидат с таким email уже существует');
      } else {
        toast.error('Ошибка при создании кандидата');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="modal-header">
        <h3>Новый кандидат</h3>
        <p>Заполните информацию о кандидате</p>
      </div>

      <div className="form-group">
        <label>ФИО *</label>
        <input 
          type="text" 
          value={fullName} 
          onChange={e => setFullName(e.target.value)} 
          placeholder="Иванов Иван Иванович"
          required 
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label>Email *</label>
        <input 
          type="email" 
          value={email} 
          onChange={e => setEmail(e.target.value)} 
          placeholder="ivanov@example.com"
          required 
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label>Телефон *</label>
        <input 
          type="tel" 
          value={phone} 
          onChange={e => setPhone(e.target.value)} 
          placeholder="+79123456789"
          required 
          disabled={loading}
        />
        <small style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>
          Формат: +7XXXXXXXXXX (10 цифр после +7)
        </small>
      </div>

      <div className="form-group">
        <label>Ссылка на резюме</label>
        <input 
          type="url" 
          value={resumeUrl} 
          onChange={e => setResumeUrl(e.target.value)} 
          placeholder="https://example.com/resume.pdf"
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label>Вакансия *</label>
        <select 
          value={vacancyId} 
          onChange={e => setVacancyId(e.target.value)} 
          required 
          disabled={loading || loadingVacancies}
        >
          <option value="">Выберите вакансию</option>
          {vacancies.map(v => (
            <option key={v.id} value={v.id}>
              {v.title} — {v.status === 'OPEN' ? 'Открыта' : 'Закрыта'}
            </option>
          ))}
        </select>
        {loadingVacancies && <small>Загрузка вакансий...</small>}
        {vacancies.length === 0 && !loadingVacancies && (
          <small style={{ color: '#eab308' }}>
            Нет открытых вакансий. Сначала создайте вакансию.
          </small>
        )}
      </div>

      <div className="form-actions" style={{ marginTop: '20px' }}>
        <button type="button" className="btn" onClick={onCancel} disabled={loading}>
          Отмена
        </button>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Создание...' : 'Создать кандидата'}
        </button>
      </div>
    </form>
  );
}
