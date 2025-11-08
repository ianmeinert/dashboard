/**
 * API Utilities
 * 
 * Centralized HTTP client utilities with consistent error handling,
 * retry logic, and configuration management.
 */

import { API_CONFIG, FEATURES, getApiUrl } from '../config.js';

// Types
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  headers: Headers;
}

export interface ApiError {
  message: string;
  status?: number;
  details?: any;
  errorCode?: string;
}

export interface RequestOptions extends RequestInit {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
}

// Default request options
const defaultOptions: RequestOptions = {
  timeout: API_CONFIG.timeout,
  retries: API_CONFIG.retry.attempts,
  retryDelay: API_CONFIG.retry.delay,
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Sleep utility for retry delays
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Create an AbortController with timeout
 */
function createTimeoutController(timeout: number): AbortController {
  const controller = new AbortController();
  setTimeout(() => controller.abort(), timeout);
  return controller;
}

/**
 * Handle API errors consistently
 */
function handleApiError(error: any, url: string): ApiError {
  if (error.name === 'AbortError') {
    return {
      message: 'Request timeout',
      status: 408,
    };
  }

  if (error instanceof Response) {
    return {
      message: `HTTP ${error.status}: ${error.statusText}`,
      status: error.status,
    };
  }

  if (error instanceof TypeError && error.message.includes('fetch')) {
    return {
      message: 'Network error - unable to connect to server',
      status: 0,
    };
  }

  // If the error already has a status (like from our API error handling), preserve it
  if (error && typeof error === 'object' && typeof error.status === 'number') {
    return {
      message: error.message || 'API error occurred',
      status: error.status,
      details: error.details,
      errorCode: error.errorCode
    };
  }

  return {
    message: error.message || 'Unknown error occurred',
    status: 500,
  };
}

/**
 * Parse JSON response with error handling
 */
async function parseJsonResponse(response: Response): Promise<any> {
  try {
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    return await response.text();
  } catch (error) {
    throw new Error('Failed to parse response');
  }
}

/**
 * Retry logic for failed requests
 */
async function retryRequest<T>(
  requestFn: () => Promise<T>,
  retries: number,
  delay: number
): Promise<T> {
  let lastError: any;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;
      
      // Don't retry on client errors (4xx) - these are permanent failures
      if (error && typeof error === 'object' && error.status >= 400 && error.status < 500) {
        throw error;
      }
      
      if (attempt === retries) {
        break;
      }

      if (FEATURES.enableDebugLogging) {
        console.warn(`API request failed (attempt ${attempt + 1}/${retries + 1}):`, error);
      }

      await sleep(delay * Math.pow(2, attempt)); // Exponential backoff
    }
  }

  throw lastError;
}

/**
 * Core API request function
 */
export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  const url = getApiUrl(endpoint);
  const requestOptions = { ...defaultOptions, ...options };
  const { timeout, retries, retryDelay, ...fetchOptions } = requestOptions;

  const requestFn = async (): Promise<ApiResponse<T>> => {
    const controller = createTimeoutController(timeout!);
    
    try {
      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await parseJsonResponse(response);
        } catch {
          errorData = {};
        }

        // Handle structured error responses
        if (errorData.error && errorData.message) {
          // Structured error response from our custom error handling
          const error = new Error(errorData.message);
          (error as any).errorCode = errorData.error;
          (error as any).details = errorData.details;
          (error as any).detail = errorData.message; // Also set detail for consistency
          (error as any).status = response.status;
          throw error;
        }

        // Handle FastAPI validation errors
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            const errorMessage = errorData.detail.map((d: any) => d.msg).join('; ');
            const error = new Error(errorMessage);
            (error as any).detail = errorMessage; // Preserve detail field
            (error as any).status = response.status;
            throw error;
          }
          const error = new Error(errorData.detail);
          (error as any).detail = errorData.detail; // Preserve detail field
          (error as any).status = response.status;
          throw error;
        }

        // Fallback for unknown error formats
        const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
        (error as any).status = response.status;
        throw error;
      }

      const data = await parseJsonResponse(response);

      return {
        data,
        status: response.status,
        headers: response.headers,
      };
    } catch (error) {
      throw handleApiError(error, url);
    }
  };

  return retryRequest(requestFn, retries!, retryDelay!);
}

/**
 * Convenience methods for common HTTP methods
 */
export const api = {
  get: <T = any>(endpoint: string, options?: RequestOptions) =>
    apiRequest<T>(endpoint, { ...options, method: 'GET' }),

  post: <T = any>(endpoint: string, data?: any, options?: RequestOptions) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T = any>(endpoint: string, data?: any, options?: RequestOptions) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),

  patch: <T = any>(endpoint: string, data?: any, options?: RequestOptions) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T = any>(endpoint: string, options?: RequestOptions) =>
    apiRequest<T>(endpoint, { ...options, method: 'DELETE' }),
};

/**
 * Service-specific API helpers
 */
export const serviceApi = {
  grocery: {
    get: (endpoint: string = '') => api.get(`/api/grocery${endpoint}`),
    post: (data: any, endpoint: string = '') => api.post(`/api/grocery${endpoint}`, data),
    put: (id: number, data: any) => api.put(`/api/grocery/${id}`, data),
    patch: (id: number, data: any) => api.patch(`/api/grocery/${id}`, data),
    delete: (idOrEndpoint: number | string) => {
      if (typeof idOrEndpoint === 'number') {
        return api.delete(`/api/grocery/${idOrEndpoint}`);
      }
      return api.delete(`/api/grocery${idOrEndpoint}`);
    },
  },

  calendar: {
    get: (endpoint: string = '') => api.get(`/api/calendar${endpoint}`),
    post: (data: any, endpoint: string = '') => api.post(`/api/calendar${endpoint}`, data),
  },

  weather: {
    get: (endpoint: string = '') => api.get(`/api/weather${endpoint}`),
    post: (data: any, endpoint: string = '') => api.post(`/api/weather${endpoint}`, data),
  },

  monitoring: {
    get: (endpoint: string = '') => api.get(`/api/monitoring${endpoint}`),
  },

  chores: {
    get: (endpoint: string = '') => api.get(`/api/chores${endpoint}`),
    post: (data: any, endpoint: string = '') => api.post(`/api/chores${endpoint}`, data),
    put: (id: number, data: any) => api.put(`/api/chores/${id}`, data),
    patch: (id: number, data: any) => api.patch(`/api/chores/${id}`, data),
    delete: (endpoint: string) => api.delete(`/api/chores${endpoint}`),
  },

}; 