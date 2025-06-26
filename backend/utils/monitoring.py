"""
Monitoring and Observability Utilities

Provides comprehensive monitoring for the dashboard application including:
- Performance tracking
- Error logging
- Health checks
- Usage analytics
- Structured logging
"""

import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# Ensure logs directory exists
LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / 'app.log'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and stores application metrics."""
    
    def __init__(self, db_path: str = 'data/metrics.db'):
        self.db_path = db_path
        self._ensure_db()
    
    def _ensure_db(self):
        """Ensure metrics database exists with proper schema."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS api_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    response_time REAL NOT NULL,
                    status_code INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    stack_trace TEXT,
                    context TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS usage_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    user_agent TEXT,
                    ip_address TEXT,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    check_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_time REAL,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def record_api_call(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Record API call metrics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO api_metrics (endpoint, method, response_time, status_code) VALUES (?, ?, ?, ?)',
                    (endpoint, method, response_time, status_code)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record API call: {e}")
    
    def record_error(self, error_type: str, message: str, stack_trace: Optional[str] = None, context: Optional[Dict] = None):
        """Record application errors."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO errors (error_type, message, stack_trace, context) VALUES (?, ?, ?, ?)',
                    (error_type, message, stack_trace, json.dumps(context) if context else None)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record error: {e}")
    
    def record_usage_event(self, event_type: str, user_agent: Optional[str] = None, ip_address: Optional[str] = None, details: Optional[Dict] = None):
        """Record usage events."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO usage_events (event_type, user_agent, ip_address, details) VALUES (?, ?, ?, ?)',
                    (event_type, user_agent, ip_address, json.dumps(details) if details else None)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record usage event: {e}")
    
    def record_health_check(self, check_name: str, status: str, response_time: Optional[float] = None, details: Optional[Dict] = None):
        """Record health check results."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO health_checks (check_name, status, response_time, details) VALUES (?, ?, ?, ?)',
                    (check_name, status, response_time, json.dumps(details) if details else None)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record health check: {e}")
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # API metrics
                api_metrics = conn.execute('''
                    SELECT 
                        COUNT(*) as total_calls,
                        AVG(response_time) as avg_response_time,
                        COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count
                    FROM api_metrics 
                    WHERE timestamp > datetime('now', '-{} hours')
                '''.format(hours)).fetchone()
                
                # Error count
                error_count = conn.execute('''
                    SELECT COUNT(*) FROM errors 
                    WHERE timestamp > datetime('now', '-{} hours')
                '''.format(hours)).fetchone()[0]
                
                # Usage events
                usage_count = conn.execute('''
                    SELECT COUNT(*) FROM usage_events 
                    WHERE timestamp > datetime('now', '-{} hours')
                '''.format(hours)).fetchone()[0]
                
                return {
                    'total_api_calls': api_metrics[0] or 0,
                    'avg_response_time': api_metrics[1] or 0,
                    'api_errors': api_metrics[2] or 0,
                    'total_errors': error_count,
                    'usage_events': usage_count,
                    'period_hours': hours
                }
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}

# Global metrics collector instance
metrics = MetricsCollector()

def monitor_performance(endpoint: str):
    """Decorator to monitor API endpoint performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                response_time = time.time() - start_time
                metrics.record_api_call(endpoint, 'GET', response_time, 200)
                return result
            except Exception as e:
                response_time = time.time() - start_time
                metrics.record_api_call(endpoint, 'GET', response_time, 500)
                metrics.record_error('API_ERROR', str(e), context={'endpoint': endpoint})
                raise
        return wrapper
    return decorator

def log_error(error_type: str, context: Optional[Dict] = None):
    """Log an error with context."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                import traceback
                stack_trace = traceback.format_exc()
                metrics.record_error(error_type, str(e), stack_trace, context)
                logger.error(f"{error_type}: {e}", exc_info=True)
                raise
        return wrapper
    return decorator

class HealthChecker:
    """Performs health checks on various system components."""
    
    @staticmethod
    def check_database():
        """Check database connectivity."""
        start_time = time.time()
        try:
            from .sync_token_db import DB_PATH
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('SELECT 1')
            response_time = time.time() - start_time
            metrics.record_health_check('database', 'healthy', response_time)
            return True
        except Exception as e:
            response_time = time.time() - start_time
            metrics.record_health_check('database', 'unhealthy', response_time, {'error': str(e)})
            return False
    
    @staticmethod
    def check_google_calendar():
        """Check Google Calendar API connectivity."""
        start_time = time.time()
        try:
            from .google_calendar import get_upcoming_events

            # Try to fetch a small amount of data
            events = get_upcoming_events()
            response_time = time.time() - start_time
            metrics.record_health_check('google_calendar', 'healthy', response_time)
            return True
        except Exception as e:
            response_time = time.time() - start_time
            metrics.record_health_check('google_calendar', 'unhealthy', response_time, {'error': str(e)})
            return False
    
    @staticmethod
    def run_all_checks() -> Dict[str, bool]:
        """Run all health checks."""
        return {
            'database': HealthChecker.check_database(),
            'google_calendar': HealthChecker.check_google_calendar()
        }

# Global health checker instance
health_checker = HealthChecker() 