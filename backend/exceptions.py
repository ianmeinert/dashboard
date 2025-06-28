"""
Exception Handling

Provides custom exception classes and comprehensive error handling utilities
for the Family Dashboard API with secure error responses and proper logging.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class DashboardException(Exception):
    """Base exception class for dashboard-specific errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(DashboardException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationException(DashboardException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationException(DashboardException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundException(DashboardException):
    """Raised when a resource is not found."""
    
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" with id: {resource_id}"
        
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND"
        )


class ExternalAPIException(DashboardException):
    """Raised when external API calls fail."""
    
    def __init__(self, service: str, message: str, status_code: int = 502):
        super().__init__(
            message=f"{service} service error: {message}",
            status_code=status_code,
            error_code="EXTERNAL_API_ERROR",
            details={"service": service}
        )


class DatabaseException(DashboardException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        details = {"operation": operation} if operation else {}
        super().__init__(
            message=f"Database error: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details
        )


class RateLimitException(DashboardException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, retry_after: Optional[int] = None):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after} if retry_after else {}
        )


def create_error_response(
    error: Exception,
    include_details: bool = False,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        error: The exception that occurred
        include_details: Whether to include error details (for debugging)
        request_id: Optional request ID for tracking
        
    Returns:
        Dict: Standardized error response
    """
    from .config import settings

    # Base error response
    response = {
        "error": "Internal server error",
        "message": "An unexpected error occurred. Please try again later."
    }
    
    # Add request ID if available
    if request_id:
        response["request_id"] = request_id
    
    # Handle specific exception types
    if isinstance(error, DashboardException):
        response.update({
            "error": error.__class__.__name__,
            "message": error.message,
            "status_code": error.status_code
        })
        
        if error.error_code:
            response["error_code"] = error.error_code
            
        if error.details:
            response["details"] = error.details
    
    elif isinstance(error, HTTPException):
        response.update({
            "error": "HTTP Error",
            "message": error.detail,
            "status_code": error.status_code
        })
    
    elif isinstance(error, ValidationError):
        response.update({
            "error": "Validation Error",
            "message": "Invalid input data",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "error_code": "VALIDATION_ERROR",
            "details": [
                {
                    "field": " -> ".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"]
                }
                for err in error.errors()
            ]
        })
    
    elif isinstance(error, SQLAlchemyError):
        response.update({
            "error": "Database Error",
            "message": "Database operation failed",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error_code": "DATABASE_ERROR"
        })
    
    # Include additional details in debug mode
    if include_details and settings.debug:
        response["debug"] = {
            "exception_type": type(error).__name__,
            "exception_message": str(error)
        }
    
    return response


def log_exception(
    error: Exception,
    request: Request,
    include_stack_trace: bool = True
) -> None:
    """
    Log exception with context information.
    
    Args:
        error: The exception that occurred
        request: The FastAPI request object
        include_stack_trace: Whether to include stack trace
    """
    from .logging_config import log_security_event

    # Create context information
    context = {
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "exception_type": type(error).__name__,
        "exception_message": str(error)
    }
    
    # Log with appropriate level and context
    if isinstance(error, (ValidationException, NotFoundException)):
        logger.warning(f"Client error: {context}")
    elif isinstance(error, (AuthenticationException, AuthorizationException)):
        log_security_event(
            event_type="auth_error",
            message=f"{type(error).__name__}: {error.message}",
            client_ip=context["client_ip"],
            user_agent=context["user_agent"],
            request_id=getattr(request.state, "request_id", None),
            extra_fields=context
        )
    elif isinstance(error, RateLimitException):
        log_security_event(
            event_type="rate_limit_exceeded",
            message="Rate limit exceeded",
            client_ip=context["client_ip"],
            user_agent=context["user_agent"],
            request_id=getattr(request.state, "request_id", None),
            extra_fields=context
        )
    else:
        if include_stack_trace:
            logger.error(f"Server error: {context}", exc_info=True)
        else:
            logger.error(f"Server error: {context}")


async def handle_dashboard_exception(request: Request, exc: DashboardException) -> JSONResponse:
    """Handle dashboard-specific exceptions."""
    log_exception(exc, request, include_stack_trace=False)
    
    response_data = create_error_response(exc)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    log_exception(exc, request, include_stack_trace=False)
    
    response_data = create_error_response(exc)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_data
    )


async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    log_exception(exc, request, include_stack_trace=False)
    
    response_data = create_error_response(exc)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def handle_database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors."""
    log_exception(exc, request, include_stack_trace=True)
    
    response_data = create_error_response(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data
    )


async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions."""
    log_exception(exc, request, include_stack_trace=True)
    
    response_data = create_error_response(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data
    ) 