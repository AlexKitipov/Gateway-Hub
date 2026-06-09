const configuredApiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const API_BASE_URL = configuredApiUrl
  .replace(/\/api\/v1\/?$/, '')
  .replace(/\/api\/?$/, '')
  .replace(/\/$/, '');
export const API_URL = `${API_BASE_URL}/api/v1`;

export const FREE_LINK_LIMIT = 5;
export const FREE_CLICK_LIMIT = 100;

export const FREE_TIER_LIMITS = {
  LINKS_PER_MONTH: FREE_LINK_LIMIT,
  CLICKS_PER_LINK: FREE_CLICK_LIMIT,
} as const;

export const TOKEN_KEY = 'access_token';
export const REFRESH_TOKEN_KEY = 'refresh_token';
export const USER_KEY = 'user';
