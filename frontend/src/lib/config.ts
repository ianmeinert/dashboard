/**
 * Application Configuration
 * 
 * Centralized configuration management for the dashboard application.
 * Uses SvelteKit's environment variable system for secure configuration.
 */

import { env } from '$env/dynamic/public';

// Environment detection
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;

// API Configuration
export const API_CONFIG = {
  // Base URL - defaults to relative path for proxy, can be overridden with env var
  baseUrl: env.PUBLIC_API_BASE_URL || '',
  
  // API endpoints
  endpoints: {
    grocery: '/api/grocery',
    calendar: '/api/calendar',
    weather: '/api/weather',
    monitoring: '/api/monitoring',
  },
  
  // Timeouts
  timeout: 30000, // 30 seconds
  
  // Retry configuration
  retry: {
    attempts: 3,
    delay: 1000, // 1 second
  }
} as const;

// Feature flags
export const FEATURES = {
  enableCaching: true,
  enableOfflineMode: false,
  enableDebugLogging: isDevelopment,
  enableMetrics: true,
} as const;

// Cache configuration
export const CACHE_CONFIG = {
  defaultTtl: 30 * 60 * 1000, // 30 minutes
  maxSize: 100, // Maximum number of cached items
} as const;

// UI Configuration
export const UI_CONFIG = {
  refreshIntervals: {
    monitoring: 30000, // 30 seconds
    weather: 300000, // 5 minutes
    calendar: 600000, // 10 minutes
  },
  pagination: {
    defaultPageSize: 20,
    maxPageSize: 100,
  },
} as const;

/**
 * Get full API URL for a given endpoint
 */
export function getApiUrl(endpoint: string): string {
  const baseUrl = API_CONFIG.baseUrl;
  const fullEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  // If baseUrl is empty, use relative path (works with Vite proxy)
  if (!baseUrl) {
    return fullEndpoint;
  }
  
  // Ensure baseUrl doesn't end with slash
  const cleanBaseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  return `${cleanBaseUrl}${fullEndpoint}`;
}

/**
 * Get API URL for a specific service
 */
export function getServiceUrl(service: keyof typeof API_CONFIG.endpoints): string {
  return getApiUrl(API_CONFIG.endpoints[service]);
}

/**
 * Get configuration for a specific environment
 */
export function getEnvironmentConfig() {
  return {
    isDevelopment,
    isProduction,
    apiBaseUrl: API_CONFIG.baseUrl || env.PUBLIC_API_FALLBACK_URL || 'http://localhost:8000',
    features: FEATURES,
  };
}

// Type exports for better TypeScript support
export type ApiEndpoint = keyof typeof API_CONFIG.endpoints;
export type FeatureFlag = keyof typeof FEATURES; 