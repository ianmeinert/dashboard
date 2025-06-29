# Kiosk Dashboard Frontend

A modern, responsive SvelteKit application for displaying kiosk dashboard information with real-time calendar integration and weather/forecast support.

## Features

- **Real-time Calendar Display**: Show upcoming events from Google Calendar
- **Weather Widget**: Current weather and 5-day forecast by geolocation, city/state, or zip code, with robust fallback logic and instant dashboard updates
- **Responsive Design**: Optimized for kiosk displays and various screen sizes
- **Modern UI**: Clean, accessible interface with Tailwind CSS
- **Card-Style Widgets**: Visually distinct dashboard quadrants with card boundaries
- **TypeScript Support**: Full type safety and IntelliSense
- **Performance Optimized**: Fast loading and smooth interactions
- **Centralized Configuration**: Environment-based configuration management with type safety

## Weather Widget Usage

- On load, attempts to use browser geolocation for weather.
- If geolocation is denied/unavailable, falls back to Austin, TX (not shown in input fields).
- Users can search by city/state or zip code; input fields remain empty unless user enters a value.
- Robust error handling and user-friendly messages for API/network issues.
- **Instant dashboard updates:** When a user sets a new default location, the widget emits a `locationSet` event with the canonical location, and the parent updates the prop. The widget always shows the latest location, even after closing and reopening, without a full page reload.
- **Error handling:** 422 errors are avoided by sending only the expected fields to the backend.

## Svelte Event/Prop Pattern

- The dashboard uses Svelte events and props for real-time parent-child state sync (e.g., weather location updates).
- When a child widget updates a value (like the weather location), it emits an event with the new data, and the parent updates its state and passes it back down as a prop.

## Tech Stack

