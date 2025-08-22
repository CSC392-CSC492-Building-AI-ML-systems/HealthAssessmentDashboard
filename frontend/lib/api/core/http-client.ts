/**
 * Core HTTP client with interceptors and advanced features
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000'

// Error types for better error handling
export class ApiError extends Error {
  status: number;
  data?: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}

// Response type for all API calls
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

// Options for configuring requests
export interface RequestOptions extends RequestInit {
  skipAuth?: boolean;
  skipRefresh?: boolean;
  cache?: RequestCache;
  retries?: number;
}

// In-memory cache for GET requests
const apiCache = new Map<string, {data: any, timestamp: number}>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

/**
 * Core fetch wrapper with authentication, caching, and error handling
 */
export async function httpClient<T = any>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  try {
    const {
      skipAuth = false,
      skipRefresh = false,
      retries = 1,
      ...fetchOptions
    } = options;

    // Handle GET request caching
    const cacheKey = `${endpoint}:${JSON.stringify(fetchOptions)}`;
    if (fetchOptions.method === undefined || fetchOptions.method === 'GET') {
      const cached = apiCache.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
        return { data: cached.data as T, status: 200 };
      }
    }

    // Prepare headers
    const token = localStorage.getItem('access_token');
    const config: RequestInit = {
      ...fetchOptions,
      headers: {
        'Content-Type': 'application/json',
        ...(token && !skipAuth && { Authorization: `Bearer ${token}` }),
        ...fetchOptions.headers,
      },
      credentials: 'include',
    };

    // Make the request
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    // Handle authentication issues
    if (response.status === 401 && !skipRefresh && token) {
      const refreshed = await refreshToken();
      if (refreshed) {
        // Retry with new token
        return httpClient<T>(endpoint, {
          ...options,
          skipRefresh: true, // Prevent infinite refresh loops
        });
      } else {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        // Only redirect if not on public pages
        const publicPages = ['/signup', '/login'];
        if (!publicPages.includes(window.location.pathname)) {
          window.location.href = '/login';
        }
        return { error: 'Authentication failed', status: 401 };
      }
    }

    // Parse response
    let data = null;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    }

    // Cache successful GET responses
    if (
      (fetchOptions.method === undefined || fetchOptions.method === 'GET') &&
      response.ok &&
      data
    ) {
      apiCache.set(cacheKey, { data, timestamp: Date.now() });
    }

    return {
      data: response.ok ? data : undefined,
      error: response.ok ? undefined : data?.detail || 'Request failed',
      status: response.status,
    };
  } catch (error) {
    console.error('API request error:', error);
    
    // Retry logic for network errors
    if (options.retries && options.retries > 0) {
      console.log(`Retrying request, ${options.retries} attempts left`);
      return httpClient<T>(endpoint, {
        ...options,
        retries: options.retries - 1,
      });
    }
    
    return {
      error: error instanceof Error ? error.message : 'Network error',
      status: 0,
    };
  }
}

/**
 * Refresh the access token using the refresh token cookie
 */
export async function refreshToken(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      return true;
    }

    return false;
  } catch (error) {
    console.error('Token refresh error:', error);
    return false;
  }
}

/**
 * Clear the API cache
 */
export function clearApiCache(endpoint?: string): void {
  if (endpoint) {
    // Clear specific endpoint cache
    apiCache.forEach((_, key) => {
      if (key.startsWith(`${endpoint}:`)) {
        apiCache.delete(key);
      }
    });
  } else {
    // Clear all cache
    apiCache.clear();
  }
}
