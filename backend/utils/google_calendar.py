"""
Google Calendar Utility

Handles OAuth2 and fetching events from Google Calendar API.

Security Notes:
- credentials.json must be kept secure and not committed to version control.
- Token is stored locally for persistent access.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..schemas.calendar import CalendarEvent
from .sync_token_db import (get_all_calendar_colors, get_calendar_color,
                            get_sync_token, set_calendar_color, set_sync_token)

# Suppress the file_cache warning
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CREDENTIALS_FILE = os.path.join(DATA_DIR, "credentials.json")
TOKEN_FILE = os.path.join(DATA_DIR, "token.json")

_event_cache = None
_event_cache_time = None
CACHE_DURATION = timedelta(minutes=2)

# Define the color palette for calendars
CALENDAR_COLORS = [
    "bg-blue-100 text-blue-800 hover:bg-blue-200 border-blue-400",
    "bg-green-100 text-green-800 hover:bg-green-200 border-green-400",
    "bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-yellow-400",
    "bg-red-100 text-red-800 hover:bg-red-200 border-red-400",
    "bg-purple-100 text-purple-800 hover:bg-purple-200 border-purple-400",
    "bg-pink-100 text-pink-800 hover:bg-pink-200 border-pink-400",
    "bg-indigo-100 text-indigo-800 hover:bg-indigo-200 border-indigo-400",
    "bg-teal-100 text-teal-800 hover:bg-teal-200 border-teal-400",
    "bg-orange-100 text-orange-800 hover:bg-orange-200 border-orange-400",
    "bg-cyan-100 text-cyan-800 hover:bg-cyan-200 border-cyan-400",
    "bg-lime-100 text-lime-800 hover:bg-lime-200 border-lime-400",
    "bg-rose-100 text-rose-800 hover:bg-rose-200 border-rose-400",
]

def assign_calendar_color(calendar_id: str) -> str:
    """Assign a color to a calendar if it doesn't have one.
    
    Args:
        calendar_id: The calendar ID to assign a color to
        
    Returns:
        The CSS color class assigned to the calendar
    """
    # Check if calendar already has a color
    existing_color = get_calendar_color(calendar_id)
    if existing_color:
        return existing_color['color_class']
    
    # Get all existing colors to find the next available index
    existing_colors = get_all_calendar_colors()
    used_indices = {color_info['color_index'] for color_info in existing_colors.values()}
    
    # Find the first available color index
    color_index = 0
    while color_index in used_indices and color_index < len(CALENDAR_COLORS):
        color_index += 1
    
    # If we've used all colors, cycle back to the beginning
    if color_index >= len(CALENDAR_COLORS):
        color_index = 0
    
    color_class = CALENDAR_COLORS[color_index]
    
    # Save the color assignment
    set_calendar_color(calendar_id, color_index, color_class)
    
    return color_class

async def get_upcoming_events(start: Optional[str] = None, end: Optional[str] = None) -> List[CalendarEvent]:
    """Fetch Google Calendar events (all calendars) in a date range.

    Args:
        start: Optional ISO 8601 start datetime (inclusive)
        end: Optional ISO 8601 end datetime (exclusive)
    Returns:
        List[CalendarEvent]: List of events in the range
    Raises:
        Exception: If authentication or API call fails
    """
    now = datetime.now(timezone.utc)
    global _event_cache, _event_cache_time
    # Only cache if no custom range is requested
    if start is None and end is None and _event_cache is not None and _event_cache_time is not None:
        if now - _event_cache_time < CACHE_DURATION:
            return _event_cache
    def _fetch_events_sync():
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=8080)
            with open(TOKEN_FILE, "w", encoding="utf-8") as token:
                token.write(creds.to_json())
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        calendar_list = service.calendarList().list().execute()
        all_events = []
        for calendar in calendar_list.get("items", []):
            calendar_id = calendar.get("id", "")
            calendar_name = calendar.get("summary", "Other")
            
            # Ensure calendar has a color assigned
            assign_calendar_color(calendar_id)
            
            sync_token = get_sync_token(calendar_id)
            events = []
            page_token = None
            full_sync = False
            while True:
                try:
                    list_kwargs = {
                        "calendarId": calendar_id,
                        "singleEvents": True,
                        "orderBy": "startTime",
                        "pageToken": page_token
                    }
                    # Only use syncToken if no custom range is requested
                    if sync_token and not full_sync and start is None and end is None:
                        list_kwargs["syncToken"] = sync_token
                    else:
                        # Use timeMin/timeMax if provided, else default to now and no max
                        if start:
                            list_kwargs["timeMin"] = start
                        else:
                            list_kwargs["timeMin"] = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
                        if end:
                            list_kwargs["timeMax"] = end
                        list_kwargs["maxResults"] = 2500  # Google API max per page
                    events_result = service.events().list(**list_kwargs).execute()
                except Exception as e:
                    # If sync token is invalid, do a full sync
                    if hasattr(e, 'resp') and getattr(e.resp, 'status', None) == 410:
                        sync_token = None
                        full_sync = True
                        continue
                    else:
                        raise
                for event in events_result.get("items", []):
                    start_info = event.get("start", {})
                    end_info = event.get("end", {})
                    start_val = start_info.get("dateTime") or start_info.get("date") or ""
                    end_val = end_info.get("dateTime") or end_info.get("date") or ""
                    all_events.append({
                        "id": event.get("id", ""),
                        "summary": event.get("summary", "(No Title)"),
                        "start": start_val,
                        "end": end_val,
                        "calendarId": calendar_id,
                        "calendarName": calendar_name,
                        "description": event.get("description") or "",
                        "location": event.get("location") or "",
                    })
                page_token = events_result.get("nextPageToken")
                if not page_token:
                    # Store new sync token if present and not a custom range
                    new_sync_token = events_result.get("nextSyncToken")
                    if new_sync_token and start is None and end is None:
                        set_sync_token(calendar_id, new_sync_token)
                    break
        def get_event_start(event):
            return event["start"]
        all_events.sort(key=get_event_start)
        return [CalendarEvent(**event) for event in all_events]
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _fetch_events_sync)
    if start is None and end is None:
        _event_cache = result
        _event_cache_time = now
    return result 