"""
Google Calendar Integration Backend

This FastAPI app provides an endpoint to fetch upcoming Google Calendar events.
OAuth2 credentials are stored locally. Events are fetched live from Google API.

Features:
- /api/calendar/events: Get upcoming events (read-only)
- /api/grocery: Manage grocery list items

Version: 0.1.0
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import calendar, grocery, monitoring, weather
from .api.grocery import migrate_json_to_db
from .models import init_db


async def lifespan(app: FastAPI):
    # Run DB initialization and migration at startup
    await init_db()
    await migrate_json_to_db()
    yield
    # (Optional) Add shutdown logic here

app = FastAPI(
    title="Dashboard API",
    description="Backend API for the touchscreen dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # SvelteKit dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(calendar.calendar_router, prefix="/api/calendar", tags=["calendar"])
app.include_router(monitoring.monitoring_router, prefix="/api/monitoring", tags=["monitoring"])
app.include_router(weather.weather_router, prefix="/api/weather", tags=["weather"])
app.include_router(grocery.grocery_router, prefix="/api/grocery", tags=["grocery"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "calendar": "/api/calendar",
            "monitoring": "/api/monitoring",
            "weather": "/api/weather",
            "grocery": "/api/grocery"
        }
    }

@app.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "healthy"}
