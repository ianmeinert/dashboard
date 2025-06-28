"""
Family Dashboard Backend API

A FastAPI application providing endpoints for calendar integration, weather data,
grocery list management, and system monitoring with enhanced security and performance.

Features:
- Google Calendar integration with OAuth2
- Weather data from OpenWeatherMap API
- Grocery list management with SQLite database
- System monitoring and health checks
- Rate limiting and security headers
- Connection pooling and memory management
- Comprehensive exception handling
- Structured logging with file rotation

Version: 2.0.0
"""

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from .api import calendar, grocery, monitoring, weather
from .config import settings
from .database import close_db, init_db
from .exceptions import (DashboardException, handle_dashboard_exception,
                         handle_database_error, handle_generic_exception,
                         handle_http_exception, handle_validation_error)
from .http_client import http_client
from .logging_config import log_request, log_security_event, setup_logging
from .security import add_security_headers, get_client_id, rate_limiter

# Setup structured logging
setup_logging()

# Get logger for this module
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Family Dashboard API", extra={
        "extra_fields": {
            "version": settings.app_version,
            "debug_mode": settings.debug,
            "host": settings.host,
            "port": settings.port
        }
    })
    
    # Initialize database
    await init_db()
    logger.info("Database initialized", extra={
        "extra_fields": {"database_url": settings.database_url}
    })
    
    # Run migrations
    from .api.grocery import migrate_json_to_db
    await migrate_json_to_db()
    logger.info("Migrations completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Family Dashboard API")
    
    # Close HTTP client
    await http_client.close()
    logger.info("HTTP client closed")
    
    # Close database connections
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Backend API for the Family Dashboard with enhanced security and performance",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
    ],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to all requests for tracking."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing and response data."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log request
    log_request(
        logger=logger,
        request=request,
        response=response,
        duration=duration,
        extra_fields={
            "response_size_bytes": len(response.body) if hasattr(response, 'body') else 0,
        }
    )
    
    return response


# Security middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Add security headers and rate limiting."""
    # Rate limiting
    client_id = get_client_id(request)
    if not rate_limiter.is_allowed(
        client_id, 
        settings.rate_limit_requests, 
        settings.rate_limit_window
    ):
        # Log rate limit event
        log_security_event(
            event_type="rate_limit_exceeded",
            message="Rate limit exceeded",
            client_ip=client_id,
            user_agent=request.headers.get("user-agent", "unknown"),
            request_id=getattr(request.state, "request_id", None),
            extra_fields={
                "rate_limit_requests": settings.rate_limit_requests,
                "rate_limit_window": settings.rate_limit_window,
                "url": str(request.url),
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add security headers
    add_security_headers(request, response)
    
    # Add rate limit headers
    remaining = rate_limiter.get_remaining(
        client_id, 
        settings.rate_limit_requests, 
        settings.rate_limit_window
    )
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(settings.rate_limit_window)
    
    return response


# Exception handlers
@app.exception_handler(DashboardException)
async def dashboard_exception_handler(request: Request, exc: DashboardException):
    """Handle dashboard-specific exceptions."""
    return await handle_dashboard_exception(request, exc)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    return await handle_validation_error(request, exc)


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors."""
    return await handle_database_error(request, exc)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all other unhandled exceptions."""
    return await handle_generic_exception(request, exc)


# Include API routers
app.include_router(
    calendar.calendar_router, 
    prefix="/api/calendar", 
    tags=["calendar"]
)
app.include_router(
    monitoring.monitoring_router, 
    prefix="/api/monitoring", 
    tags=["monitoring"]
)
app.include_router(
    weather.weather_router, 
    prefix="/api/weather", 
    tags=["weather"]
)
app.include_router(
    grocery.grocery_router, 
    prefix="/api/grocery", 
    tags=["grocery"]
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "endpoints": {
            "calendar": "/api/calendar",
            "monitoring": "/api/monitoring",
            "weather": "/api/weather",
            "grocery": "/api/grocery",
            "docs": "/docs" if settings.debug else None,
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    from .database import check_db_health
    
    db_healthy = await check_db_health()
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "healthy" if db_healthy else "unhealthy",
        "version": settings.app_version,
    }


@app.get("/info")
async def info():
    """Application information endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "environment": "development" if settings.debug else "production",
    }
