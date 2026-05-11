// src/types.ts

// ========== Пользователи ==========
export type UserRole = "ADMIN" | "HR" | "TECH_SPEC" | "MANAGER";

export interface User {
  id: string; // user_id
  email: string;
  full_name: string;
  role: UserRole;
  // password_hash не включаем в ответы API
}

// ========== Вакансии ==========
export type VacancyStatus = "OPEN" | "CLOSED";

export interface Vacancy {
  id: string; // vacancy_id
  title: string;
  description: string;
  status: VacancyStatus;
  created_at: number; // Unix timestamp (секунды)
  closed_at?: number; // Unix timestamp, только если статус CLOSED
}

// ========== Тестовые задания ==========
export interface TestTask {
  id: string; // task_id
  title: string;
  test_task_url: string;
  vacancy_id: string; // связь с вакансией
}

// ========== Кандидаты ==========
export type CandidateStatus =
  | "NEW"
  | "TEST"
  | "AWAIT_INTERVIEW"
  | "INTERVIEW_PASSED"
  | "OFFER"
  | "REJECTED"
  | "HIRED";

export interface Candidate {
  id: string; // candidate_id
  full_name: string;
  email: string;
  phone: string;
  resume_url?: string;
  status: CandidateStatus;
  vacancy_id: string; // связь APPLIES: Candidate → Vacancy (одна вакансия? В API указано vacancy_id)
  test_task_id?: string; // связь COMPLETES: Candidate → TestTask (опционально)
}

// ========== Интервью ==========
export type InterviewResult =
  | "AWAIT_INTERVIEW"
  | "INTERVIEW_PASSED"
  | "INTERVIEW_FAILED";

export interface Interview {
  id: string; // interview_id
  candidate_id: string;
  tech_spec_id: string; // ID пользователя с ролью TECH_SPEC
  scheduled_at: number; // Unix timestamp
  zoom_url?: string;
  feedback?: string;
  result: InterviewResult;
}

// ========== Офферы ==========
export type OfferStatus =
  | "PENDING"
  | "APPROVED_MNG"
  | "REJECTED_MNG"
  | "APPROVED_CND"
  | "REJECTED_CNF";

export interface Offer {
  id: string; // offer_id
  candidate_id: string;
  vacancy_id: string;
  created_by: string; // ID пользователя (MANAGER/HR/ADMIN)
  salary: number;
  start_at: number; // Unix timestamp — дата выхода
  status: OfferStatus;
}

// ========== Вспомогательные типы для фильтров ==========
export type FilterFieldType = "text" | "select" | "date" | "datetime-local";

export interface FilterField {
  key: string; // ключ в объекте filters
  label: string;
  type: FilterFieldType;
  placeholder?: string;
  options?: { value: string; label: string }[]; // для select
}

// ========== Типы для пагинированных ответов ==========
export interface PaginatedResponse<T> {
  total: number;
  items: T[];
}
