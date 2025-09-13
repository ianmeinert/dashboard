"""
Google Calendar Integration

Provides functionality to fetch and manage Google Calendar events.
- credentials.json must be kept secure and not committed to version control.
- Token is stored locally for persistent access.
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .sync_token_db import (get_sync_token,
                            set_sync_token)

from ..models.schemas.calendar import CalendarEvent

logger = logging.getLogger(__name__)

# Suppress verbose logging from Google API client
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CREDENTIALS_FILE = os.path.join(DATA_DIR, "credentials.json")
TOKEN_FILE = os.path.join(DATA_DIR, "token.json")

def get_google_calendar_service():
    """Get authenticated Google Calendar service."""
    creds = None
   
    # Load credentials securely
    try:
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            logger.debug("Loaded existing Google Calendar token")
       
        # If there are no (valid) credentials available
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.debug("Refreshing expired Google Calendar token")
                creds.refresh(Request())
                
                # Save the refreshed credentials
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                logger.debug("Refreshed credentials saved")
            else:
                # No valid credentials - cannot proceed in headless environment
                logger.error("No valid Google Calendar credentials found")
                logger.error("Initial authentication required. Please run the setup script with GUI access:")
                logger.error("python3 setup_google_auth.py")
                raise Exception(
                    "Google Calendar authentication required. "
                    "Run setup_google_auth.py on a machine with GUI access, "
                    "then copy the token file to this server."
                )
       
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        logger.info("Google Calendar service initialized successfully")
        return service
       
    except Exception as e:
        logger.error(f"Failed to initialize Google Calendar service: {type(e).__name__}")
        raise

async def get_upcoming_events(start: Optional[str] = None, end: Optional[str] = None) -> List[CalendarEvent]:
    """Fetch Google Calendar events (all calendars) in a date range.
    
    Args:
        start: Start date in ISO format (default: now)
        end: End date in ISO format (default: 7 days from now)
        
    Returns:
        List of calendar events
    """
    try:
        service = get_google_calendar_service()
        
        # Set default date range if not provided
        if not start:
            start = datetime.now(timezone.utc).isoformat()
        if not end:
            end = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        
        logger.debug("Fetching Google Calendar events", extra={
            "extra_fields": {
                "start_date": start,
                "end_date": end,
                "calendars": "all"
            }
        })
        
        # Get all calendars
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        all_events = []
        
        for calendar in calendars:
            calendar_id = calendar['id']
            calendar_name = calendar.get('summary', 'Unknown')
            colorId = calendar.get('colorId', "1")
            logger.info(f"Processing calendar: {calendar} with colorId: {colorId}")
            
            logger.debug(f"Fetching events for calendar: {calendar_name}", extra={
                "extra_fields": {
                    "calendar_id": calendar_id,
                    "calendar_name": calendar_name
                }
            })
            
            try:
                # Get sync token for this calendar
                sync_token = get_sync_token(calendar_id)
                
                # Prepare list parameters
                list_kwargs = {
                    "calendarId": calendar_id,
                    "timeMin": start,
                    "timeMax": end,
                    "singleEvents": True,
                    "orderBy": "startTime",
                    "pageToken": None
                }
                
                # Only use syncToken if no custom range is requested
                if sync_token and not start and not end:
                    list_kwargs["syncToken"] = sync_token
                
                events_result = service.events().list(**list_kwargs).execute()
                events = events_result.get('items', [])
                
                # If sync token is invalid, do a full sync
                if events_result.get('nextSyncToken') is None and sync_token:
                    logger.warning(f"Invalid sync token for calendar {calendar_name}, doing full sync")
                    sync_token = None
                    list_kwargs.pop("syncToken", None)
                    events_result = service.events().list(**list_kwargs).execute()
                    events = events_result.get('items', [])
                
                # Process events
                for event in events:
                    logger.info(f"Processing color_id: {event.get('colorId')} for calendar {calendar_name}")
                    event_obj = CalendarEvent(
                        id=event['id'],
                        summary=event.get('summary', 'No Title'),
                        start=event['start'].get('dateTime', event['start'].get('date')),
                        end=event['end'].get('dateTime', event['end'].get('date')),
                        description=event.get('description', ''),
                        location=event.get('location', ''),
                        calendarId=calendar_id,
                        calendarName=calendar_name,
                        color_id=event.get('colorId'),
                        color_class = f"{calendar.get('backgroundColor', '')} {calendar.get('foregroundColor', '')}".strip()
                    )
                    all_events.append(event_obj)
                
                # Handle pagination
                page_token = events_result.get("nextPageToken")
                while page_token:
                    list_kwargs["pageToken"] = page_token
                    events_result = service.events().list(**list_kwargs).execute()
                    events = events_result.get('items', [])
                    
                    for event in events:
                        logger.debug(f"Processing color_id: {event.get('colorId')} for calendar {calendar_name}")
                        event_obj = CalendarEvent(
                            id=event['id'],
                            summary=event.get('summary', 'No Title'),
                            start=event['start'].get('dateTime', event['start'].get('date')),
                            end=event['end'].get('dateTime', event['end'].get('date')),
                            description=event.get('description', ''),
                            location=event.get('location', ''),
                            calendarId=calendar_id,
                            calendarName=calendar_name,
                            color_id=event.get('colorId'),
                            color_class = f"{calendar.get('backgroundColor', '')} {calendar.get('foregroundColor', '')}".strip()

                        )
                        all_events.append(event_obj)
                    
                    page_token = events_result.get("nextPageToken")
                    if not page_token:
                        # Store new sync token if present and not a custom range
                        new_sync_token = events_result.get("nextSyncToken")
                        if new_sync_token and not start and not end:
                            set_sync_token(calendar_id, new_sync_token)
                
                logger.debug(f"Retrieved {len(events)} events from calendar {calendar_name}")
                
            except Exception as e:
                logger.error(f"Error fetching events for calendar {calendar_name}: {type(e).__name__}: {str(e)}", exc_info=True)
                continue
        
        logger.info(f"Successfully retrieved {len(all_events)} total events from {len(calendars)} calendars")
        return all_events
        
    except Exception as e:
        logger.error(f"Failed to fetch Google Calendar events: {type(e).__name__}: {str(e)}", exc_info=True)
        raise