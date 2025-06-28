"""
Metrics and Monitoring Module

This module provides Prometheus metrics for the Family Dashboard API,
including custom metrics for calendar events, weather data, grocery items,
and system performance.

Features:
- Custom business metrics for dashboard functionality
- Performance monitoring for external API calls
- Database operation metrics
- Error tracking and alerting
- Health check metrics
"""

import logging
import os
import time
from typing import Any, Dict, Optional

from prometheus_client import (CONTENT_TYPE_LATEST, CollectorRegistry, Counter,
                               Gauge, Histogram, Summary, generate_latest,
                               multiprocess)
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_fastapi_instrumentator.metrics import Info

from .config import settings

logger = logging.getLogger(__name__)

# Set PROMETHEUS_MULTIPROC_DIR environment variable for multiprocess support
os.environ.setdefault('PROMETHEUS_MULTIPROC_DIR', str(settings.prometheus_multiproc_dir))

# Create a custom registry for multiprocess support
registry = CollectorRegistry()
multiprocess.MultiProcessCollector(registry)

# HTTP Request Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    registry=registry
)

# Business Logic Metrics
calendar_events_total = Counter(
    "calendar_events_total",
    "Total number of calendar events processed",
    ["operation", "status"],
    registry=registry
)

weather_requests_total = Counter(
    "weather_requests_total",
    "Total number of weather API requests",
    ["status", "location"],
    registry=registry
)

grocery_items_total = Counter(
    "grocery_items_total",
    "Total number of grocery items processed",
    ["operation", "status"],
    registry=registry
)

# External API Metrics
external_api_requests_total = Counter(
    "external_api_requests_total",
    "Total number of external API requests",
    ["api_name", "endpoint", "status"],
    registry=registry
)

external_api_duration_seconds = Histogram(
    "external_api_duration_seconds",
    "External API request duration in seconds",
    ["api_name", "endpoint"],
    registry=registry
)

# Database Metrics
database_operations_total = Counter(
    "database_operations_total",
    "Total number of database operations",
    ["operation", "table", "status"],
    registry=registry
)

database_operation_duration_seconds = Histogram(
    "database_operation_duration_seconds",
    "Database operation duration in seconds",
    ["operation", "table"],
    registry=registry
)

# System Health Metrics
active_connections = Gauge(
    "active_connections",
    "Number of active database connections",
    registry=registry
)

memory_usage_bytes = Gauge(
    "memory_usage_bytes",
    "Current memory usage in bytes",
    registry=registry
)

# Error Metrics
errors_total = Counter(
    "errors_total",
    "Total number of errors",
    ["error_type", "endpoint"],
    registry=registry
)

# Rate Limiting Metrics
rate_limit_hits_total = Counter(
    "rate_limit_hits_total",
    "Total number of rate limit hits",
    ["client_id"],
    registry=registry
)

# Custom Metrics Functions
def record_calendar_event(operation: str, status: str = "success") -> None:
    """Record a calendar event operation."""
    calendar_events_total.labels(operation=operation, status=status).inc()
    logger.debug(f"Recorded calendar event: {operation} - {status}")

def record_weather_request(status: str, location: str = "unknown") -> None:
    """Record a weather API request."""
    weather_requests_total.labels(status=status, location=location).inc()
    logger.debug(f"Recorded weather request: {status} - {location}")

def record_grocery_operation(operation: str, status: str = "success") -> None:
    """Record a grocery item operation."""
    grocery_items_total.labels(operation=operation, status=status).inc()
    logger.debug(f"Recorded grocery operation: {operation} - {status}")

def record_external_api_request(
    api_name: str, 
    endpoint: str, 
    status: str, 
    duration: float
) -> None:
    """Record an external API request."""
    external_api_requests_total.labels(
        api_name=api_name, 
        endpoint=endpoint, 
        status=status
    ).inc()
    external_api_duration_seconds.labels(
        api_name=api_name, 
        endpoint=endpoint
    ).observe(duration)
    logger.debug(f"Recorded external API request: {api_name}/{endpoint} - {status}")

def record_database_operation(
    operation: str, 
    table: str, 
    status: str, 
    duration: float
) -> None:
    """Record a database operation."""
    database_operations_total.labels(
        operation=operation, 
        table=table, 
        status=status
    ).inc()
    database_operation_duration_seconds.labels(
        operation=operation, 
        table=table
    ).observe(duration)
    logger.debug(f"Recorded database operation: {operation} on {table} - {status}")

def record_error(error_type: str, endpoint: str = "unknown") -> None:
    """Record an error occurrence."""
    errors_total.labels(error_type=error_type, endpoint=endpoint).inc()
    logger.debug(f"Recorded error: {error_type} - {endpoint}")

