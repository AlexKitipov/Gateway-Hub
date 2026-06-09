import React, { createContext, useReducer, useCallback, ReactNode } from 'react';
import { User, AuthContextType } from '../types';
import { authAPI } from '../services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'RESTORE_TOKEN'; payload: { user: User | null; token: string | null } };

const initialState: AuthState = {
  user: null,
  token: null,
  loading: true,
  error: null,
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, loading: true, error: null };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        loading: false,
        user: action.payload.user,
        token: action.payload.token,
      };
    case 'LOGIN_ERROR':
      return { ...state, loading: false, error: action.payload };
    case 'LOGOUT':
      return { ...state, user: null, token: null };
    case 'RESTORE_TOKEN':
      return {
        ...state,
        loading: false,
        user: action.payload.user,
        token: action.payload.token,
      };
    default:
      return state;
  }
};

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Restore token from localStorage on mount
  React.useEffect(() => {
    const restoreToken = () => {
      const token = localStorage.getItem('access_token');
      const userStr = localStorage.getItem('user');
      const user = userStr ? JSON.parse(userStr) : null;

      dispatch({
        type: 'RESTORE_TOKEN',
        payload: { token, user },
      });
    };

    restoreToken();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await authAPI.login(email, password);
      const { user, access_token, refresh_token } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user', JSON.stringify(user));

      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user, token: access_token },
      });
    } catch (error: any) {
      const message = error.response?.data?.error?.message || 'Login failed';
      dispatch({ type: 'LOGIN_ERROR', payload: message });
      throw error;
    }
  }, []);

  const register = useCallback(
    async (email: string, password: string, full_name?: string) => {
      dispatch({ type: 'LOGIN_START' });
      try {
        const response = await authAPI.register(email, password, full_name);
        const { user, access_token, refresh_token } = response.data;

        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        localStorage.setItem('user', JSON.stringify(user));

        dispatch({
          type: 'LOGIN_SUCCESS',
          payload: { user, token: access_token },
        });
      } catch (error: any) {
        const message = error.response?.data?.error?.message || 'Registration failed';
        dispatch({ type: 'LOGIN_ERROR', payload: message });
        throw error;
      }
    },
    []
  );

  const logout = useCallback(async () => {
    try {
      await authAPI.logout();
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      dispatch({ type: 'LOGOUT' });
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user: state.user,
        token: state.token,
        loading: state.loading,
        login,
        register,
        logout,
        isAuthenticated: Boolean(state.user && state.token),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
