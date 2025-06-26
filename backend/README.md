# Kiosk Dashboard Backend

## Google Calendar Integration

This FastAPI backend provides an endpoint to fetch upcoming Google Calendar events for use in a kiosk-style dashboard.

### Features

- `/api/calendar/events`: Get upcoming events (read-only)

### Setup

1. Create a Google Cloud project and enable the Google Calendar API.
2. Download `credentials.json` (OAuth2 client secrets) and place it in the `backend/` directory.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI app:

   ```bash
   uvicorn main:app --reload
   ```

5. On first run, follow the OAuth2 flow in your browser to authorize access. Token will be saved as `token.json`.

### Security Notes

- **Never commit `credentials.json` or `token.json` to version control.**
- Store credentials securely and restrict file permissions.
- Only the minimum required OAuth2 scopes are used.

### API Example

```
GET /api/calendar/events
Response: [
  {
    "id": "abc123",
    "summary": "Meeting",
    "start": "2024-06-01T10:00:00Z",
    "end": "2024-06-01T11:00:00Z",
    "description": "Discuss project",
    "location": "Conference Room"
  },
  ...
]
```
