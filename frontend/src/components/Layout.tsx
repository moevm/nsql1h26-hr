import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { usePermissions } from '../hooks/usePermissions';
import '../styles/App.css';

export function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState<{ id: string; email: string; full_name: string; role: string } | null>(null);
  const permissions = usePermissions(user?.role as any);

  useEffect(() => {
    const stored = localStorage.getItem('user');
    if (stored) {
      setUser(JSON.parse(stored));
    } else {
      navigate('/');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    navigate('/');
  };

  if (!user) return null;

  const isActive = (path: string) => location.pathname === path;

  const getRoleLabel = (role: string): string => {
    const roleMap: Record<string, string> = {
      'ADMIN': 'Администратор',
      'HR': 'HR-менеджер',
      'MANAGER': 'Руководитель',
      'TECH_SPEC': 'Технический специалист',
    };
    return roleMap[role] || role;
  };

  // Навигационные элементы с проверкой прав через usePermissions
  const navigationItems = [
    { 
      path: '/vacancies', 
      label: 'Вакансии', 
      show: permissions.canViewVacancies 
    },
    { 
      path: '/candidates', 
      label: 'Кандидаты', 
      show: permissions.canViewCandidates 
    },
    { 
      path: '/test-assignments', 
      label: 'Тестовые задания', 
      show: permissions.canViewTestTasks 
    },
    { 
      path: '/interviews', 
      label: 'Интервью', 
      show: permissions.canViewInterviews 
    },
    { 
      path: '/offers', 
      label: 'Офферы', 
      show: permissions.canViewOffers 
    },
    { 
      path: '/administration', 
      label: 'Пользователи', 
      show: permissions.canViewUsers 
    },
  ];

  const allowedItems = navigationItems.filter(item => item.show);

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">HR</div>
            <div className="logo-text">
              <h1>HR CRM</h1>
              <p>{user.full_name} • {getRoleLabel(user.role)}</p>
            </div>
          </div>
          <button className="btn btn-sm" onClick={handleLogout}>
            🚪 Выйти
          </button>
        </div>
      </header>
      <div className="layout-main">
        <aside className="sidebar">
          <nav className="nav">
            {allowedItems.length > 0 ? (
              allowedItems.map(item => (
                <Link 
                  key={item.path} 
                  to={item.path} 
                  className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                >
                  {item.label}
                </Link>
              ))
            ) : (
              <div style={{ padding: '0.5rem', color: '#64748b', fontSize: '0.875rem' }}>
                Нет доступных разделов
              </div>
            )}
          </nav>
        </aside>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
