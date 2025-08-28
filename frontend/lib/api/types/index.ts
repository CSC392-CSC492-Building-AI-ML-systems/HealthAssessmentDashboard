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
  therapeutic_areas: string[];
  news_preferences: string;
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


// ============================================================================
// Drug Types
// ============================================================================

/**
 * Complete chat conversation history
 */
export type NewDrugPayload = {
  title: string;
  genericName: string;
  therapeuticArea: string;
  din: string;
  organization: string;
  costEffectiveness: number;
  submissionPathway: string;
  therapeuticValue: string;
  manufacturerPrice: number;
  reimbursementRestrictions: string;
  drugType: string;
  dosageForm: string;
  submissionDate?: string;
  projectNumber?: string;
  description?: string;
  documents?: File[];
};

export interface DrugFileInfo {
  id: number;
  filename: string;
  original_filename: string;
  file_size?: number;
  content_type?: string;
  blob_url?: string;
  file_type?: string;
  created_at: string;
}

export interface DrugResponse {
  id: number;
  user_id: number;
  created_at: string;
  updated_at?: string;
  files: DrugFileInfo[];

  title: string;
  genericName: string;
  therapeuticArea: string;
  din: string;
  organization: string;
  submissionDate?: string;
  projectNumber?: string;
  description?: string;
}