/**
 * Error handling utilities
 */

export interface ErrorInfo {
  message: string;
  title: string;
  code?: string | number;
}

/**
 * Extract error information
 */
export const extractErrorInfo = (error: unknown): ErrorInfo => {
  let message = 'An unexpected error occurred';
  let title = 'Operation Failed';
  let code: string | number | undefined;
  
  if (error instanceof Error) {
    message = error.message;
    title = error.name !== 'Error' ? error.name : title;
  } else if (typeof error === 'string') {
    message = error;
  } else if (error && typeof error === 'object') {
    const apiError = error as any;
    message = apiError.message || apiError.detail || apiError.error || message;
    title = apiError.title || apiError.name || title;
    code = apiError.code || apiError.status;
  }
  
  return { message, title, code };
};

/**
 * Check if an API response indicates success
 */
export const isSuccessResponse = (response: any): boolean => {
  return response?.data && (response.status === 200 || response.status === 201);
};

/**
 * Validate required fields
 */
export const validateRequiredFields = (fields: Record<string, any>): string[] => {
  const errors: string[] = [];
  
  Object.entries(fields).forEach(([key, value]) => {
    if (!value || (typeof value === 'string' && !value.trim())) {
      errors.push(`${key} is required`);
    }
  });
  
  return errors;
};
