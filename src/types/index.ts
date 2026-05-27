/**
 * User types
 */
export interface User {
  id: number;
  email: string;
  is_premium: boolean;
  created_at: string;
}

export interface UserStats {
  total_links: number;
  total_clicks: number;
  links_this_month: number;
  plan: 'free' | 'premium';
}

/**
 * Short Link types
 */
export interface ShortLink {
  id: number;
  user_id: number;
  code: string;
  target: string;
  clicks: number;
  created_at: string;
}

export interface CreateLinkRequest {
  target: string;
  custom_code?: string;
}

/**
 * API Response types
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

/**
 * Auth types
 */
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  password_confirm?: string;
}

/**
 * Context types
 */
export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
}

export interface LinksContextType {
  links: ShortLink[];
  isLoading: boolean;
  error: string | null;
  stats: UserStats | null;
  fetchLinks: () => Promise<void>;
  createLink: (data: CreateLinkRequest) => Promise<ShortLink>;
  deleteLink: (code: string) => Promise<void>;
  upgradeAccount: () => Promise<void>;
}
