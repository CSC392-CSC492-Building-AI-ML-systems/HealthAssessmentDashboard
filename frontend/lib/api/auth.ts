import { httpClient } from './core/http-client';
import {
  ApiResponse,
  AuthResponse,
  SignupPayload,
  UserCredentials,
} from './types';

/**
 * Authentication API endpoints
 */
export const authApi = {
  /**
   * Sign up a new user
   */
  signup: async (userData: SignupPayload): Promise<ApiResponse<AuthResponse>> => {
    return httpClient<AuthResponse>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(userData),
      skipAuth: true, // Don't need auth for signup
    });
  },

  /**
   * Login user with email and password
   */
  login: async (credentials: UserCredentials): Promise<ApiResponse<AuthResponse>> => {
    const formData = new URLSearchParams({
      username: credentials.email,
      password: credentials.password,
    });

    return httpClient<AuthResponse>('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
      skipAuth: true,
    });
  },

  /**
   * Logout user and clear credentials
   */
  logout: async (): Promise<void> => {
    try {
      await httpClient('/auth/logout', {
        method: 'POST',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Get stored access token
   */
  getAccessToken: (): string | null => {
    return localStorage.getItem('access_token');
  },

  /**
   * Clear authentication data
   */
  clearAuth: (): void => {
    localStorage.removeItem('access_token');
  },

  /**
   * Get current auth state
   */
  getAuthState: async (): Promise<ApiResponse<AuthResponse>> => {
    return httpClient<AuthResponse>('/auth/me');
  },
};
