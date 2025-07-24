/**
 * Shared TypeScript types for API operations

 */

// ============================================================================
// Core API Types
// ============================================================================

/**
 * Standard API response wrapper for all endpoints
 */
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

// ============================================================================
// Authentication & User Types
// ============================================================================

/**
 * User login credentials
 */
export interface UserCredentials {
  email: string;
  password: string;
}

/**
 * User signup payload
 */
export interface SignupPayload {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  organization_id?: number | null;
}

/**
 * Authentication response containing tokens and user info
 */
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

/**
 * Complete user profile information
 */
export interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  organization_id?: number;
  created_at: string;
  updated_at: string;
}

/**
 * User preferences for therapeutic areas and custom settings
 */
export interface UserPreferences {
  selected_therapeutic_areas: string[];
  custom_preferences: string;
}

/**
 * Payload for updating user information
 */
export interface UserUpdatePayload {
  organization_id?: number;
  first_name?: string;
  last_name?: string;
}

// ============================================================================
// Organization Types
// ============================================================================

/**
 * Complete organization information
 */
export interface Organization {
  id: number;
  name: string;
  province: string;
  description: string;
  created_at: string;
  updated_at: string;
}

/**
 * Payload for creating a new organization
 */
export interface CreateOrganizationPayload {
  name: string;
  province: string;
  description: string;
}

/**
 * Payload for updating organization information
 */
export interface UpdateOrganizationPayload {
  name?: string;
  province?: string;
  description?: string;
}

// ============================================================================
// Chatbot Types
// ============================================================================

/**
 * Individual chat message
 */
export interface ChatMessage {
  id?: number;
  content: string;
  role: 'user' | 'assistant';
  timestamp?: string;
}

/**
 * Complete chat conversation history
 */
export interface ChatHistory {
  messages: ChatMessage[];
  conversation_id: string;
}
