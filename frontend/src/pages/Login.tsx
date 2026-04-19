// pages/Login.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import '../styles/App.css';

export function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();

    // TODO: заменить на реальный API вызов
    if (username === 'hr' && password === 'hr123') {
      const user = {
        id: '1',
        full_name: 'HR Менеджер',  // full_name вместо fullName
        role: 'HR',                 // правильный формат
        email: 'hr@example.com',
      };
      localStorage.setItem('user', JSON.stringify(user));
      toast.success('Добро пожаловать!');
      navigate('/vacancies');
    } else if (username === 'admin' && password === 'admin123') {
      const user = {
        id: '2',
        full_name: 'Администратор',
        role: 'ADMIN',              // правильный формат (заглавные)
        email: 'admin@example.com',
      };
      localStorage.setItem('user', JSON.stringify(user));
      toast.success('Добро пожаловать!');
      navigate('/vacancies');
    } else if (username === 'tech' && password === 'tech123') {
      const user = {
        id: '3',
        full_name: 'Технический специалист',
        role: 'TECH_SPEC',          // правильный формат (полное название)
        email: 'tech@example.com',
      };
      localStorage.setItem('user', JSON.stringify(user));
      toast.success('Добро пожаловать!');
      navigate('/vacancies');
    } else if (username === 'manager' && password === 'manager123') {
      const user = {
        id: '4',
        full_name: 'Менеджер',
        role: 'MANAGER',            // правильный формат (заглавные)
        email: 'manager@example.com',
      };
      localStorage.setItem('user', JSON.stringify(user));
      toast.success('Добро пожаловать!');
      navigate('/vacancies');
    } else {
      toast.error('Неверный логин или пароль');
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
            <label htmlFor="username">Логин</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="Введите логин"
              required
              autoFocus
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
            />
          </div>
          <button type="submit" className="btn btn-primary w-full">
            Войти
          </button>
        </form>
        <div className="login-footer">
          <p>Тестовые пользователи:</p>
          <ul>
            <li><strong>HR:</strong> hr / hr123</li>
            <li><strong>Администратор:</strong> admin / admin123</li>
            <li><strong>Менеджер:</strong> manager / manager123</li>
            <li><strong>Технический специалист:</strong> tech / tech123</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
