export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_premium: boolean;
  is_active: boolean;
  premium_until?: string | null;
  created_at: string;
}

export interface ShortLink {
  id: number;
  code: string;
  target_url: string;
  title: string | null;
  description: string | null;
  click_count: number;
  is_active: boolean;
  created_at: string;
  expires_at: string | null;
  short_url: string;
}

export interface UserStats {
  total_links: number;
  total_clicks: number;
  links_this_month: number;
  is_premium: boolean;
  premium_until: string | null;
}

export interface CreateLinkRequest {
  target_url: string;
  title?: string;
  description?: string;
  custom_code?: string;
  expires_at?: string;
}

export interface LinkListResponse {
  total: number;
  limit: number;
  offset: number;
  links: ShortLink[];
}

export interface DeleteLinkResponse {
  success: boolean;
  message: string;
}

export interface UpgradeResponse {
  success: boolean;
  message: string;
  premium_until: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type LinkResponse = ShortLink;

export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}

export type AuthContextType = {
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, full_name?: string) => Promise<void>;
  logout: () => void;
};

export type LinksContextType = {
  links: ShortLink[];
  stats: UserStats | null;
  isLoading: boolean;
  error: string | null;
  fetchLinks: () => Promise<void>;
  createLink: (data: CreateLinkRequest) => Promise<ShortLink>;
  deleteLink: (code: string) => Promise<void>;
  upgradeAccount: () => Promise<void>;
};
