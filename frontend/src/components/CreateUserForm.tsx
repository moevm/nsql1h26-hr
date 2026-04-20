import { useState } from 'react';
import { toast } from 'sonner';
import { createUser } from '../api';

interface CreateUserFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export function CreateUserForm({ onSuccess, onCancel }: CreateUserFormProps) {
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    password: '',
    role: 'HR',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.email.trim()) {
      toast.error('Введите email пользователя');
      return;
    }
    if (!formData.full_name.trim()) {
      toast.error('Введите ФИО пользователя');
      return;
    }
    if (!formData.password) {
      toast.error('Введите пароль');
      return;
    }
    if (formData.password.length < 6) {
      toast.error('Пароль должен содержать минимум 6 символов');
      return;
    }
    if (!formData.role) {
      toast.error('Выберите роль пользователя');
      return;
    }

    setLoading(true);
    
    try {
      await createUser({
        email: formData.email.trim(),
        full_name: formData.full_name.trim(),
        password: formData.password,
        role: formData.role,
      });
      toast.success('Пользователь успешно создан');
      onSuccess();
    } catch (err: any) {
      console.error(err);
      if (err.message?.includes('409')) {
        toast.error('Пользователь с таким email уже существует');
      } else if (err.message?.includes('400')) {
        toast.error('Неверные данные. Проверьте email и ФИО (минимум 3 символа)');
      } else {
        toast.error('Ошибка при создании пользователя');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const roleOptions = [
    { value: 'ADMIN', label: 'Администратор', description: 'Полный доступ ко всем функциям' },
    { value: 'HR', label: 'HR', description: 'Управление кандидатами, вакансиями, интервью' },
    { value: 'MANAGER', label: 'Менеджер', description: 'Управление офферами и согласование' },
    { value: 'TECH_SPEC', label: 'Технический специалист', description: 'Проведение интервью' },
  ];

  return (
    <form onSubmit={handleSubmit}>
      <div className="modal-header">
        <h3>Новый пользователь</h3>
        <p>Заполните данные для создания учётной записи</p>
      </div>

      <div className="form-group">
        <label>Email (логин) *</label>
        <input
          type="email"
          value={formData.email}
          onChange={e => handleChange('email', e.target.value)}
          placeholder="user@example.com"
          required
          disabled={loading}
        />
        <small style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>
          Email будет использоваться для входа в систему
        </small>
      </div>

      <div className="form-group">
        <label>ФИО *</label>
        <input
          type="text"
          value={formData.full_name}
          onChange={e => handleChange('full_name', e.target.value)}
          placeholder="Иванов Иван Иванович"
          required
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label>Пароль *</label>
        <input
          type="password"
          value={formData.password}
          onChange={e => handleChange('password', e.target.value)}
          placeholder="Минимум 6 символов"
          required
          disabled={loading}
        />
        <small style={{ color: '#64748b', fontSize: '0.75rem', marginTop: '0.25rem', display: 'block' }}>
          Пароль должен содержать минимум 6 символов
        </small>
      </div>

      <div className="form-group">
        <label>Роль *</label>
        <select
          value={formData.role}
          onChange={e => handleChange('role', e.target.value)}
          required
          disabled={loading}
        >
          {roleOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <div style={{ marginTop: '8px' }}>
          {roleOptions.find(r => r.value === formData.role) && (
            <small style={{ color: '#64748b', fontSize: '0.75rem' }}>
              {roleOptions.find(r => r.value === formData.role)?.description}
            </small>
          )}
        </div>
      </div>

      <div className="form-actions" style={{ marginTop: '24px' }}>
        <button type="button" className="btn" onClick={onCancel} disabled={loading}>
          Отмена
        </button>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Создание...' : 'Создать пользователя'}
        </button>
      </div>
    </form>
  );
}
