const BASE_URL = '/api/v1';

export function getStoredToken(): string | null {
  return localStorage.getItem('careerloom_token');
}

export function setStoredToken(token: string | null) {
  if (token) {
    localStorage.setItem('careerloom_token', token);
  } else {
    localStorage.removeItem('careerloom_token');
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getStoredToken();
  const headers = new Headers(options.headers || {});

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'An unexpected error occurred.';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch {
      errorDetail = `Request failed with status ${response.status} (${response.statusText})`;
    }
    throw new Error(errorDetail);
  }

  return response.json() as Promise<T>;
}

export const api = {
  auth: {
    login: (credentials: { email: string; password: string }) =>
      request<{ access_token: string; user: any }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      }),
    register: (data: { email: string; password: string; full_name: string; preferred_role?: string }) =>
      request<{ access_token: string; user: any }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    me: () => request<any>('/auth/me'),
  },

  profile: {
    get: () => request<any>('/profile/'),
    update: (data: any) =>
      request<any>('/profile/', {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    addSkill: (skill: { skill_name: string; proficiency_level?: string; category?: string }) =>
      request<any>('/profile/skills', {
        method: 'POST',
        body: JSON.stringify(skill),
      }),
    deleteSkill: (id: string) =>
      request<any>(`/profile/skills/${id}`, {
        method: 'DELETE',
      }),
    addProject: (project: { title: string; description: string; skills_used: string[]; demo_url?: string; repo_url?: string }) =>
      request<any>('/profile/projects', {
        method: 'POST',
        body: JSON.stringify(project),
      }),
    deleteProject: (id: string) =>
      request<any>(`/profile/projects/${id}`, {
        method: 'DELETE',
      }),
    claimAction: (claim_id: string, action: 'approve' | 'reject', user_correction?: string) =>
      request<any>('/profile/claims/action', {
        method: 'POST',
        body: JSON.stringify({ claim_id, action, user_correction }),
      }),
  },

  documents: {
    upload: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return request<any>('/documents/upload', {
        method: 'POST',
        body: formData,
      });
    },
    list: () => request<any[]>('/documents/'),
    get: (id: string) => request<any>(`/documents/${id}`),
    delete: (id: string) =>
      request<any>(`/documents/${id}`, {
        method: 'DELETE',
      }),
  },

  jobs: {
    list: (params?: { q?: string; work_arrangement?: string; min_match?: number; sort?: string }) => {
      const search = new URLSearchParams();
      if (params?.q) search.append('q', params.q);
      if (params?.work_arrangement) search.append('work_arrangement', params.work_arrangement);
      if (params?.min_match) search.append('min_match', String(params.min_match));
      if (params?.sort) search.append('sort', params.sort);
      return request<any[]>(`/jobs/?${search.toString()}`);
    },
    get: (id: string) => request<any>(`/jobs/${id}`),
    submit: (data: any) =>
      request<any>('/jobs/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    retrieveUrl: (url: string) =>
      request<any>('/jobs/retrieve-url', {
        method: 'POST',
        body: JSON.stringify({ url }),
      }),
    save: (jobId: string, status: 'saved' | 'dismissed', notes?: string) =>
      request<any>(`/jobs/${jobId}/save`, {
        method: 'POST',
        body: JSON.stringify({ status, notes }),
      }),
    getSaved: () => request<any[]>('/jobs/saved/all'),
  },

  assessments: {
    evaluate: (data: {
      title: string;
      employer: string;
      description: string;
      employer_domain?: string;
      contact_email?: string;
      contact_messaging?: string;
      salary_text?: string;
      application_url?: string;
    }) =>
      request<any>('/assessments/evaluate', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    benchmark: () => request<any>('/assessments/benchmark'),
  },

  careerPlans: {
    current: () => request<any>('/career-plans/current'),
    generate: (target_role: string, target_job_id?: string) =>
      request<any>('/career-plans/generate', {
        method: 'POST',
        body: JSON.stringify({ target_role, target_job_id }),
      }),
    updateTask: (taskId: string, status: string, completion_evidence?: string, skip_reason?: string) =>
      request<any>(`/career-plans/tasks/${taskId}`, {
        method: 'PUT',
        body: JSON.stringify({ status, completion_evidence, skip_reason }),
      }),
    addCustomTask: (task: any) =>
      request<any>('/career-plans/tasks', {
        method: 'POST',
        body: JSON.stringify(task),
      }),
  },

  applications: {
    list: () => request<any>('/applications/'),
    create: (job_id: string, stage?: string, notes?: string) =>
      request<any>('/applications/', {
        method: 'POST',
        body: JSON.stringify({ job_id, stage, notes }),
      }),
    updateStage: (appId: string, stage: string) =>
      request<any>(`/applications/${appId}/stage`, {
        method: 'PUT',
        body: JSON.stringify({ stage }),
      }),
    delete: (appId: string) =>
      request<any>(`/applications/${appId}`, {
        method: 'DELETE',
      }),
  },

  interviews: {
    createSession: (role_title: string, interview_type?: string, job_id?: string) =>
      request<any>('/interviews/sessions', {
        method: 'POST',
        body: JSON.stringify({ role_title, interview_type, job_id }),
      }),
    getSession: (id: string) => request<any>(`/interviews/sessions/${id}`),
    submitPractice: (question_id: string, user_response: string) =>
      request<any>('/interviews/practice', {
        method: 'POST',
        body: JSON.stringify({ question_id, user_response }),
      }),
  },

  resumes: {
    list: () => request<any>('/resumes/'),
    generate: (data: any) =>
      request<any>('/resumes/generate', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    getContent: (resumeId: string) => request<any>(`/resumes/${resumeId}/content`),
    share: (resume_id: string, employer_name: string, contact_visibility?: string) =>
      request<any>('/resumes/share', {
        method: 'POST',
        body: JSON.stringify({ resume_id, employer_name, contact_visibility }),
      }),
    revoke: (share_id: string) =>
      request<any>(`/resumes/shares/${share_id}/revoke`, {
        method: 'POST',
      }),
  },

  fairness: {
    audit: () => request<any>('/fairness/audit'),
  },

  dashboard: {
    summary: () => request<any>('/dashboard/summary'),
  },

  audit: {
    history: () => request<any[]>('/audit/history'),
  },

  reports: {
    submit: (job_id: string, reason: string, details?: string) =>
      request<any>('/reports/', {
        method: 'POST',
        body: JSON.stringify({ job_id, reason, details }),
      }),
    mine: () => request<any[]>('/reports/mine'),
  },
};
