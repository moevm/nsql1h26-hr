import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { login } from '../api';
import '../styles/App.css';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error('Введите email и пароль');
      return;
    }

    setLoading(true);
    
    try {
      await login({ email, password });
      toast.success('Добро пожаловать!');
      navigate('/vacancies');
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || 'Ошибка при входе в систему');
    } finally {
      setLoading(false);
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
    </div>
  );
}
