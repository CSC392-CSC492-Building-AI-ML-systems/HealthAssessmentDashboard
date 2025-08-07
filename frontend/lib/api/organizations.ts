import { httpClient } from './core/http-client';
import {
  ApiResponse,
  Organization,
  CreateOrganizationPayload,
  UpdateOrganizationPayload,
} from './types';

/**
 * Organization-related API endpoints
 */
export const organizationsApi = {
  /**
   * Create a new organization
   */
  createOrganization: async (
    orgData: CreateOrganizationPayload
  ): Promise<ApiResponse<Organization>> => {
    return httpClient<Organization>('/organizations/', {
      method: 'POST',
      body: JSON.stringify(orgData),
    });
  },

  /**
   * Get all organizations
   */
  getOrganizations: async (): Promise<ApiResponse<Organization[]>> => {
    return httpClient<Organization[]>('/organizations/');
  },

  /**
   * Get organization by ID
   */
  getOrganizationById: async (id: number): Promise<ApiResponse<Organization>> => {
    return httpClient<Organization>(`/organizations/${id}`);
  },

  /**
   * Get organization by name (for existing org selection)
   */
  getOrganizationByName: async (name: string): Promise<ApiResponse<Organization[]>> => {
    return httpClient<Organization[]>(`/organizations/search?q=${encodeURIComponent(name)}`);
  },

  /**
   * Update organization
   */
  updateOrganization: async (
    id: number,
    data: UpdateOrganizationPayload
  ): Promise<ApiResponse<Organization>> => {
    return httpClient<Organization>(`/organizations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete organization
   */
  deleteOrganization: async (id: number): Promise<ApiResponse<void>> => {
    return httpClient<void>(`/organizations/${id}`, {
      method: 'DELETE',
    });
  },
};
