# Kiosk Dashboard Backend

A FastAPI-based backend service for managing kiosk dashboard functionality with Google Calendar integration.

## Features

- **Google Calendar Integration**: Fetch upcoming events via OAuth2 authentication
- **RESTful API**: Clean, documented endpoints following OpenAPI standards
- **Security**: Secure credential management and OAuth2 flow
- **Monitoring**: Health checks and system monitoring endpoints

## API Endpoints

### Calendar

- `GET /api/calendar/events` - Retrieve upcoming calendar events
- `GET /api/calendar/health` - Calendar service health check

### Monitoring

- `GET /api/monitoring/health` - Overall system health status
- `GET /api/monitoring/status` - Detailed system status

## Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud Platform account
- Google Calendar API enabled

### Installation

1. **Clone and navigate to the backend directory:**

   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**

   ```bash
   # Using uv (recommended)
   uv venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/macOS
   
   # Or using venv
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/macOS
   ```

3. **Install dependencies:**

   ```bash
   # Using uv
   uv pip install -r requirements.txt
   
   # Or using pip
   pip install -r requirements.txt
   ```

4. **Set up Google Calendar credentials:**
   - Create a Google Cloud project
   - Enable the Google Calendar API
   - Create OAuth2 credentials
   - Download `credentials.json` and place it in the `backend/` directory

5. **Run the application:**

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Complete OAuth2 setup:**
   - Visit `http://localhost:8000/docs` for API documentation
   - On first run, follow the OAuth2 authorization flow
   - Token will be automatically saved as `token.json`

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Application
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
```

### Security Configuration

- **Never commit sensitive files to version control**
- Store `credentials.json` and `token.json` securely
- Use environment variables for configuration
- Restrict file permissions on credential files

## API Documentation

### Calendar Events Endpoint

**GET** `/api/calendar/events`

Retrieve upcoming calendar events.

**Query Parameters:**

- `days` (optional): Number of days to look ahead (default: 7)
- `max_events` (optional): Maximum number of events to return (default: 10)

**Response Example:**

```json
[
  {
    "id": "abc123def456",
    "summary": "Team Meeting",
    "start": "2024-06-01T10:00:00Z",
    "end": "2024-06-01T11:00:00Z",
    "description": "Weekly team sync meeting",
    "location": "Conference Room A",
    "attendees": [
      {
        "email": "user@example.com",
        "displayName": "John Doe"
      }
    ]
  }
]
```

### Health Check Endpoint

**GET** `/api/monitoring/health`

Check system health status.

**Response Example:**

```json
{
  "status": "healthy",
  "timestamp": "2024-06-01T10:00:00Z",
  "version": "1.0.0",
  "services": {
    "calendar": "healthy",
    "database": "healthy"
  }
}
```

## Development

### Project Structure

```
backend/
├── api/                 # API route modules
│   ├── calendar.py     # Calendar endpoints
│   └── monitoring.py   # Monitoring endpoints
├── schemas/            # Pydantic models
│   └── calendar.py     # Calendar data models
├── utils/              # Utility functions
│   ├── google_calendar.py  # Google Calendar integration
│   ├── monitoring.py       # Monitoring utilities
│   └── sync_token_db.py    # Token management
├── data/               # Data storage
├── main.py             # FastAPI application entry point
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=api --cov=utils --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

## Security Considerations

### OAuth2 Implementation

- Uses Google OAuth2 for secure calendar access
- Implements token refresh mechanism
- Stores tokens securely in local filesystem
- Minimal required scopes: `https://www.googleapis.com/auth/calendar.readonly`

### Best Practices

- **Input Validation**: All inputs validated using Pydantic models
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes
- **Logging**: Structured logging for debugging and monitoring
- **Rate Limiting**: Consider implementing rate limiting for production
- **CORS**: Configure CORS appropriately for your frontend domain

### Production Deployment

1. **Use HTTPS**: Always use HTTPS in production
2. **Environment Variables**: Store all secrets in environment variables
3. **Process Management**: Use Gunicorn or similar for production
4. **Monitoring**: Implement proper logging and monitoring
5. **Backup**: Regular backup of token and configuration data

## Troubleshooting

### Common Issues

**OAuth2 Authorization Error:**

- Ensure `credentials.json` is properly formatted
- Check that Google Calendar API is enabled
- Verify redirect URIs in Google Cloud Console

**Token Refresh Issues:**

- Delete `token.json` and re-authenticate
- Check network connectivity to Google APIs

**Import Errors:**

- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Logs

Check application logs for detailed error information:

```bash
# View logs in development
uvicorn main:app --reload --log-level debug
```

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation for API changes
5. Use conventional commit messages

## License

[Add your license information here]

## Support

For issues and questions:

- Check the troubleshooting section above
- Review API documentation at `/docs` when running
- Create an issue in the project repository
