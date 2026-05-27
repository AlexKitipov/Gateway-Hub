import axios from 'axios';
import { API_URL } from '../config';
import { ApiResponse, AuthTokens, ShortLink, User, UserStats } from '../types';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
}

export const authApi = {
  login: (payload: LoginPayload) => api.post<ApiResponse<{ user: User; tokens: AuthTokens }>>('/auth/login', payload),
  register: (payload: RegisterPayload) => api.post<ApiResponse<{ user: User; tokens: AuthTokens }>>('/auth/register', payload),
  me: () => api.get<ApiResponse<User>>('/auth/me'),
};

export const linksApi = {
  getAll: () => api.get<ApiResponse<ShortLink[]>>('/links'),
  create: (payload: { originalUrl: string }) => api.post<ApiResponse<ShortLink>>('/links', payload),
  update: (id: string, payload: { originalUrl?: string }) => api.patch<ApiResponse<ShortLink>>(`/links/${id}`, payload),
  remove: (id: string) => api.delete<ApiResponse<{ id: string }>>(`/links/${id}`),
  stats: () => api.get<ApiResponse<UserStats>>('/links/stats'),
};

export default api;
