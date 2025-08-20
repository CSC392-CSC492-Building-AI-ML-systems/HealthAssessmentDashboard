/**
 * Validation utilities for signup flow
 */

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

/**
 * Validate email format
 */
export const validateEmail = (email: string): ValidationResult => {
  const errors: string[] = [];
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!email) {
    errors.push('Email is required');
  } else if (!emailRegex.test(email)) {
    errors.push('Please enter a valid email address');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Validate password strength
 */
export const validatePassword = (password: string): ValidationResult => {
  const errors: string[] = [];
  
  if (!password) {
    errors.push('Password is required');
  } else {
    if (password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }
    if (!/(?=.*[a-z])/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }
    if (!/(?=.*[A-Z])/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }
    if (!/(?=.*\d)/.test(password)) {
      errors.push('Password must contain at least one number');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Validate name fields
 */
export const validateName = (name: string, fieldName: string): ValidationResult => {
  const errors: string[] = [];
  
  if (!name || !name.trim()) {
    errors.push(`${fieldName} is required`);
  } else if (name.trim().length < 2) {
    errors.push(`${fieldName} must be at least 2 characters long`);
  } else if (!/^[a-zA-Z\s'-]+$/.test(name.trim())) {
    errors.push(`${fieldName} can only contain letters, spaces, hyphens, and apostrophes`);
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Validate organization data
 */
export const validateOrganization = (organization: any): ValidationResult => {
  const errors: string[] = [];
  
  if (!organization) {
    errors.push('Organization information is required');
    return { isValid: false, errors };
  }
  
  if (!organization.name || !organization.name.trim()) {
    errors.push('Organization name is required');
  }
  
  // If it's a new organization (has province/description), validate those fields
  if ('province' in organization || 'description' in organization) {
    if (!organization.province || !organization.province.trim()) {
      errors.push('Province is required for new organizations');
    }
    if (!organization.description || !organization.description.trim()) {
      errors.push('Description is required for new organizations');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Validate complete signup form
 */
export const validateSignupForm = (formData: {
  email: string;
  firstName: string;
  lastName: string;
  password: string;
  organization: any;
}): ValidationResult => {
  const allErrors: string[] = [];
  
  const emailValidation = validateEmail(formData.email);
  const firstNameValidation = validateName(formData.firstName, 'First name');
  const lastNameValidation = validateName(formData.lastName, 'Last name');
  const passwordValidation = validatePassword(formData.password);
  const organizationValidation = validateOrganization(formData.organization);
  
  allErrors.push(
    ...emailValidation.errors,
    ...firstNameValidation.errors,
    ...lastNameValidation.errors,
    ...passwordValidation.errors,
    ...organizationValidation.errors
  );
  
  return {
    isValid: allErrors.length === 0,
    errors: allErrors,
  };
};