def record_rate_limit_hit(client_id: str) -> None:
    """Record a rate limit hit."""
    rate_limit_hits_total.labels(client_id=client_id).inc()
    logger.debug(f"Recorded rate limit hit for client: {client_id}")

def update_active_connections(count: int) -> None:
    """Update the active connections gauge."""
    active_connections.set(count)
    logger.debug(f"Updated active connections: {count}")

def update_memory_usage(bytes_used: int) -> None:
    """Update the memory usage gauge."""
    memory_usage_bytes.set(bytes_used)
    logger.debug(f"Updated memory usage: {bytes_used} bytes")

# Custom Instrumentator Metrics
def calendar_events_metric(info: Info) -> None:
    """Custom metric for calendar events."""
    if "calendar" in info.request.url.path:
        calendar_events_total.labels(
            operation=info.request.method,
            status=str(info.response.status_code)
        ).inc()

def weather_requests_metric(info: Info) -> None:
    """Custom metric for weather requests."""
    if "weather" in info.request.url.path:
        weather_requests_total.labels(
            status=str(info.response.status_code),
            location="api"
        ).inc()

def grocery_operations_metric(info: Info) -> None:
    """Custom metric for grocery operations."""
    if "grocery" in info.request.url.path:
        grocery_items_total.labels(
            operation=info.request.method,
            status=str(info.response.status_code)
        ).inc()

def error_tracking_metric(info: Info) -> None:
    """Custom metric for error tracking."""
    if info.response.status_code >= 400:
        errors_total.labels(
            error_type=f"http_{info.response.status_code}",
            endpoint=info.request.url.path
        ).inc()

# Metrics Instrumentator Setup
def setup_metrics_instrumentator() -> Instrumentator:
    """Setup and configure the FastAPI instrumentator with custom metrics."""
    instrumentator = Instrumentator(
        registry=registry,
        should_instrument=lambda request, response: True,
        should_gather=lambda request, response: True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health", "/docs", "/redoc", "/openapi.json"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )
    
    # Add custom metrics
    instrumentator.add(calendar_events_metric)
    instrumentator.add(weather_requests_metric)
    instrumentator.add(grocery_operations_metric)
    instrumentator.add(error_tracking_metric)
    
    return instrumentator

# Metrics Endpoint
def get_metrics() -> bytes:
    """Generate Prometheus metrics."""
    try:
        return generate_latest(registry)
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return b"# Error generating metrics\n"

# Health Check Metrics
def record_health_check(status: str, duration: float) -> None:
    """Record health check metrics."""
    http_requests_total.labels(
        method="GET", 
        endpoint="/health", 
        status=status
    ).inc()
    http_request_duration_seconds.labels(
        method="GET", 
        endpoint="/health"
    ).observe(duration)
    logger.debug(f"Recorded health check: {status} - {duration}s")

# Performance Monitoring Decorator
def monitor_performance(operation: str, category: str = "general"):
    """Decorator to monitor function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record success
                if category == "database":
                    record_database_operation(
                        operation=operation,
                        table="unknown",
                        status="success",
                        duration=duration
                    )
                elif category == "external_api":
                    record_external_api_request(
                        api_name=operation,
                        endpoint="unknown",
                        status="success",
                        duration=duration
                    )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error
                if category == "database":
                    record_database_operation(
                        operation=operation,
                        table="unknown",
                        status="error",
                        duration=duration
                    )
                elif category == "external_api":
                    record_external_api_request(
                        api_name=operation,
                        endpoint="unknown",
                        status="error",
                        duration=duration
                    )
                
                record_error(error_type=type(e).__name__, endpoint=operation)
                raise
        
        return wrapper
    return decorator

# Async version of the decorator
def monitor_performance_async(operation: str, category: str = "general"):
    """Async decorator to monitor function performance."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record success
                if category == "database":
                    record_database_operation(
                        operation=operation,
                        table="unknown",
                        status="success",
                        duration=duration
                    )
                elif category == "external_api":
                    record_external_api_request(
                        api_name=operation,
                        endpoint="unknown",
                        status="success",
                        duration=duration
                    )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error
                if category == "database":
                    record_database_operation(
                        operation=operation,
                        table="unknown",
                        status="error",
                        duration=duration
                    )
                elif category == "external_api":
                    record_external_api_request(
                        api_name=operation,
                        endpoint="unknown",
                        status="error",
                        duration=duration
                    )
                
                record_error(error_type=type(e).__name__, endpoint=operation)
                raise
        
        return wrapper
    return decorator 