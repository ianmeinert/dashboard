from datetime import datetime


def validate_datetime_string(dt_str: str) -> bool:
    """Validate ISO 8601 datetime string."""
    try:
        datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False
    
