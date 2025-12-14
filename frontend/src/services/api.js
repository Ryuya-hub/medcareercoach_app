import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター：トークンを自動付与
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター：エラーハンドリング
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // トークン期限切れの場合、ログアウト処理
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 認証API
export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (data) => api.post('/api/auth/register', data),
  verify: () => api.get('/api/auth/verify'),
  logout: () => api.post('/api/auth/logout'),
};

// コーチAPI
export const coachesAPI = {
  getMe: () => api.get('/api/coaches/me'),
  getAll: () => api.get('/api/coaches'),
  getById: (id) => api.get(`/api/coaches/${id}`),
  update: (id, data) => api.put(`/api/coaches/${id}`, data),
};

// 顧客API
export const clientsAPI = {
  getMe: () => api.get('/api/clients/me'),
  getAll: () => api.get('/api/clients'),
  getById: (id) => api.get(`/api/clients/${id}`),
  create: (data) => api.post('/api/clients', data),
  update: (id, data) => api.put(`/api/clients/${id}`, data),
  delete: (id) => api.delete(`/api/clients/${id}`),
  addCoach: (clientId, coachId) => api.post(`/api/clients/${clientId}/coaches/${coachId}`),
  removeCoach: (clientId, coachId) => api.delete(`/api/clients/${clientId}/coaches/${coachId}`),
};

// 応募企業API
export const applicationsAPI = {
  getAll: (params) => api.get('/api/applications', { params }),
  getById: (id) => api.get(`/api/applications/${id}`),
  create: (data) => api.post('/api/applications', data),
  update: (id, data) => api.put(`/api/applications/${id}`, data),
  delete: (id) => api.delete(`/api/applications/${id}`),
  getHistory: (id) => api.get(`/api/applications/history/${id}`),
  getCompanyAnalysis: (name) => api.get(`/api/applications/companies/${name}/analysis`),
  getAllCompanies: () => api.get('/api/applications/companies/analysis'),
};

// 面談予約API
export const appointmentsAPI = {
  getAll: (params) => api.get('/api/appointments', { params }),
  getById: (id) => api.get(`/api/appointments/${id}`),
  create: (data) => api.post('/api/appointments', data),
  update: (id, data) => api.put(`/api/appointments/${id}`, data),
  cancel: (id) => api.delete(`/api/appointments/${id}`),
  approve: (id) => api.post(`/api/appointments/${id}/approve`),
  reject: (id) => api.post(`/api/appointments/${id}/reject`),
  getAllCoachAvailability: (params) => api.get('/api/appointments/coach-availability', { params }),
  getCoachAvailability: (coachId, params) =>
    api.get(`/api/appointments/coach-availability/${coachId}`, { params }),
  createAvailability: (data) => api.post('/api/appointments/coach-availability', data),
  deleteAvailability: (id) => api.delete(`/api/appointments/coach-availability/${id}`),
};

// 職務経歴書API
export const resumesAPI = {
  getMe: () => api.get('/api/resumes/me'),
  getClientResumes: (clientId) => api.get(`/api/resumes/client/${clientId}`),
  getById: (id) => api.get(`/api/resumes/${id}`),
  create: (data) => api.post('/api/resumes', data),
  update: (id, data) => api.put(`/api/resumes/${id}`, data),
  submit: (id) => api.post(`/api/resumes/${id}/submit`),
  delete: (id) => api.delete(`/api/resumes/${id}`),

  // 職務経歴
  getWorkExperiences: (resumeId) => api.get(`/api/resumes/${resumeId}/work-experiences`),
  createWorkExperience: (resumeId, data) =>
    api.post(`/api/resumes/${resumeId}/work-experiences`, data),
  updateWorkExperience: (id, data) => api.put(`/api/resumes/work-experiences/${id}`, data),
  deleteWorkExperience: (id) => api.delete(`/api/resumes/work-experiences/${id}`),

  // 学歴
  getEducation: (resumeId) => api.get(`/api/resumes/${resumeId}/education`),
  createEducation: (resumeId, data) => api.post(`/api/resumes/${resumeId}/education`, data),

  // 資格
  getCertifications: (resumeId) => api.get(`/api/resumes/${resumeId}/certifications`),
  createCertification: (resumeId, data) =>
    api.post(`/api/resumes/${resumeId}/certifications`, data),

  // スキル
  getSkills: (resumeId) => api.get(`/api/resumes/${resumeId}/skills`),
  createSkill: (resumeId, data) => api.post(`/api/resumes/${resumeId}/skills`, data),

  // 添削
  getPendingResumes: () => api.get('/api/resumes/coach/pending'),
  getReviews: (resumeId) => api.get(`/api/resumes/${resumeId}/reviews`),
  createReview: (resumeId, data) => api.post(`/api/resumes/${resumeId}/reviews`, data),
  createComment: (reviewId, data) => api.post(`/api/resumes/reviews/${reviewId}/comments`, data),
  completeReview: (reviewId) => api.post(`/api/resumes/reviews/${reviewId}/complete`),
  applyReview: (resumeId, reviewId) => api.post(`/api/resumes/${resumeId}/apply-review/${reviewId}`),
  deleteByCoach: (id) => api.delete(`/api/resumes/${id}/coach`),
};

export default api;
