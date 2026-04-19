import { useState, useEffect, useMemo } from 'react';
import { DataTable, Column } from '../components/DataTable';
import { FilterBar } from '../components/FilterBar';
import { useFilters } from '../hooks/useFilters';
import { FilterField } from '../types/filters';
import { toast } from 'sonner';
import { getUsers, deleteUser, User } from '../api';
import { usePermissions } from '../hooks/usePermissions';
import { CreateUserForm } from '../components/CreateUserForm';
import '../styles/App.css';

export function Administration() {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const permissions = usePermissions(user?.role);

  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [pagination, setPagination] = useState({ limit: 20, offset: 0 });
  const [showFilters, setShowFilters] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);

  const { filters, updateFilter, clearFilters, hasActiveFilters } = useFilters({
    email: '',
    full_name: '',
    role: 'all' as string,
  });

  useEffect(() => {
    loadUsers();
  }, [filters, pagination]);

  async function loadUsers() {
    setLoading(true);
    try {
      const params: any = {
        limit: pagination.limit,
        offset: pagination.offset,
      };
      if (filters.email) params.email = filters.email;
      if (filters.full_name) params.full_name = filters.full_name;
      if (filters.role !== 'all') params.role = filters.role;
      const response = await getUsers(params);
      setUsers(response.items);
      setTotal(response.total);
    } catch (err) {
      toast.error('Ошибка загрузки пользователей');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleFilterChange = (key: string, value: any) => {
    updateFilter(key, value);
    setPagination(prev => ({ ...prev, offset: 0 }));
  };

  const handleClearFilters = () => {
    clearFilters();
    setPagination({ limit: 20, offset: 0 });
  };

  const handleSelectAll = (checked: boolean) => {
    setSelectedUsers(checked ? users.map(u => u.id) : []);
  };

  const handleSelectOne = (id: string, checked: boolean) => {
    setSelectedUsers(prev => (checked ? [...prev, id] : prev.filter(x => x !== id)));
  };

  const handleBulkDelete = async () => {
    if (!permissions.canDeleteUser) {
      toast.error('У вас нет прав на удаление пользователей');
      return;
    }
    const usersToDelete = selectedUsers.filter(id => id !== user.id);
    if (usersToDelete.length === 0) {
      toast.error('Нельзя удалить свою учётную запись');
      return;
    }
    if (!window.confirm(`Удалить ${usersToDelete.length} пользователей?`)) return;
    try {
      await Promise.all(usersToDelete.map(id => deleteUser(id)));
      toast.success('Пользователи удалены');
      setSelectedUsers([]);
      loadUsers();
    } catch (err) {
      toast.error('Ошибка при удалении');
    }
  };

  const filterFields: FilterField[] = useMemo(
    () => [
      { key: 'email', label: 'Email', type: 'text', placeholder: 'Email пользователя' },
      { key: 'full_name', label: 'ФИО', type: 'text', placeholder: 'ФИО' },
      {
        key: 'role',
        label: 'Роль',
        type: 'select',
        options: [
          { value: 'ADMIN', label: 'Администратор' },
          { value: 'HR', label: 'HR' },
          { value: 'MANAGER', label: 'Менеджер' },
          { value: 'TECH_SPEC', label: 'Технический специалист' },
        ],
      },
    ],
    []
  );

  const getRoleLabel = (role: string): string => {
    const roleMap: Record<string, string> = {
      'ADMIN': 'Администратор',
      'HR': 'HR',
      'MANAGER': 'Менеджер',
      'TECH_SPEC': 'Технический специалист',
    };
    return roleMap[role] || role;
  };

  const getRoleBadgeClass = (role: string): string => {
    const classMap: Record<string, string> = {
      'ADMIN': 'badge-danger',
      'HR': 'badge-success',
      'MANAGER': 'badge-primary',
      'TECH_SPEC': 'badge-warning',
    };
    return classMap[role] || 'badge';
  };

  const columns: Column<User>[] = [
    { key: 'email', header: 'Email' },
    { key: 'full_name', header: 'ФИО' },
    { key: 'role', header: 'Роль', render: u => <span className={`badge ${getRoleBadgeClass(u.role)}`}>{getRoleLabel(u.role)}</span> },
  ];

  if (!permissions.canViewUsers) {
    return (
      <div className="content">
        <div className="page-header"><h2>Управление пользователями</h2></div>
        <div className="table-container" style={{ padding: '2rem', textAlign: 'center' }}>
          <p>У вас нет доступа к этому разделу.</p>
          <p style={{ fontSize: '0.875rem', color: '#64748b', marginTop: '0.5rem' }}>Только администраторы могут управлять пользователями.</p>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(total / pagination.limit);
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;

  return (
    <div className="content">
      <div className="page-header">
        <h2>Управление пользователями {total > 0 && `(${total})`}</h2>
        <div className="btn-group">
          {selectedUsers.length > 0 && permissions.canDeleteUser && (
            <button className="btn btn-danger" onClick={handleBulkDelete}>
              🗑️ Удалить ({selectedUsers.length})
            </button>
          )}
          <button className="btn" onClick={() => setShowFilters(!showFilters)}>
            🔍 Фильтры {hasActiveFilters && '●'}
          </button>
          {permissions.canCreateUser && (
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
              ➕ Добавить пользователя
            </button>
          )}
        </div>
      </div>

      <FilterBar fields={filterFields} filters={filters} onFilterChange={handleFilterChange} onClear={handleClearFilters} hasActiveFilters={hasActiveFilters} isVisible={showFilters} />

      {loading ? (
        <div>Загрузка...</div>
      ) : (
        <>
          <DataTable
            columns={columns}
            data={users}
            keyExtractor={u => u.id}
            selectedIds={selectedUsers}
            onSelect={handleSelectOne}
            onSelectAll={handleSelectAll}
            emptyMessage="Нет пользователей"
          />
          {totalPages > 1 && (
            <div className="pagination" style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1rem' }}>
              <button className="btn btn-sm" disabled={pagination.offset === 0} onClick={() => setPagination(prev => ({ ...prev, offset: prev.offset - prev.limit }))}>
                ← Назад
              </button>
              <span style={{ padding: '0.25rem 0.5rem' }}>Страница {currentPage} из {totalPages}</span>
              <button className="btn btn-sm" disabled={pagination.offset + pagination.limit >= total} onClick={() => setPagination(prev => ({ ...prev, offset: prev.offset + prev.limit }))}>
                Вперёд →
              </button>
            </div>
          )}
        </>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <CreateUserForm onSuccess={() => { setShowModal(false); setPagination({ limit: 20, offset: 0 }); loadUsers(); }} onCancel={() => setShowModal(false)} />
          </div>
        </div>
      )}
    </div>
  );
}
