import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const processClaim = async (claimData) => {
  const response = await api.post('/api/claims/process', claimData);
  return response.data;
};

export const getPendingClaims = async () => {
  const response = await api.get('/api/dashboard/pending');
  return response.data;
};

export const approveClaim = async (claim_id, reviewer_id) => {
  const response = await api.post('/api/review/approve', {
    claim_id,
    reviewer_id,
    decision: 'APPROVED',
  });
  return response.data;
};

export const rejectClaim = async (claim_id, reviewer_id, override_reason) => {
  const response = await api.post('/api/review/reject', {
    claim_id,
    reviewer_id,
    decision: 'DENIED',
    override_reason,
  });
  return response.data;
};
