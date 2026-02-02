import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Add project ID header to all requests
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const projectId = localStorage.getItem('currentProjectId');
  if (projectId && config.headers) {
    config.headers['X-Project-ID'] = projectId;
  }
  return config;
});

// Error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const data = error.response?.data as any;
    console.error('API Error:', data?.detail || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;

export const setCurrentProjectId = (projectId: string | null) => {
  if (projectId) localStorage.setItem('currentProjectId', projectId);
  else localStorage.removeItem('currentProjectId');
};

export const getCurrentProjectId = (): string | null => {
  if (typeof window !== 'undefined') return localStorage.getItem('currentProjectId');
  return null;
};
