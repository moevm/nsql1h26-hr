import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { login, createUser } from '../api';
import '../styles/App.css';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [registerData, setRegisterData] = useState({
    email: '',
    full_name: '',
    password: '',
    role: 'HR' as 'ADMIN' | 'HR' | 'MANAGER' | 'TECH_SPEC'
  });
  const [registerLoading, setRegisterLoading] = useState(false);
  const navigate = useNavigate();

  const getDashboardPathByRole = (role: string): string => {
    switch (role) {
      case 'ADMIN':
        return '/administration';
      case 'HR':
        return '/vacancies';
      case 'MANAGER':
        return '/offers';
      case 'TECH_SPEC':
        return '/interviews';
      default:
        return '/vacancies';
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Введите email и пароль');
      return;
    }
    setLoading(true);
    try {
      const response = await login({ email, password });
      toast.success('Добро пожаловать!');
      const dashboardPath = getDashboardPathByRole(response.user.role);
      navigate(dashboardPath);
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || 'Ошибка при входе');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    const { email, full_name, password, role } = registerData;
    if (!email.trim() || !full_name.trim() || !password.trim()) {
      toast.error('Заполните все поля');
      return;
    }
    if (password.length < 6) {
      toast.error('Пароль должен быть не менее 6 символов');
      return;
    }
    setRegisterLoading(true);
    try {
      await createUser({ email, full_name, password, role });
      toast.success('Пользователь успешно зарегистрирован! Теперь войдите.');
      setShowRegisterModal(false);
      setRegisterData({ email: '', full_name: '', password: '', role: 'HR' });
      setEmail(email);
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || 'Ошибка регистрации');
    } finally {
      setRegisterLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="login-icon">HR</div>
          <h2>HR CRM System</h2>
          <p>Войдите в систему</p>
        </div>
        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="user@example.com"
              required
              autoFocus
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Пароль</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Введите пароль"
              required
              disabled={loading}
            />
          </div>
          <button type="submit" className="btn btn-primary w-full" disabled={loading}>
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <button
            type="button"
            className="btn"
            onClick={() => setShowRegisterModal(true)}
            style={{ fontSize: '0.875rem' }}
          >
            Зарегистрировать нового пользователя
          </button>
        </div>
        <div className="login-footer">
          <p>Тестовые пользователи:</p>
          <ul>
            <li><strong>HR:</strong> hr@example.com / hr123</li>
            <li><strong>Администратор:</strong> admin@example.com / admin123</li>
            <li><strong>Менеджер:</strong> manager@example.com / manager123</li>
            <li><strong>Тех. специалист:</strong> tech@example.com / tech123</li>
          </ul>
        </div>
      </div>

      {showRegisterModal && (
        <div className="modal-overlay" onClick={() => setShowRegisterModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Регистрация нового пользователя</h3>
              <p>Заполните данные</p>
            </div>
            <form onSubmit={handleRegister}>
              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  value={registerData.email}
                  onChange={e => setRegisterData({ ...registerData, email: e.target.value })}
                  required
                  disabled={registerLoading}
                />
              </div>
              <div className="form-group">
                <label>Полное имя *</label>
                <input
                  type="text"
                  value={registerData.full_name}
                  onChange={e => setRegisterData({ ...registerData, full_name: e.target.value })}
                  required
                  disabled={registerLoading}
                />
              </div>
              <div className="form-group">
                <label>Пароль *</label>
                <input
                  type="password"
                  value={registerData.password}
                  onChange={e => setRegisterData({ ...registerData, password: e.target.value })}
                  required
                  disabled={registerLoading}
                  minLength={6}
                />
                <small>Минимум 6 символов</small>
              </div>
              <div className="form-group">
                <label>Роль *</label>
                <select
                  value={registerData.role}
                  onChange={e => setRegisterData({ ...registerData, role: e.target.value as any })}
                  required
                  disabled={registerLoading}
                >
                  <option value="HR">HR</option>
                  <option value="ADMIN">Администратор</option>
                  <option value="MANAGER">Менеджер</option>
                  <option value="TECH_SPEC">Технический специалист</option>
                </select>
              </div>
              <div className="form-actions">
                <button type="button" className="btn" onClick={() => setShowRegisterModal(false)} disabled={registerLoading}>
                  Отмена
                </button>
                <button type="submit" className="btn btn-primary" disabled={registerLoading}>
                  {registerLoading ? 'Регистрация...' : 'Зарегистрировать'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
