"""
Calendar API Router

Provides endpoints for Google Calendar integration.

Features:
- /events: Get upcoming events from Google Calendar
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query, status

from ..models.schemas.calendar import CalendarEvent
from ..services.calendar_service import get_upcoming_events
from ..services.monitoring_service import log_error, monitor_performance

calendar_router = APIRouter()

@calendar_router.get("/events", response_model=List[CalendarEvent])
@monitor_performance("/api/calendar/events")
@log_error("CALENDAR_EVENTS_ERROR")
async def get_events(
    start: str = Query(None, description="Start date/time (ISO 8601, inclusive)"),
    end: str = Query(None, description="End date/time (ISO 8601, exclusive)")
) -> List[CalendarEvent]:
    """Fetch Google Calendar events in a date range.

    Args:
        start: ISO 8601 start datetime (inclusive)
        end: ISO 8601 end datetime (exclusive)
    Returns:
        List[CalendarEvent]: List of events in the range
    Raises:
        HTTPException: If fetching events fails or if range is missing
    """
    if not start or not end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both 'start' and 'end' query parameters are required (ISO 8601 format)."
        )
    try:
        events = await get_upcoming_events(start=start, end=end)
    except Exception as exc:
        print(exc)
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {exc}") from exc
    return events
