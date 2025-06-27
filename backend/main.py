"""
Google Calendar Integration Backend

This FastAPI app provides an endpoint to fetch upcoming Google Calendar events.
OAuth2 credentials are stored locally. Events are fetched live from Google API.

Features:
- /api/calendar/events: Get upcoming events (read-only)

Author: Your Name
Version: 0.1.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import calendar, monitoring, weather

app = FastAPI(
    title="Dashboard API",
    description="Backend API for the touchscreen dashboard",
    version="1.0.0"
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

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "calendar": "/api/calendar",
            "monitoring": "/api/monitoring"
        }
    }

@app.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "healthy"}