- **Framework**: [SvelteKit](https://kit.svelte.dev/) - Full-stack web framework
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- **Language**: [TypeScript](https://www.typescriptlang.org/) - Type-safe JavaScript
- **Build Tool**: [Vite](https://vitejs.dev/) - Fast build tool and dev server
- **Package Manager**: npm/yarn/pnpm

## Quick Start

### Prerequisites

- Node.js 18+
- npm, yarn, or pnpm
- Backend API running (see [backend README](../backend/README.md))

### Installation

1. **Navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   # Using npm
   npm install
   ```

3. **Set up environment variables:**
   Copy the template and configure your environment:

   ```bash
   cp templates/env_template.txt .env.local
   ```

   For development (recommended):

   ```env
   # Leave empty to use Vite proxy
   PUBLIC_API_BASE_URL=
   ```

   For production:

   ```env
   PUBLIC_API_BASE_URL=https://api.yourdomain.com
   ```

4. **Start the development server:**

   ```bash
   npm run dev
   # Or with auto-open
   npm run dev -- --open
   ```

5. **Open your browser:**
   Navigate to `http://localhost:5173` (or the URL shown in terminal)

## Project Structure

```
frontend/
├── src/
│   ├── app.html              # HTML template
│   ├── app.css               # Global styles
│   ├── app.d.ts              # TypeScript declarations
│   ├── lib/                  # Shared utilities and components
│   │   ├── components/       # Reusable Svelte components
│   │   ├── stores/           # Svelte stores for state management
│   │   ├── utils/            # Utility functions
│   │   │   └── api.ts        # Centralized API utilities
│   │   ├── config.ts         # Configuration management
│   │   └── types/            # TypeScript type definitions
│   ├── routes/               # SvelteKit routes
│   │   ├── +layout.svelte    # Root layout
│   │   ├── +page.svelte      # Home page (dashboard)
│   │   └── monitoring/       # Monitoring pages
│   └── styles/               # Additional stylesheets
├── static/                   # Static assets
│   ├── favicon.png
│   └── images/
├── templates/                # Template files
│   └── env_template.txt      # Environment configuration template
├── docs/                     # Documentation
│   └── configuration.md      # Configuration management guide
├── package.json              # Dependencies and scripts
├── svelte.config.js          # SvelteKit configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
├── vite.config.ts            # Vite configuration
└── README.md                 # This file
```

## Configuration Management

The frontend uses a centralized configuration system for better maintainability and environment flexibility. See [Configuration Guide](docs/configuration.md) for detailed information.

### Key Benefits

- **Environment Flexibility**: Easy switching between development, staging, and production
- **Type Safety**: Full TypeScript support for all configuration options
- **Consistent Error Handling**: Centralized error handling and retry logic
- **Service APIs**: Type-safe, service-specific API helpers

### Quick Configuration Examples

```typescript
// Using service APIs
import { serviceApi } from '$lib/utils/api.js';

const items = await serviceApi.grocery.get();
const events = await serviceApi.calendar.get('/events?start=...&end=...');

// Using configuration
import { UI_CONFIG, FEATURES } from '$lib/config.js';

const refreshInterval = UI_CONFIG.refreshIntervals.monitoring;
if (FEATURES.enableCaching) {
  // Enable caching logic
}
```

## Dashboard Layout

- Quadrants: Family Calendar, Weather/Forecast, Grocery List (placeholder), Family Chores (placeholder)
- Card-style boundaries for each widget/quadrant
- Responsive grid adapts to screen size
- Expand/focus any quadrant for detailed view

## Weather Widget Details

- **Geolocation**: Uses browser geolocation if available; otherwise, falls back to Austin, TX (not shown in input fields)
- **Manual Search**: User can enter city/state or zip code; input fields remain empty unless user enters a value
- **Error Handling**: Displays user-friendly error messages for API/network issues
- **Location Display**: Shows resolved location below the search bar

## Development

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run dev -- --open # Start dev server and open browser

# Building
npm run build        # Build for production
npm run preview      # Preview production build

# Code Quality
npm run check        # Type check and lint
npm run lint         # Run ESLint
npm run format       # Format code with Prettier

# Testing
npm run test         # Run unit tests
npm run test:watch   # Run tests in watch mode
npm run test:coverage # Run tests with coverage
```

### Development Workflow

1. **Start the backend API** (see backend README)
2. **Start the frontend dev server:**

   ```bash
   npm run dev
   ```

3. **Make changes** - files will auto-reload
4. **Check code quality:**

   ```bash
   npm run check
   npm run lint
   npm run format
   ```

### Code Quality Tools

- **ESLint**: Code linting and style enforcement
- **Prettier**: Code formatting
- **TypeScript**: Type checking
- **Svelte Check**: Svelte-specific type checking

## API Integration

### Backend Communication

The frontend communicates with the FastAPI backend for:

- Calendar events data
- Weather and forecast data (with geolocation/city/zip fallback)
- System health monitoring
- Real-time updates

### Environment Configuration

The application uses SvelteKit's environment variable system. Configure API endpoints in your `.env.local` file:

```env
# Development (uses Vite proxy)
PUBLIC_API_BASE_URL=

# Production
PUBLIC_API_BASE_URL=https://your-api-domain.com
```

### Error Handling

The centralized API utilities provide consistent error handling:

- Automatic retry logic with exponential backoff
- FastAPI validation error parsing
- Network error detection
- Timeout handling
- User-friendly error messages

## Styling

### Tailwind CSS

This project uses Tailwind CSS for styling:

```bash
# Customize Tailwind configuration
npx tailwindcss init
```

### Custom Styles

- Global styles in `src/app.css`
- Component-specific styles in `.svelte` files
- Utility classes for common patterns

## Testing

### Unit Testing

```bash
# Run tests
npm run test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

### Testing Strategy

- Component testing with `@testing-library/svelte`
- Unit tests for utilities and stores
- Integration tests for API communication
- E2E tests for critical user flows

## Building for Production

### Build Process

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

### Optimization

- Code splitting for better performance
- Asset optimization and compression
- Tree shaking to reduce bundle size
- Service worker for caching (if configured)

### Deployment

1. **Build the application:**

   ```bash
   npm run build
   ```

2. **Deploy the `build/` directory** to your hosting provider

3. **Configure environment variables** for production

4. **Set up proper CORS** on your backend API

## Security Considerations

### Frontend Security

- **Input Validation**: All user inputs are validated
- **XSS Prevention**: Svelte's built-in XSS protection
- **CSRF Protection**: Implemented for state-changing requests
- **Content Security Policy**: Configured for additional security

### API Security

- **HTTPS Only**: All API requests use HTTPS in production
- **Authentication**: Proper token management
- **Rate Limiting**: Handle rate limit responses gracefully
- **Error Handling**: Never expose sensitive error details

### Environment Variables

- **Never commit secrets** to version control
- **Use VITE_ prefix** for client-side variables
- **Validate environment** on startup
- **Provide fallbacks** for missing variables

## Performance Optimization

### Loading Performance

- **Code Splitting**: Automatic route-based splitting
- **Lazy Loading**: Components loaded on demand
- **Asset Optimization**: Images and fonts optimized
- **Caching**: Browser and service worker caching

### Runtime Performance

- **Svelte Reactivity**: Efficient reactive updates
- **Store Optimization**: Minimal store subscriptions
- **Memory Management**: Proper cleanup in components
- **Debouncing**: API calls debounced to prevent spam

## Accessibility (a11y)

### Standards Compliance

- **WCAG 2.1 AA**: Accessibility standards compliance
- **Semantic HTML**: Proper HTML structure
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: ARIA labels and descriptions

### Testing Accessibility

```bash
# Run accessibility tests
npm run test:a11y

# Manual testing checklist
# - Keyboard navigation
# - Screen reader compatibility
# - Color contrast
# - Focus management
```

## Troubleshooting

### Common Issues

**Build Errors:**

- Check Node.js version (requires 18+)
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run check`

**API Connection Issues:**

- Verify backend is running
- Check environment variables
- Ensure CORS is configured properly
- Check network connectivity

**Styling Issues:**

- Restart dev server after Tailwind changes
- Check CSS import order
- Verify Tailwind classes are correct

### Debug Mode

Enable debug mode for additional logging:

```env
VITE_DEV_MODE=true
VITE_DEBUG=true
```

## Contributing

### Development Guidelines

1. **Follow Svelte conventions**
2. **Use TypeScript** for all new code
3. **Write tests** for new features
4. **Follow accessibility guidelines**
5. **Use conventional commit messages**

### Code Style

- Use Prettier for formatting
- Follow ESLint rules
- Use meaningful variable names
- Add JSDoc comments for functions

### Pull Request Process

1. Create feature branch
2. Make changes with tests
3. Run quality checks
4. Submit PR with description
5. Address review feedback

## License

[Add your license information here]

## Support

For issues and questions:

- Check the troubleshooting section above
- Review the [SvelteKit documentation](https://kit.svelte.dev/docs)
- Create an issue in the project repository
- Check the backend API documentation

## Changelog

### Version 1.0.0

- Initial release
- Calendar integration
- Responsive design
- TypeScript support
