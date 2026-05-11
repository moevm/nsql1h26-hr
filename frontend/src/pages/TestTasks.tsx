import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { DataTable, Column } from "../components/DataTable";
import { FilterBar } from "../components/FilterBar";
import { useFilters } from "../hooks/useFilters";
import { FilterField } from "../types/filters";
import { toast } from "sonner";
import {
  getTestTasks,
  deleteTestTask,
  getVacancies,
  TestTask,
  Vacancy,
} from "../api";
import { usePermissions } from "../hooks/usePermissions";
import { CreateTestTaskForm } from "../components/CreateTestTaskForm";
import "../styles/App.css";

export function TestTasks() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const permissions = usePermissions(user?.role);

  const [assignments, setAssignments] = useState<TestTask[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [pagination, setPagination] = useState({ limit: 20, offset: 0 });
  const [showFilters, setShowFilters] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedAssignments, setSelectedAssignments] = useState<string[]>([]);

  const { filters, updateFilter, clearFilters, hasActiveFilters } = useFilters({
    title: "",
    vacancy_id: "all",
    createdFrom: "",
    createdTo: "",
  });

  useEffect(() => {
    loadVacancies();
  }, []);

  useEffect(() => {
    loadTestTasks();
  }, [filters, pagination]);

  async function loadVacancies() {
    try {
      const response = await getVacancies({ limit: 200 });
      setVacancies(response.items);
    } catch (err) {
      console.error("Failed to load vacancies:", err);
    }
  }

  async function loadTestTasks() {
    setLoading(true);
    try {
      const params: any = {
        limit: pagination.limit,
        offset: pagination.offset,
      };
      if (filters.title) params.title = filters.title;
      if (filters.vacancy_id !== "all") params.vacancy_id = filters.vacancy_id;
      if (filters.createdFrom) {
        params.created_at_from = Math.floor(
          new Date(filters.createdFrom).getTime() / 1000,
        );
      }
      if (filters.createdTo) {
        params.created_at_to = Math.floor(
          new Date(filters.createdTo).getTime() / 1000,
        );
      }
      const response = await getTestTasks(params);
      setAssignments(response.items);
      setTotal(response.total);
    } catch (err) {
      toast.error("Ошибка загрузки тестовых заданий");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleFilterChange = (key: string, value: any) => {
    updateFilter(key, value);
    setPagination((prev) => ({ ...prev, offset: 0 }));
  };

  const handleClearFilters = () => {
    clearFilters();
    setPagination({ limit: 20, offset: 0 });
  };

  const handleSelectAll = (checked: boolean) => {
    setSelectedAssignments(checked ? assignments.map((a) => a.id) : []);
  };

  const handleSelectOne = (id: string, checked: boolean) => {
    setSelectedAssignments((prev) =>
      checked ? [...prev, id] : prev.filter((x) => x !== id),
    );
  };

  const handleBulkDelete = async () => {
    if (!permissions.canDeleteTestTask) {
      toast.error("У вас нет прав на удаление тестовых заданий");
      return;
    }
    if (!window.confirm(`Удалить ${selectedAssignments.length} заданий?`))
      return;
    try {
      await Promise.all(selectedAssignments.map((id) => deleteTestTask(id)));
      toast.success("Задания удалены");
      setSelectedAssignments([]);
      loadTestTasks();
    } catch (err) {
      toast.error("Ошибка при удалении");
    }
  };

  const filterFields: FilterField[] = useMemo(() => {
    const vacancyOptions = vacancies.map((v) => ({
      value: v.id,
      label: v.title,
    }));
    return [
      {
        key: "title",
        label: "Название",
        type: "text",
        placeholder: "Название задания",
      },
      {
        key: "vacancy_id",
        label: "Вакансия",
        type: "select",
        options: vacancyOptions,
      },
      { key: "createdFrom", label: "Создано с", type: "date" },
      { key: "createdTo", label: "Создано по", type: "date" },
    ];
  }, [vacancies]);

  const columns: Column<TestTask>[] = [
    { key: "title", header: "Название" },
    {
      key: "test_task_url",
      header: "Ссылка",
      render: (a) =>
        a.test_task_url ? (
          <a
            href={a.test_task_url}
            target="_blank"
            rel="noreferrer"
            className="btn btn-sm"
          >
            Открыть
          </a>
        ) : (
          "—"
        ),
    },
    {
      key: "vacancy_id",
      header: "Вакансия",
      render: (a) => vacancies.find((v) => v.id === a.vacancy_id)?.title || "—",
    },
  ];

  const totalPages = Math.ceil(total / pagination.limit);
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;

  return (
    <div className="content">
      <div className="page-header">
        <h2>Тестовые задания {total > 0 && `(${total})`}</h2>
        <div className="btn-group">
          {selectedAssignments.length > 0  && permissions.canDeleteTestTask && (
            <button className="btn btn-danger" onClick={handleBulkDelete}>
              🗑️ Удалить ({selectedAssignments.length})
            </button> 
          	)}
          <button className="btn" onClick={() => setShowFilters(!showFilters)}>
            🔍 Фильтры {hasActiveFilters && "●"}
          </button>
          {permissions.canCreateTestTask && (
            <button
              className="btn btn-primary"
              onClick={() => setShowModal(true)}
            >
              ➕ Добавить задание
            </button>
          )}
        </div>
      </div>

      <FilterBar
        fields={filterFields}
        filters={filters}
        onFilterChange={handleFilterChange}
        onClear={handleClearFilters}
        hasActiveFilters={hasActiveFilters}
        isVisible={showFilters}
      />

      {loading ? (
        <div>Загрузка...</div>
      ) : (
        <>
          <DataTable
            columns={columns}
            data={assignments}
            keyExtractor={(a) => a.id}
            selectedIds={selectedAssignments}
            onSelect={handleSelectOne}
            onSelectAll={handleSelectAll}
            emptyMessage="Нет тестовых заданий"
            actions={(a) => (
              <button
                className="btn btn-sm"
                onClick={() => navigate(`/vacancies/${a.vacancy_id}`)}
                title="Просмотр деталей"
              >
                👁️
              </button>
            )}
          />
          {totalPages > 1 && (
            <div
              className="pagination"
              style={{
                display: "flex",
                justifyContent: "center",
                gap: "0.5rem",
                marginTop: "1rem",
              }}
            >
              <button
                className="btn btn-sm"
                disabled={pagination.offset === 0}
                onClick={() =>
                  setPagination((prev) => ({
                    ...prev,
                    offset: prev.offset - prev.limit,
                  }))
                }
              >
                ← Назад
              </button>
              <span style={{ padding: "0.25rem 0.5rem" }}>
                Страница {currentPage} из {totalPages}
              </span>
              <button
                className="btn btn-sm"
                disabled={pagination.offset + pagination.limit >= total}
                onClick={() =>
                  setPagination((prev) => ({
                    ...prev,
                    offset: prev.offset + prev.limit,
                  }))
                }
              >
                Вперёд →
              </button>
            </div>
          )}
        </>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <CreateTestTaskForm
              vacancies={vacancies}
              onSuccess={() => {
                setShowModal(false);
                setPagination({ limit: 20, offset: 0 });
                loadTestTasks();
              }}
              onCancel={() => setShowModal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
