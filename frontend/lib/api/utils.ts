/**
 * API utility helpers and configuration
 */

export { clearApiCache, ApiError, NetworkError } from './core/http-client';

export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL,
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production',
};
