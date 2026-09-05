import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const riskApi = {
  score: (transactionId: string) => api.post(`/risk/score`, { transaction_id: transactionId }),
  getRisk: (transactionId: string) => api.get(`/risk/${transactionId}`),
};

export const casesApi = {
  getAll: () => api.get('/cases'),
  getById: (caseId: string) => api.get(`/cases/${caseId}`),
  updateStatus: (caseId: string, status: string, reason?: string) => 
    api.patch(`/cases/${caseId}/status`, { status, reason }),
};

export const graphApi = {
  getEntity: (entityId: string) => api.get(`/graph/entity/${entityId}`),
  getCase: (caseId: string) => api.get(`/graph/case/${caseId}`),
  getPath: (params: any) => api.get('/graph/path', { params }),
};

export const signalsApi = {
  query: (entityToken: string) => api.post('/signals/query', { entity_token: entityToken }),
  getById: (claimId: string) => api.get(`/signals/${claimId}`),
};

export const evidenceApi = {
  verify: (caseId: string) => api.get(`/evidence/${caseId}/verify`),
};

export const ledgerApi = {
  getClaim: (claimId: string) => api.get(`/ledger/claims/${claimId}`),
  verify: (claimId: string) => api.get(`/ledger/verify/${claimId}`),
};
