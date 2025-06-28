"""
Security Utilities

Provides security features including rate limiting, input validation,
secure error handling, and CORS configuration.
"""

import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from ..core.config import settings


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, client_id: str, max_requests: int, window: int) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            client_id: Unique identifier for the client (IP, user ID, etc.)
            max_requests: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            bool: True if request is allowed, False otherwise
        """
        now = time.time()
        # Remove old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < window
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) < max_requests:
            self.requests[client_id].append(now)
            return True
        
        return False
    
    def get_remaining(self, client_id: str, max_requests: int, window: int) -> int:
        """Get remaining requests for a client."""
        now = time.time()
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < window
        ]
        return max(0, max_requests - len(self.requests[client_id]))


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_id(request: Request) -> str:
    """Get unique client identifier for rate limiting."""
    # Use X-Forwarded-For for proxy support, fallback to client.host
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def validate_coordinates(lat: float, lon: float) -> Tuple[float, float]:
    """
    Validate and sanitize coordinates.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Tuple[float, float]: Validated coordinates
        
    Raises:
        HTTPException: If coordinates are invalid
    """
    if not (-90 <= lat <= 90):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latitude must be between -90 and 90 degrees"
        )
    
    if not (-180 <= lon <= 180):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Longitude must be between -180 and 180 degrees"
        )
    
    return float(lat), float(lon)


def validate_location_input(
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None
) -> None:
    """
    Validate location input parameters.
    
    Args:
        city: City name
        state: State/province
        zip_code: ZIP/postal code
        
    Raises:
        HTTPException: If input is invalid
    """
    if city and len(city.strip()) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City name too long (max 100 characters)"
        )
    
    if state and len(state.strip()) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State name too long (max 50 characters)"
        )
    
    if zip_code and not zip_code.strip().replace("-", "").isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ZIP code format"
        )


def secure_error_response(error: Exception, include_details: bool = False) -> Dict:
    """
    Create a secure error response without exposing sensitive information.
    
    Args:
        error: The exception that occurred
        include_details: Whether to include error details (for debugging)
        
    Returns:
        Dict: Secure error response
    """
    if include_details and settings.debug:
        return {
            "error": "Internal server error",
            "detail": str(error),
            "type": type(error).__name__
        }
    
    # Log the full error for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Application error: {error}", exc_info=True)
    
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred. Please try again later."
    }


def handle_validation_error(error: ValidationError) -> Dict:
    """
    Handle Pydantic validation errors securely.
    
    Args:
        error: Pydantic validation error
        
    Returns:
        Dict: User-friendly error response
    """
    errors = []
    for err in error.errors():
        field = " -> ".join(str(loc) for loc in err["loc"])
        message = err["msg"]
        errors.append(f"{field}: {message}")
    
    return {
        "error": "Validation error",
        "details": errors
    }


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    import os
    import re

    # Remove path separators and other dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    # Ensure it's not empty
    if not sanitized.strip():
        sanitized = "unnamed"
    
    return sanitized


def validate_file_path(file_path: str, allowed_dirs: List[str]) -> bool:
    """
    Validate file path to prevent path traversal attacks.
    
    Args:
        file_path: Path to validate
        allowed_dirs: List of allowed base directories
        
    Returns:
        bool: True if path is safe, False otherwise
    """
    import os
    
    try:
        # Resolve the path
        resolved_path = os.path.abspath(file_path)
        
        # Check if path is within allowed directories
        for allowed_dir in allowed_dirs:
            allowed_abs = os.path.abspath(allowed_dir)
            if resolved_path.startswith(allowed_abs):
                return True
        
        return False
    except Exception:
        return False


# Security headers middleware
def add_security_headers(request: Request, response):
    """Add security headers to responses."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Add CSP header for additional security
    # Allow Swagger UI CDN resources for /docs endpoint
    if request.url.path == "/docs":
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net https://unpkg.com; "
            "connect-src 'self';"
        )
    else:
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self';"
        )
    response.headers["Content-Security-Policy"] = csp_policy 