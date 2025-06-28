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
- Prometheus metrics for monitoring and alerting

Version: 2.0.0
"""

import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from .api import calendar, grocery, monitoring, weather
from .config import settings
from .database import close_db, init_db
from .exceptions import (DashboardException, handle_dashboard_exception,
                         handle_database_error, handle_generic_exception,
                         handle_validation_error)
from .http_client import http_client, weather_client
from .logging_config import log_request, log_security_event, setup_logging
from .metrics import (get_metrics, record_health_check, record_rate_limit_hit,
                      setup_metrics_instrumentator)
from .security import add_security_headers, get_client_id, rate_limiter
from .utils.google_calendar import get_upcoming_events

# Setup structured logging
setup_logging()

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
        # Record rate limit hit in metrics
        record_rate_limit_hit(client_id)
        
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

# Setup Prometheus metrics instrumentator
if settings.debug or settings.metrics_enabled:
    try:
        instrumentator = setup_metrics_instrumentator()
        instrumentator.instrument(app).expose(app, should_gzip=True)
        logger.info("Prometheus metrics instrumentator configured")
    except Exception as e:
        logger.warning(f"Failed to setup metrics instrumentator: {e}")

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    try:
        metrics_data = get_metrics()
        return Response(
            content=metrics_data,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Error serving metrics: {e}")
        return Response(
            content=b"# Error generating metrics\n",
            media_type="text/plain; version=0.0.4; charset=utf-8",
            status_code=500
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
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs" if settings.debug else None,
        }
    }


async def check_openweathermap_health() -> dict:
    """Check OpenWeatherMap API health by fetching weather for Austin, TX."""
    try:
        # Austin, TX coordinates
        result = await weather_client.get_current_weather(lat=30.2672, lon=-97.7431)
        if result and "weather" in result:
            return {"status": "healthy"}
        return {"status": "unhealthy", "error": "No weather data returned"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_google_calendar_health() -> dict:
    """Check Google Calendar API health by fetching events for a short range."""
    try:
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        start = now.isoformat()
        end = (now + timedelta(minutes=1)).isoformat()
        events = await get_upcoming_events(start=start, end=end)
        return {"status": "healthy", "event_count": len(events)}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/health")
async def health():
    """Health check endpoint for DB, OpenWeatherMap, Google Calendar, and critical dependencies."""
    from .database import check_db_health
    start_time = time.time()
    
    # Run all checks in parallel
    db_task = asyncio.create_task(check_db_health())
    owm_task = asyncio.create_task(check_openweathermap_health())
    gcal_task = asyncio.create_task(check_google_calendar_health())
    
    db_healthy = await db_task
    owm_result = await owm_task
    gcal_result = await gcal_task
    duration = time.time() - start_time
    
    # Compose detailed status
    checks = {
        "database": {"status": "healthy" if db_healthy else "unhealthy"},
        "openweathermap": owm_result,
        "google_calendar": gcal_result
    }
    overall = all(v["status"] == "healthy" for v in checks.values())
    status = "healthy" if overall else "degraded"
    
    # Record health check metrics
    record_health_check(status, duration)
    
    return {
        "status": status,
        "checks": checks,
        "version": settings.app_version,
        "response_time_ms": round(duration * 1000, 2)
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
