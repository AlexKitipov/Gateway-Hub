import axios, { AxiosError, AxiosInstance } from 'axios';
import {
  AuthResponse,
  CreateLinkRequest,
  DeleteLinkResponse,
  ErrorResponse,
  LinkListResponse,
  LinkResponse,
  UpgradeResponse,
  User,
  UserStats,
} from '../types';
import { API_URL } from '../config';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
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
          const response = await axios.post<AuthResponse>(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token, user } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          localStorage.setItem('user', JSON.stringify(user));

          // Retry original request
          return apiClient(error.config!);
        } catch {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
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
    apiClient.post<AuthResponse>('/auth/refresh', { refresh_token: refreshToken }),
};

// User endpoints
export const userAPI = {
  getMe: () => apiClient.get<User>('/users/me'),
  getStats: () => apiClient.get<UserStats>('/users/stats'),
  upgrade: () => apiClient.post<UpgradeResponse>('/users/upgrade'),
};

// Links endpoints
export const linksAPI = {
  getAll: (skip = 0, limit = 50) =>
    apiClient.get<LinkListResponse>('/links/', { params: { skip, limit } }),

  getOne: (code: string) => apiClient.get<LinkResponse>(`/links/${code}`),

  create: (data: CreateLinkRequest) =>
    apiClient.post<LinkResponse>('/links/create', data),

  delete: (code: string) => apiClient.delete<DeleteLinkResponse>(`/links/${code}`),

  getAnalytics: (code: string, days = 30) =>
    apiClient.get(`/analytics/${code}`, { params: { days } }),
};

export { API_BASE_URL, API_URL } from '../config';
