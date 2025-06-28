"""
Structured Logging Configuration

Provides comprehensive logging setup with structured output, file rotation,
and production-ready configuration for the Family Dashboard API.
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from .config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        # Add request context if available
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        
        if hasattr(record, "client_ip"):
            log_entry["client_ip"] = record.client_ip
        
        if hasattr(record, "user_agent"):
            log_entry["user_agent"] = record.user_agent
        
        if hasattr(record, "method"):
            log_entry["method"] = record.method
        
        if hasattr(record, "url"):
            log_entry["url"] = record.url
        
        # Add performance metrics if available
        if hasattr(record, "duration"):
            log_entry["duration_ms"] = record.duration
        
        if hasattr(record, "response_size"):
            log_entry["response_size_bytes"] = record.response_size
        
        return json.dumps(log_entry, ensure_ascii=False)


class HumanReadableFormatter(logging.Formatter):
    """Human-readable formatter for development."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record for human reading."""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        
        # Base format
        formatted = f"[{timestamp}] {record.levelname:8} | {record.name} | {record.getMessage()}"
        
        # Add location info
        if record.module != "__main__":
            formatted += f" | {record.module}.{record.funcName}:{record.lineno}"
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            formatted += f" | {record.extra_fields}"
        
        # Add request context if available
        if hasattr(record, "request_id"):
            formatted += f" | req:{record.request_id[:8]}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logging() -> None:
    """Setup comprehensive logging configuration."""
    # Create logs directory if it doesn't exist
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, str(settings.log_level).upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Choose formatter based on environment
    if settings.debug:
        formatter = HumanReadableFormatter()
    else:
        formatter = StructuredFormatter()
    
    # File handlers with rotation
    setup_file_handlers(root_logger, formatter)
    
    # Console handler (only in debug mode or if explicitly configured)
    if settings.debug or getattr(settings, "console_logging", False):
        setup_console_handler(root_logger, formatter)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized", extra={
        "extra_fields": {
            "log_level": settings.log_level,
            "debug_mode": settings.debug,
            "log_directory": str(settings.logs_dir)
        }
    })


def setup_file_handlers(root_logger: logging.Logger, formatter: logging.Formatter) -> None:
    """Setup file handlers with rotation."""
    # Main application log
    app_handler = logging.handlers.RotatingFileHandler(
        settings.logs_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)
    root_logger.addHandler(app_handler)
    
    # Error log (errors and above)
    error_handler = logging.handlers.RotatingFileHandler(
        settings.logs_dir / "errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # Security log (for auth, rate limiting, etc.)
    security_handler = logging.handlers.RotatingFileHandler(
        settings.logs_dir / "security.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8"
    )
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(formatter)
    
    # Create security logger
    security_logger = logging.getLogger("security")
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False  # Don't propagate to root logger
    
    # Performance log (for timing, metrics, etc.)
    perf_handler = logging.handlers.RotatingFileHandler(
        settings.logs_dir / "performance.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8"
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.setFormatter(formatter)
    
    # Create performance logger
    perf_logger = logging.getLogger("performance")
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)
    perf_logger.propagate = False  # Don't propagate to root logger


def setup_console_handler(root_logger: logging.Logger, formatter: logging.Formatter) -> None:
    """Setup console handler for development."""
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def log_request(
    logger: logging.Logger,
    request: Any,
    response: Any = None,
    duration: Optional[float] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> None:
    """Log HTTP request with structured data."""
    log_data = {
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "request_id": getattr(request.state, "request_id", None),
    }
    
    if response:
        log_data.update({
            "status_code": response.status_code,
            "response_size_bytes": len(response.body) if hasattr(response, 'body') else 0,
        })
    
    if duration:
        log_data["duration_ms"] = round(duration * 1000, 2)
    
    if extra_fields:
        log_data.update(extra_fields)
    
    logger.info("HTTP request processed", extra={"extra_fields": log_data})


def log_security_event(
    event_type: str,
    message: str,
    client_ip: str,
    user_agent: str = "unknown",
    request_id: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> None:
    """Log security-related events."""
    logger = logging.getLogger("security")
    
    log_data = {
        "event_type": event_type,
        "client_ip": client_ip,
        "user_agent": user_agent,
        "request_id": request_id,
    }
    
    if extra_fields:
        log_data.update(extra_fields)
    
    logger.warning(f"Security event: {message}", extra={"extra_fields": log_data})


def log_performance_metric(
    metric_name: str,
    value: float,
    unit: str = "ms",
    tags: Optional[Dict[str, str]] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> None:
    """Log performance metrics."""
    logger = logging.getLogger("performance")
    
    log_data = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
    }
    
    if tags:
        log_data["tags"] = tags
    
    if extra_fields:
        log_data.update(extra_fields)
    
    logger.info("Performance metric", extra={"extra_fields": log_data})


def log_database_operation(
    operation: str,
    table: str,
    duration: float,
    success: bool,
    error: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> None:
    """Log database operations."""
    logger = logging.getLogger("performance")
    
    log_data = {
        "operation": operation,
        "table": table,
        "duration_ms": round(duration * 1000, 2),
        "success": success,
    }
    
    if error:
        log_data["error"] = error
    
    if extra_fields:
        log_data.update(extra_fields)
    
    level = logging.ERROR if not success else logging.INFO
    logger.log(level, "Database operation", extra={"extra_fields": log_data})


def log_external_api_call(
    service: str,
    endpoint: str,
    method: str,
    duration: float,
    status_code: Optional[int] = None,
    success: bool = True,
    error: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> None:
    """Log external API calls."""
    logger = logging.getLogger("performance")
    
    log_data = {
        "service": service,
        "endpoint": endpoint,
        "method": method,
        "duration_ms": round(duration * 1000, 2),
        "success": success,
    }
    
    if status_code:
        log_data["status_code"] = status_code
    
    if error:
        log_data["error"] = error
    
    if extra_fields:
        log_data.update(extra_fields)
    
    level = logging.ERROR if not success else logging.INFO
    logger.log(level, "External API call", extra={"extra_fields": log_data}) 