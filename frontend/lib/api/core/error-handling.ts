/**
 * API error handling utilities
 */
import { ApiResponse } from '../types';

/**
 * Default error message to display when an API call fails
 */
export const DEFAULT_ERROR_MESSAGE = 'An unexpected error occurred. Please try again.';

/**
 * Extract a error message from an API response
 */
export function getErrorMessage(response: ApiResponse | undefined): string {
  if (!response) {
    return DEFAULT_ERROR_MESSAGE;
  }

  if (response.error) {
    return response.error;
  }

  if (response.status === 401) {
    return 'Authentication failed. Please login again.';
  }

  if (response.status === 403) {
    return 'You do not have permission to perform this action.';
  }

  if (response.status === 404) {
    return 'The requested resource was not found.';
  }

  if (response.status === 500) {
    return 'Server error. Please try again later.';
  }

  return DEFAULT_ERROR_MESSAGE;
}

/**
 * Check if an API response is successful
 */
export function isSuccessResponse<T>(response: ApiResponse<T>): response is ApiResponse<T> & { data: T } {
  return response.status >= 200 && response.status < 300 && response.data !== undefined;
}

/**
 * Helper to handle API errors in async functions
 */
export async function withErrorHandling<T>(
  apiCall: () => Promise<ApiResponse<T>>,
  options: {
    onSuccess?: (data: T) => void;
    onError?: (error: string) => void;
    fallbackValue?: T;
  } = {}
): Promise<T | undefined> {
  try {
    const response = await apiCall();
    
    if (isSuccessResponse(response)) {
      options.onSuccess?.(response.data);
      return response.data;
    } else {
      const errorMessage = getErrorMessage(response);
      options.onError?.(errorMessage);
      return options.fallbackValue;
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : DEFAULT_ERROR_MESSAGE;
    options.onError?.(errorMessage);
    return options.fallbackValue;
  }
}
