/**
 * Main API entry point
 */

export {
  httpClient as apiRequest,
  refreshToken,
  clearApiCache,
  type ApiResponse,
  type RequestOptions,
  ApiError,
  NetworkError,
} from './api/core/http-client';

export { authApi } from './api/auth';
// export { organizationsApi } from './api/organizations';
export { usersApi } from './api/users';
export { chatbotApi } from './api/chatbot';

export * from './api/types';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
