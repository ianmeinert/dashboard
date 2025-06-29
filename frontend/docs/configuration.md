# Frontend Configuration Management

This document describes the centralized configuration management system for the dashboard frontend.

## Overview

The frontend now uses a centralized configuration system that:

- Manages API URLs and endpoints consistently
- Supports environment-specific configuration
- Provides type-safe configuration access
- Includes centralized error handling and retry logic

## Configuration Files

### Core Configuration (`src/lib/config.ts`)

The main configuration module that defines:

- API endpoints and base URLs
- Feature flags
- Cache settings
- UI configuration (refresh intervals, pagination, etc.)

### API Utilities (`src/lib/utils/api.ts`)

Centralized HTTP client with:

- Consistent error handling
- Automatic retry logic
- Request/response interceptors
- Service-specific API helpers

## Environment Variables

### Development Setup

1. Copy the template file:

   ```bash
   cp templates/env_template.txt .env.local
   ```

2. Configure your environment variables:

   ```bash
   # For development (uses Vite proxy)
   PUBLIC_API_BASE_URL=
   
   # For production
   PUBLIC_API_BASE_URL=https://api.yourdomain.com
   ```

### Available Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PUBLIC_API_BASE_URL` | API base URL (empty = use proxy) | `''` |
| `PUBLIC_ENABLE_DEBUG_LOGGING` | Enable debug logging | `true` (dev) |
| `PUBLIC_ENABLE_METRICS` | Enable metrics collection | `true` |
| `PUBLIC_ENABLE_CACHING` | Enable client-side caching | `true` |

## Usage Examples

### Using Service APIs

```typescript
import { serviceApi } from '$lib/utils/api.js';

// Grocery API
const items = await serviceApi.grocery.get();
await serviceApi.grocery.post(newItem);
await serviceApi.grocery.put(itemId, updates);
await serviceApi.grocery.delete(itemId);

// Calendar API
const events = await serviceApi.calendar.get('/events?start=...&end=...');
const colors = await serviceApi.calendar.get('/colors');

// Weather API
const current = await serviceApi.weather.get('/current?city=...');
const forecast = await serviceApi.weather.get('/forecast?city=...');

// Monitoring API
const status = await serviceApi.monitoring.get('/status');
const metrics = await serviceApi.monitoring.get('/metrics?hours=1');
```

### Using Configuration

```typescript
import { API_CONFIG, FEATURES, UI_CONFIG } from '$lib/config.js';

// Check environment
if (isDevelopment) {
  console.log('Running in development mode');
}

// Get API URL
const groceryUrl = getServiceUrl('grocery');

// Check feature flags
if (FEATURES.enableCaching) {
  // Enable caching logic
}

// Use UI configuration
const refreshInterval = UI_CONFIG.refreshIntervals.monitoring;
```

### Direct API Calls

```typescript
import { api } from '$lib/utils/api.js';

// GET request
const response = await api.get('/api/custom/endpoint');

// POST request with data
const result = await api.post('/api/custom/endpoint', { data: 'value' });

// Custom options
const response = await api.get('/api/custom/endpoint', {
  timeout: 5000,
  retries: 2,
  headers: { 'Custom-Header': 'value' }
});
```

## Migration Guide

### Before (Old Way)

```typescript
// Hardcoded URLs
const response = await fetch('http://localhost:8000/api/grocery');
const data = await response.json();

// Manual error handling
if (!response.ok) {
  throw new Error(`HTTP error! status: ${response.status}`);
}
```

### After (New Way)

```typescript
// Centralized API calls
const response = await serviceApi.grocery.get();
const data = response.data;

// Automatic error handling and retries
// Errors are automatically handled and retried
```

## Benefits

1. **Environment Flexibility**: Easy switching between development, staging, and production
2. **Type Safety**: Full TypeScript support for all configuration options
3. **Consistent Error Handling**: Centralized error handling and retry logic
4. **Maintainability**: Single source of truth for API configuration
5. **Security**: Environment variables for sensitive configuration
6. **Performance**: Built-in caching and optimization features

## Best Practices

1. **Always use service APIs**: Use `serviceApi.*` methods instead of direct fetch calls
2. **Environment variables**: Use environment variables for environment-specific settings
3. **Type safety**: Leverage TypeScript types for configuration access
4. **Error handling**: Let the centralized error handling manage API errors
5. **Caching**: Use the built-in caching features when appropriate

## Troubleshooting

### Common Issues

1. **API calls failing**: Check that `PUBLIC_API_BASE_URL` is set correctly
2. **Proxy not working**: Ensure Vite dev server is running and proxy is configured
3. **Environment variables not loading**: Make sure `.env.local` file exists and is in the correct location

### Debug Mode

Enable debug logging by setting `PUBLIC_ENABLE_DEBUG_LOGGING=true` in your environment file. This will show:

- API request/response details
- Retry attempts
- Configuration values
- Error details
