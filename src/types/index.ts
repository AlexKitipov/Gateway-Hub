export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
}

export interface ShortLink {
  id: string;
  originalUrl: string;
  shortCode: string;
  shortUrl: string;
  clicks: number;
  createdAt: string;
  updatedAt?: string;
}

export interface UserStats {
  totalLinks: number;
  totalClicks: number;
  topLinks: ShortLink[];
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken?: string;
}
