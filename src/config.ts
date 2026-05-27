/**
 * Application configuration
 */

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export const FREE_TIER_LIMITS = {
  LINKS_PER_MONTH: 5,
  CLICKS_PER_LINK: 100,
};

export const PREMIUM_FEATURES = {
  UNLIMITED_LINKS: true,
  CUSTOM_DOMAINS: true,
  ANALYTICS: true,
  API_ACCESS: true,
};

export const REDIRECT_TIMEOUT = 5000; // ms

export const AUTH_TOKEN_KEY = 'miniurl_token';
export const USER_KEY = 'miniurl_user';
