/**
 * Shared types for signup flow
 */

export interface ExistingOrganization {
  name: string;
}

export interface NewOrganization {
  name: string;
  province: string;
  description: string;
}

export interface UserPreferences {
  selected: string[];
  custom: string;
}

export type OrganizationType = ExistingOrganization | NewOrganization;

/**
 * Signup form data
 */
export interface SignupFormData {
  email: string;
  firstName: string;
  lastName: string;
  password: string;
  organization: OrganizationType;
  preferences?: UserPreferences;
}

/**
 * Signup flow state
 */
export interface SignupState {
  isLoading: boolean;
  currentStep?: 'account' | 'organization' | 'preferences' | 'complete';
  error?: string;
}
