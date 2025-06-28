# Configuration Guide

This guide covers all configuration options for the Family Dashboard, including API credentials, environment variables, and security settings.

## 🔑 API Credentials Setup

### Google Calendar API

The dashboard integrates with Google Calendar to display family events and appointments.

#### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "Family Dashboard")
4. Click "Create"

#### Step 2: Enable Google Calendar API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

#### Step 3: Create OAuth2 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Enter a name (e.g., "Family Dashboard Desktop")
5. Click "Create"
6. Download the credentials file (JSON format)

#### Step 4: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type
3. Fill in required fields:
   - App name: "Family Dashboard"
   - User support email: Your email
   - Developer contact information: Your email
4. Add scopes:
   - `https://www.googleapis.com/auth/calendar.readonly`
5. Add test users (your Google account)
6. Save and continue

### OpenWeatherMap API

The weather widget uses OpenWeatherMap for current conditions and forecasts.

#### Step 1: Create Account

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Click "Sign Up" and create a free account
3. Verify your email address

#### Step 2: Get API Key

1. Log in to your OpenWeatherMap account
2. Go to "My API Keys" in your profile
3. Copy your default API key
4. **Note**: New API keys may take a few hours to activate

#### Step 3: API Plan

The free plan includes:

- 1,000 calls per day
- Current weather data
- 5-day forecast
- Basic weather maps

For production use, consider upgrading to a paid plan.

## 📁 Credentials File Setup

### Step 1: Copy Template

```bash
cp templates/credentials_template.json backend/data/credentials.json
```

### Step 2: Edit Credentials

Open `backend/data/credentials.json` and replace the placeholder values:

```json
{
  "client_id": "your-google-oauth2-client-id.apps.googleusercontent.com",
  "client_secret": "your-google-oauth2-client-secret",
  "project_id": "your-google-cloud-project-id",
  "openweathermap_api_key": "your-openweathermap-api-key"
}
```

### Step 3: Verify Configuration

```bash
# Test Google Calendar connection
curl http://localhost:8000/api/calendar/health

# Test OpenWeatherMap connection
curl "http://localhost:8000/api/weather/current?city=Austin&state=TX"
```

## 🌍 Environment Variables

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Application Settings
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Google Calendar
GOOGLE_CALENDAR_ID=primary
EVENT_LOOKAHEAD_DAYS=7
MAX_EVENTS=10

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./data/dashboard.db

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Frontend Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=10000

# Application Configuration
VITE_APP_TITLE=Family Dashboard
VITE_REFRESH_INTERVAL=30000

# Development
VITE_DEV_MODE=true
```

### Production Environment Variables

For production deployment, use these secure settings:

```env
# Backend (.env)
DEBUG=false
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-very-secure-secret-key
DATABASE_URL=sqlite:///./data/dashboard.db
ALLOWED_ORIGINS=https://your-domain.com

# Frontend (.env)
VITE_API_BASE_URL=https://your-api-domain.com
VITE_APP_TITLE=Family Dashboard
VITE_REFRESH_INTERVAL=30000
VITE_DEV_MODE=false
```

## 🔒 Security Configuration

### Credential Security

- **Never commit credentials to version control**
- The `credentials.json` file is already in `.gitignore`
- Use environment variables for production deployments
- Restrict file permissions on credential files

### File Permissions

```bash
# Secure credential files
chmod 600 backend/data/credentials.json
chmod 600 backend/data/token.json

# Secure environment files
chmod 600 backend/.env
chmod 600 frontend/.env
```

### CORS Configuration

The backend includes CORS protection. Configure allowed origins in your `.env`:

```env
# Development
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Production
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

## 🗄️ Database Configuration

### SQLite (Default)

The dashboard uses SQLite by default, which requires no additional setup:

```env
DATABASE_URL=sqlite:///./data/dashboard.db
```

### PostgreSQL (Optional)

For production deployments, you can use PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost/dashboard
```

Install PostgreSQL dependencies:

```bash
uv pip install psycopg2-binary
```

## 📊 Monitoring Configuration

### Health Check Endpoints

The dashboard includes built-in health monitoring:

- `GET /api/monitoring/health` - Basic health status
- `GET /api/monitoring/status` - Detailed system status

### Logging Configuration

Configure logging levels in your `.env`:

```env
# Development
LOG_LEVEL=DEBUG

# Production
LOG_LEVEL=WARNING
```

## 🔧 Advanced Configuration

### Custom Calendar ID

To use a specific Google Calendar instead of the primary one:

```env
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
```

### Weather API Customization

Configure weather widget behavior:

```env
# Default location fallback
DEFAULT_CITY=Austin
DEFAULT_STATE=TX
DEFAULT_LAT=30.2672
DEFAULT_LON=-97.7431
```

### Refresh Intervals

Configure how often data refreshes:

```env
# Frontend refresh interval (milliseconds)
VITE_REFRESH_INTERVAL=30000

# Backend cache duration (seconds)
WEATHER_CACHE_DURATION=300
CALENDAR_CACHE_DURATION=600
```

## ✅ Configuration Validation

### Test Your Setup

Run these commands to verify your configuration:

```bash
# Test backend health
curl http://localhost:8000/api/monitoring/health

# Test Google Calendar
curl http://localhost:8000/api/calendar/health

# Test weather API
curl "http://localhost:8000/api/weather/current?city=Austin&state=TX"

# Test grocery API
curl http://localhost:8000/api/grocery/
```

### Common Issues

**Google Calendar not working:**

- Verify OAuth consent screen is configured
- Check that test users are added
- Ensure API is enabled in Google Cloud Console

**Weather not loading:**

- Verify OpenWeatherMap API key is correct
- Check that API key is activated (may take hours for new keys)
- Test API key directly on OpenWeatherMap website

**CORS errors:**

- Verify `ALLOWED_ORIGINS` includes your frontend URL
- Check that backend and frontend ports match configuration
- Ensure HTTPS is used in production

## 🔄 Configuration Updates

When updating configuration:

1. **Backup current settings** before making changes
2. **Test in development** before applying to production
3. **Update documentation** for team members
4. **Monitor logs** for any configuration-related errors

---

**Need help?** Check the [Troubleshooting Guide](troubleshooting.md) for common issues and solutions.
