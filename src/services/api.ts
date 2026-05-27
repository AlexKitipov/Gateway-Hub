import axios, { AxiosInstance, AxiosError } from 'axios';
import { API_BASE_URL, AUTH_TOKEN_KEY } from '../config';
import {
  AuthResponse,
  LoginCredentials,
  RegisterCredentials,
  ShortLink,
  CreateLinkRequest,
  ApiResponse,
  UserStats,
} from '../types';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem(AUTH_TOKEN_KEY);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Clear auth data on 401
          localStorage.removeItem(AUTH_TOKEN_KEY);
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Authentication endpoints
   */
  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    const response = await this.client.post<ApiResponse<AuthResponse>>(
      '/auth/register',
      credentials
    );
    return response.data.data!;
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.client.post<ApiResponse<AuthResponse>>(
      '/auth/login',
      credentials
    );
    return response.data.data!;
  }

  async logout(): Promise<void> {
    await this.client.post('/auth/logout');
  }

  /**
   * User endpoints
   */
  async getUserStats(): Promise<UserStats> {
    const response = await this.client.get<ApiResponse<UserStats>>(
      '/user/stats'
    );
    return response.data.data!;
  }

  async upgradeAccount(): Promise<void> {
    await this.client.post('/user/upgrade');
  }

  /**
   * Links endpoints
   */
  async getLinks(): Promise<ShortLink[]> {
    const response = await this.client.get<ApiResponse<ShortLink[]>>(
      '/links'
    );
    return response.data.data || [];
  }

  async createLink(data: CreateLinkRequest): Promise<ShortLink> {
    const response = await this.client.post<ApiResponse<ShortLink>>(
      '/links/create',
      data
    );
    return response.data.data!;
  }

  async deleteLink(code: string): Promise<void> {
    await this.client.delete(`/links/${code}`);
  }

  async getLinkAnalytics(code: string): Promise<ShortLink> {
    const response = await this.client.get<ApiResponse<ShortLink>>(
      `/links/${code}/analytics`
    );
    return response.data.data!;
  }

  /**
   * Public redirect endpoint (no auth needed)
   */
  async redirectLink(code: string): Promise<{ target: string }> {
    const response = await this.client.get<{ target: string }>(
      `/redirect/${code}`
    );
    return response.data;
  }
}

export const apiClient = new ApiClient();
