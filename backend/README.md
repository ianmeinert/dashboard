# Kiosk Dashboard Backend

A FastAPI-based backend service for managing kiosk dashboard functionality with Google Calendar integration, weather/forecast support, and a robust, database-backed grocery list.

## Features

- **Google Calendar Integration**: Fetch upcoming events via OAuth2 authentication
- **Weather & Forecast API**: Fetch current weather and 5-day forecast by geolocation (lat/lon), city/state, or zip code
- **Grocery List API**: Add, edit, delete, and check off grocery items with priority, category, and notes (async SQLAlchemy + SQLite)
- **RESTful API**: Clean, documented endpoints following OpenAPI standards
- **Security**: Secure credential management and OAuth2 flow
- **Monitoring**: Health checks and system monitoring endpoints
- **Robust Error Handling**: Graceful error messages for upstream and internal errors

## API Endpoints

### Calendar

- `GET /api/calendar/events` - Retrieve upcoming calendar events
- `GET /api/calendar/health` - Calendar service health check

### Weather

- `GET /api/weather/current` - Get current weather by lat/lon, city/state, or zip code
- `GET /api/weather/forecast` - Get 5-day forecast by lat/lon, city/state, or zip code

#### Weather Endpoint Usage Examples

- By geolocation:
  - `/api/weather/current?lat=30.2672&lon=-97.7431`
  - `/api/weather/forecast?lat=30.2672&lon=-97.7431`
- By city/state:
  - `/api/weather/current?city=Austin&state=TX`
  - `/api/weather/forecast?city=Austin&state=TX`
- By zip code:
  - `/api/weather/current?zip_code=78701`
  - `/api/weather/forecast?zip_code=78701`

### Grocery List

- `GET /api/grocery/` - Get all grocery items
- `POST /api/grocery/` - Add new grocery item
- `GET /api/grocery/{item_id}` - Get specific item
- `PUT /api/grocery/{item_id}` - Update item
- `DELETE /api/grocery/{item_id}` - Delete item
- `PATCH /api/grocery/{item_id}/toggle` - Toggle completion status
- `DELETE /api/grocery/` - Clear all completed items

#### Grocery List Data Model

- All grocery items are stored in `backend/data/dashboard.db` (SQLite) using async SQLAlchemy ORM.
- On first run, any legacy grocery data in `grocery_list.json` is automatically migrated to the database.
- Example item:

```json
{
  "id": 1,
  "name": "Bananas",
  "quantity": "2 lbs",
  "category": "Produce",
  "notes": "",
  "priority": "medium",
  "completed": false,
  "created_at": "2024-07-01T12:34:56.789Z",
  "updated_at": "2024-07-01T12:34:56.789Z"
}
```

### Monitoring

- `GET /api/monitoring/health` - Overall system health status
- `GET /api/monitoring/status` - Detailed system status

## Geolocation Fallback Logic

- The backend supports weather queries by geolocation (lat/lon), city/state, or zip code.
- If geolocation is not available, the frontend falls back to a default location (Austin, TX).
- All endpoints provide robust error handling and user-friendly error messages.

## Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud Platform account
- Google Calendar API enabled
- OpenWeatherMap API key

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
   ```

3. **Install dependencies:**

   ```bash
   uv pip install -r requirements.txt
   ```

4. **Set up credentials:**
   - See the main [README.md](../README.md#credentials-setup) for detailed credentials setup instructions
   - Ensure `backend/data/credentials.json` is properly configured with Google Calendar and OpenWeatherMap credentials

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

### Weather Endpoint

**GET** `/api/weather/current` or `/api/weather/forecast`

Query Parameters:

- `lat`, `lon`: Latitude and longitude (preferred for geolocation)
- `city`, `state`: City and state (fallback)
- `zip_code`: US zip code (fallback)

**Response Example:**

```json
{
  "weather": {
    "coord": { "lon": -97.7431, "lat": 30.2672 },
    "weather": [ { "id": 800, "main": "Clear", "description": "clear sky", "icon": "01d" } ],
    "main": { "temp": 75.2, "humidity": 60 },
    ...
  }
}
```

### Grocery List Endpoint

**GET** `/api/grocery/`

Retrieve all grocery items (optionally filter by completion status).

**POST** `/api/grocery/`

Add a new grocery item (fields: name, quantity, category, notes, priority).

**PUT** `/api/grocery/{item_id}`

Update an existing grocery item.

**PATCH** `/api/grocery/{item_id}/toggle`

Toggle completion status.

**DELETE** `/api/grocery/{item_id}`

Delete a grocery item.

**DELETE** `/api/grocery/`

Clear all completed items.

## Development

### Project Structure

```
backend/
├── api/                 # API route modules
│   ├── calendar.py     # Calendar endpoints
│   ├── monitoring.py   # Monitoring endpoints
│   ├── weather.py      # Weather endpoints
│   └── grocery.py      # Grocery list endpoints (async SQLAlchemy)
├── schemas/            # Pydantic models
│   ├── calendar.py     # Calendar data models
│   └── grocery.py      # Grocery data models
├── models.py           # SQLAlchemy ORM models and async DB setup
├── utils/              # Utility functions
│   ├── google_calendar.py  # Google Calendar integration
│   ├── monitoring.py       # Monitoring utilities
│   ├── sync_token_db.py    # Token management
│   └── weather.py          # Weather/AQI utilities
├── data/               # Data storage (credentials, tokens, SQLite DB)
│   ├── credentials.json
│   ├── token.json
│   ├── dashboard.db    # SQLite database for all persistent data
│   └── grocery_list.json.migrated.json (legacy, after migration)
├── main.py             # FastAPI app entry point
└── requirements.txt    # Python dependencies
```

## Grocery List Improvements

- **Database-backed:** All grocery items are stored in `backend/data/dashboard.db` (SQLite), not a JSON file.
- **Automatic migration:** On first run, any existing grocery items in the old JSON file are migrated to the database.
- **Modern async API:** All grocery endpoints use async SQLAlchemy for performance and reliability.
- **Improved UX:**
  - Compact list view in dashboard mode
  - Friendly empty state with "Add Item" button
  - Full-featured add/edit/delete in expanded view
  - Priority, category, and notes support

## License

[Add your license information here]
