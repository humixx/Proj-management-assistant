import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Add auth token and project ID headers to all requests
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // Auth token
  try {
    const authStore = localStorage.getItem('auth-store');
    if (authStore) {
      const parsed = JSON.parse(authStore);
      const token = parsed?.state?.token;
      if (token && config.headers) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
    }
  } catch {
    // Ignore parse errors
  }

  // Project ID
  const projectId = localStorage.getItem('currentProjectId');
  if (projectId && config.headers) {
    config.headers['X-Project-ID'] = projectId;
  }
  return config;
});

// Error handling with 401 auto-logout
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const data = error.response?.data as any;
    console.error('API Error:', data?.detail || error.message);

    // Auto-logout on 401 (skip for auth endpoints to avoid loop)
    if (error.response?.status === 401 && !error.config?.url?.startsWith('/auth/')) {
      // Clear auth state
      localStorage.removeItem('auth-store');
      document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      // Redirect to login
      if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
        window.location.href = '/login';
      }
    }

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
