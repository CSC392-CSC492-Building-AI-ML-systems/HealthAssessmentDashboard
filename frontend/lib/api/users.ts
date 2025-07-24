import { httpClient } from './core/http-client';
import {
  ApiResponse,
  UserProfile,
  UserPreferences,
  UserUpdatePayload,
} from './types';

/**
 * User-related API endpoints
 */
export const usersApi = {
  /**
   * Get current user profile
   */
  getCurrentUser: async (): Promise<ApiResponse<UserProfile>> => {
    return httpClient<UserProfile>('/users/aboutme');
  },

  /**
   * Update user information
   */
  updateUser: async (userData: UserUpdatePayload): Promise<ApiResponse<UserProfile>> => {
    return httpClient<UserProfile>('/users/aboutme', {
      method: 'PATCH',
      body: JSON.stringify(userData),
    });
  },

  /**
   * Save user preferences
   */
  saveUserPreferences: async (preferences: UserPreferences): Promise<ApiResponse<UserPreferences>> => {
    return httpClient<UserPreferences>('/users/preferences', {
      method: 'POST',
      body: JSON.stringify(preferences),
    });
  },

  /**
   * Get user preferences
   */
  getUserPreferences: async (): Promise<ApiResponse<UserPreferences>> => {
    return httpClient<UserPreferences>('/users/preferences');
  },

  /**
   * Delete user account (self)
   */
  deleteAccount: async (): Promise<ApiResponse<void>> => {
    return httpClient<void>('/users/aboutme', {
      method: 'DELETE',
    });
  },
};
