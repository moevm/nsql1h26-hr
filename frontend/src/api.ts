const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v2';

function getAccessToken(): string | null {
  return localStorage.getItem('access_token');
}

function setAccessToken(token: string): void {
  localStorage.setItem('access_token', token);
}

function removeAccessToken(): void {
  localStorage.removeItem('access_token');
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAccessToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    removeAccessToken();
    localStorage.removeItem('user');
    window.dispatchEvent(new CustomEvent('auth:unauthorized'));
    throw new Error('Session expired. Please login again.');
  }

  if (!response.ok) {
    let errorMessage = `API error: ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.message || errorData.detail || errorMessage;
    } catch {
      // ignore
    }
    throw new Error(errorMessage);
  }

  if (response.status === 204) {
    return {} as T;
  }
  
  return response.json();
}

export async function login(credentials: { email: string; password: string }) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  const data = await response.json();
  setAccessToken(data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  return data;
}

export async function logout() {
  removeAccessToken();
  localStorage.removeItem('user');
  window.dispatchEvent(new CustomEvent('auth:logout'));
}

// ---------- Users ----------
export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'ADMIN' | 'HR' | 'TECH_SPEC' | 'MANAGER';
}

export async function getUsers(params?: {
  full_name?: string;
  email?: string;
  role?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}): Promise<{ total: number; items: User[] }> {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') searchParams.append(key, String(value));
    });
  }
  const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
  return apiRequest(`/users${query}`);
}

export async function createUser(userData: {
  email: string;
  full_name: string;
  password: string;
  role: string;
}): Promise<User> {
  return apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  });
}

export async function deleteUser(userId: string): Promise<void> {
  return apiRequest(`/users/${userId}`, { method: 'DELETE' });
}

// ---------- Vacancies ----------
export interface Vacancy {
  id: string;
  title: string;
  description: string;
  status: 'OPEN' | 'CLOSED';
  created_at: number;
  closed_at?: number;
}

export async function getVacancies(params?: {
  title?: string;
  description_contains?: string;
  status?: 'OPEN' | 'CLOSED';
  created_at_from?: number;
  created_at_to?: number;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}): Promise<{ total: number; items: Vacancy[] }> {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') searchParams.append(key, String(value));
    });
  }
  const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
  return apiRequest(`/vacancies${query}`);
}

export async function createVacancy(data: {
  title: string;
  description: string;
  status?: 'OPEN' | 'CLOSED';
}): Promise<Vacancy> {
  return apiRequest('/vacancies', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateVacancy(
  id: string,
  data: { title?: string; description?: string; status?: 'OPEN' | 'CLOSED'; closed_at?: number }
): Promise<Vacancy> {
  return apiRequest(`/vacancies/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteVacancy(id: string): Promise<void> {
  return apiRequest(`/vacancies/${id}`, { method: 'DELETE' });
}

// ---------- Test Tasks ----------
export interface TestTask {
  id: string;
  title: string;
  test_task_url: string;
  vacancy_id: string;
  created_at?: number;
}

export async function getTestTasks(params?: {
  title?: string;
  vacancy_id?: string;
  created_at_from?: number;
  created_at_to?: number;
  limit?: number;
  offset?: number;
}): Promise<{ total: number; items: TestTask[] }> {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') searchParams.append(key, String(value));
    });
  }
  const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
  return apiRequest(`/test-tasks${query}`);
}

export async function createTestTask(data: {
  title: string;
  test_task_url: string;
  vacancy_id: string;
}): Promise<TestTask> {
  return apiRequest('/test-tasks', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteTestTask(id: string): Promise<void> {
  return apiRequest(`/test-tasks/${id}`, { method: 'DELETE' });
}

// ---------- Candidates ----------
export interface Candidate {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  resume_url?: string;
  status: 'NEW' | 'TEST' | 'INTERVIEW' | 'OFFER' | 'REJECTED' | 'HIRED';
  vacancy_id: string;
  test_task_id?: string;
  created_at?: number;
}

export async function getCandidates(params?: {
  full_name?: string;
  email?: string;
  phone?: string;
  status?: string;
  vacancy_id?: string;
  created_at_from?: number;
  created_at_to?: number;
  limit?: number;
  offset?: number;
}): Promise<{ total: number; items: Candidate[] }> {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') searchParams.append(key, String(value));
    });
  }
  const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
  return apiRequest(`/candidates${query}`);
}

export async function createCandidate(data: {
  full_name: string;
  email: string;
  phone: string;
  resume_url?: string;
  status: string;
  vacancy_id: string;
  test_task_id?: string;
}): Promise<Candidate> {
  return apiRequest('/candidates', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateCandidate(
  id: string,
  data: Partial<Candidate>
): Promise<Candidate> {
  return apiRequest(`/candidates/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteCandidate(id: string): Promise<void> {
  return apiRequest(`/candidates/${id}`, { method: 'DELETE' });
}

// ---------- Interviews ----------
export interface Interview {
  id: string;
  candidate_id: string;
  vacancy_id: string;
  tech_spec_id: string;
  scheduled_at: number;
  zoom_url?: string;
  feedback?: string;
  result: 'AWAIT_INTERVIEW' | 'INTERVIEW_PASSED' | 'INTERVIEW_FAILED';
}

export async function getInterviews(params?: {
  candidate_id?: string;
  tech_spec_id?: string;
  vacancy_id?: string;
  result?: string;
  scheduled_at_from?: number;
  scheduled_at_to?: number;
  limit?: number;
  offset?: number;
}): Promise<{ total: number; items: Interview[] }> {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') searchParams.append(key, String(value));
    });
  }
  const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
  return apiRequest(`/interviews${query}`);
}

export async function createInterview(data: {
  candidate_id: string;
  tech_spec_id: string;
  scheduled_at: number;
  zoom_url?: string;
}): Promise<Interview> {
  return apiRequest('/interviews', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateInterview(
  id: string,
  data: { feedback: string; result: 'INTERVIEW_PASSED' | 'INTERVIEW_FAILED' }
): Promise<Interview> {
  return apiRequest(`/interviews/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteInterview(id: string): Promise<void> {
  return apiRequest(`/interviews/${id}`, { method: 'DELETE' });
}

// ---------- Offers ----------
export interface Offer {
  id: string;
  candidate_id: string;
  vacancy_id: string;
  created_by: string;
  salary: number;
  start_at: number;
  status: 'PENDING' | 'APPROVED_MNG' | 'REJECTED_MNG' | 'APPROVED_CND' | 'REJECTED_CNF';
  created_at?: number;
}

export async function getOffers(params?: {
  candidate_id?: string;
  vacancy_id?: string;
  status?: string;
  salary_from?: number;
  salary_to?: number;
  created_at_from?: number;
  created_at_to?: number;
  limit?: number;
  offset?: number;
}): Promise<{ total: number; items: Offer[] }> {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') searchParams.append(key, String(value));
    });
  }
  const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
  return apiRequest(`/offers${query}`);
}

export async function createOffer(data: {
  candidate_id: string;
  vacancy_id: string;
  created_by: string;
  salary: number;
  start_at: number;
}): Promise<Offer> {
  return apiRequest('/offers', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateOfferStatus(
  id: string,
  status: 'APPROVED_MNG' | 'REJECTED_MNG' | 'APPROVED_CND' | 'REJECTED_CNF'
): Promise<Offer> {
  return apiRequest(`/offers/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

export async function deleteOffer(id: string): Promise<void> {
  return apiRequest(`/offers/${id}`, { method: 'DELETE' });
}


