// ========== Пользователи ==========
export type UserRole = "ADMIN" | "HR" | "TECH_SPEC" | "MANAGER";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
}

// ========== Вакансии ==========
export type VacancyStatus = "OPEN" | "CLOSED";

export interface Vacancy {
  id: string; 
  title: string;
  description: string;
  status: VacancyStatus;
  created_at: number;
  closed_at?: number;
}

// ========== Тестовые задания ==========
export interface TestTask {
  id: string;
  title: string;
  test_task_url: string;
  vacancy_id: string; 
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
  id: string;
  full_name: string;
  email: string;
  phone: string;
  resume_url?: string;
  status: CandidateStatus;
  vacancy_id: string; 
  test_task_id?: string; 
}

// ========== Интервью ==========
export type InterviewResult =
  | "AWAIT_INTERVIEW"
  | "INTERVIEW_PASSED"
  | "INTERVIEW_FAILED";

export interface Interview {
  id: string;
  candidate_id: string;
  tech_spec_id: string; 
  scheduled_at: number;
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
  id: string;
  candidate_id: string;
  vacancy_id: string;
  created_by: string; 
  salary: number;
  start_at: number; 
  status: OfferStatus;
}

// ========== Вспомогательные типы для фильтров ==========
export type FilterFieldType = "text" | "select" | "date" | "datetime-local";

export interface FilterField {
  key: string; 
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
