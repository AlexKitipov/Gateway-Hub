import axios, { AxiosError, AxiosInstance } from 'axios';
import { AuthResponse, LinkResponse, ErrorResponse } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ErrorResponse>) => {
    if (error.response?.status === 401) {
      // Try to refresh token
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const newAccessToken = response.data.access_token;
          localStorage.setItem('access_token', newAccessToken);

          // Retry original request
          return apiClient(error.config!);
        } catch {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  register: (email: string, password: string, full_name?: string) =>
    apiClient.post<AuthResponse>('/auth/register', {
      email,
      password,
      full_name,
    }),

  login: (email: string, password: string) =>
    apiClient.post<AuthResponse>('/auth/login', {
      email,
      password,
    }),

  logout: () => apiClient.post('/auth/logout'),

  refresh: (refreshToken: string) =>
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
};

// User endpoints
export const userAPI = {
  getMe: () => apiClient.get('/users/me'),
  getStats: () => apiClient.get('/users/stats'),
  upgrade: (plan: string) =>
    apiClient.post('/users/upgrade', { plan }),
};

// Links endpoints
export const linksAPI = {
  getAll: (skip = 0, limit = 50) =>
    apiClient.get(`/links?skip=${skip}&limit=${limit}`),

  getOne: (code: string) => apiClient.get(`/links/${code}`),

  create: (targetUrl: string, title?: string, description?: string) =>
    apiClient.post<LinkResponse>('/links/create', {
      target_url: targetUrl,
      title,
      description,
    }),

  delete: (code: string) => apiClient.delete(`/links/${code}`),

  getAnalytics: (code: string, days = 30) =>
    apiClient.get(`/analytics/${code}?days=${days}`),
};
