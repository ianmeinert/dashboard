"""
Calendar Event Schema

Defines the Pydantic model for a Google Calendar event.
"""

from typing import Optional

from pydantic import BaseModel


class CalendarEvent(BaseModel):
    """Google Calendar event model.

    Attributes:
        id: Event unique identifier
        summary: Event title
        start: Event start datetime (ISO8601)
        end: Event end datetime (ISO8601)
        description: Optional event description
        location: Optional event location
    """
    id: str
    summary: str
    start: str
    end: str
    calendarId: str
    calendarName: str
    description: Optional[str] = None
    location: Optional[str] = None
    color_id: Optional[str] = None
    color_class: Optional[str] = None
