/**
 * API module exports - Internal use only
 */

// Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export {
  httpClient,
  refreshToken,
  clearApiCache,
  type ApiResponse,
  type RequestOptions,
  ApiError,
  NetworkError,
} from './core/http-client';

export * from './types';
