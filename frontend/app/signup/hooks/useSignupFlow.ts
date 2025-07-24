import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/general/ToastProvider';
import { authApi, organizationsApi, usersApi } from '@/lib/api';
import { extractErrorInfo, isSuccessResponse } from '../utils/errorHandling';
import type { ExistingOrganization, NewOrganization, UserPreferences } from '../types';


type OrganizationType = ExistingOrganization | NewOrganization;

/**
 * Custom hook for handling signup flow
 */
export const useSignupFlow = () => {
  const router = useRouter();
  const { showError: showToastError, showInfo, showWarning } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const isNewOrganization = (org: OrganizationType): org is NewOrganization => {
    return 'province' in org && 'description' in org;
  };

  // Use account creation
  const createUserAccount = async (
    email: string,
    firstName: string,
    lastName: string,
    password: string
  ) => {
    const userPayload = {
      email: email.trim(),
      first_name: firstName.trim(),
      last_name: lastName.trim(),
      password: password,
      organization_id: null,
    };
    
    const signupResponse = await authApi.signup(userPayload);

    if (!isSuccessResponse(signupResponse)) {
      const errorMessage = signupResponse.error || `Signup failed with status ${signupResponse.status}`;
      throw new Error(errorMessage);
    }

    if (signupResponse.data?.access_token) {
      localStorage.setItem('access_token', signupResponse.data.access_token);
      return signupResponse.data;
    } else {
      throw new Error('Invalid response: missing access token');
    }
  };

  // Organization creation/selection
  const handleOrganization = async (organization: OrganizationType): Promise<number | null> => {
    try {
      if (isNewOrganization(organization)) {
        const orgResult = await organizationsApi.createOrganization({
          name: organization.name,
          province: organization.province,
          description: organization.description,
        });

        if (orgResult.data) {
          return orgResult.data.id;
        }
        
        if (orgResult.status === 400) {
          showWarning(
            `Organization "${organization.name}" already exists in ${organization.province}`, 
            'Organization Warning'
          );
        } else {
          showWarning(
            `Failed to create organization: ${orgResult.error || 'Unknown error'}`, 
            'Organization Warning'
          );
        }
        return null;
      }

      const orgResult = await organizationsApi.getOrganizationByName(organization.name);
      if (orgResult.data && Array.isArray(orgResult.data) && orgResult.data.length > 0) {
        const match = orgResult.data.find((org: any) => org.name === organization.name);
        if (match) {
          return match.id;
        }
      }
      showWarning(`Could not find organization "${organization.name}"`, 'Organization Warning');
      return null;
    } catch (error) {
      const { message } = extractErrorInfo(error);
      showWarning(`Organization processing failed: ${message}`, 'Organization Warning');
      return null;
    }
  };

  // Save user preferences
  const saveUserPreferences = async (preferences: UserPreferences): Promise<boolean> => {
    if (!preferences?.selected?.length && !preferences?.custom?.trim()) {
      return true;
    }

    try {
      const prefsResult = await usersApi.saveUserPreferences({
        selected_therapeutic_areas: preferences.selected || [],
        custom_preferences: preferences.custom?.trim() || '',
      });

      if (!prefsResult.data) {
        showWarning('Failed to save preferences', 'Preferences Warning');
        return false;
      }
      return true;
    } catch (error) {
      const { message } = extractErrorInfo(error);
      showWarning(`Failed to save preferences: ${message}`, 'Preferences Warning');
      return false;
    }
  };

  // Link user-organization
  const linkUserToOrganization = async (organizationId: number): Promise<boolean> => {
    try {
      const updateResult = await usersApi.updateUser({ organization_id: organizationId });

      if (!updateResult.data) {
        showWarning('Failed to link to organization', 'Linking Warning');
        return false;
      }
      return true;
    } catch (error) {
      const { message } = extractErrorInfo(error);
      showWarning(`Failed to link user to organization: ${message}`, 'Update Warning');
      return false;
    }
  };

  const handleSignup = async (
    email: string,
    firstName: string,
    lastName: string,
    password: string,
    organization: OrganizationType,
    preferences?: UserPreferences
  ) => {
    setIsLoading(true);

    try {
      await createUserAccount(email, firstName, lastName, password);
      const organizationId = await handleOrganization(organization);

      if (preferences) {
        await saveUserPreferences(preferences);
      }

      if (organizationId) {
        await linkUserToOrganization(organizationId);
      }
      
      showInfo('Signup successful! Redirecting...', 'Welcome!');
      setTimeout(() => {
        router.push('/dashboard');
      }, 1500);

    } catch (error) {
      const { message, title } = extractErrorInfo(error);
      showToastError(message, title);
      localStorage.removeItem('access_token');
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    handleSignup,
  };
};
