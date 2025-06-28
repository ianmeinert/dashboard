"""
Monitoring API Router

Provides endpoints for monitoring and observability:
- /health: System health checks
- /metrics: Application metrics
- /logs: Recent application logs
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..services.monitoring_service import LOG_FILE, health_checker, metrics

monitoring_router = APIRouter()

# Pydantic model for usage events
class UsageEvent(BaseModel):
    event_type: str
    details: Optional[Dict[str, Any]] = None

@monitoring_router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Get system health status.
    
    Returns:
        Dict containing health status of all system components
    """
    try:
        health_results = health_checker.run_all_checks()
        overall_health = all(health_results.values())
        
        return {
            "status": "healthy" if overall_health else "unhealthy",
            "timestamp": "2024-01-01T00:00:00Z",  # You can add proper timestamp
            "checks": health_results,
            "overall_healthy": overall_health
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

@monitoring_router.get("/metrics")
async def get_metrics(hours: int = 24) -> Dict[str, Any]:
    """Get application metrics for the last N hours.
    
    Args:
        hours: Number of hours to look back (default: 24)
        
    Returns:
        Dict containing metrics summary
    """
    try:
        metrics_summary = metrics.get_metrics_summary(hours)
        return {
            "period_hours": hours,
            "metrics": metrics_summary,
            "timestamp": "2024-01-01T00:00:00Z"  # You can add proper timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {e}")

@monitoring_router.get("/metrics/detailed")
async def get_detailed_metrics(hours: int = 24) -> Dict[str, Any]:
    """Get detailed metrics including recent API calls and errors.
    
    Args:
        hours: Number of hours to look back (default: 24)
        
    Returns:
        Dict containing detailed metrics
    """
    try:
        # Get basic metrics
        basic_metrics = metrics.get_metrics_summary(hours)
        
        # Get recent API calls
        with sqlite3.connect(metrics.db_path) as conn:
            recent_calls = conn.execute('''
                SELECT endpoint, method, response_time, status_code, timestamp
                FROM api_metrics 
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
                LIMIT 50
            '''.format(hours)).fetchall()
            
            recent_errors = conn.execute('''
                SELECT error_type, message, timestamp
                FROM errors 
                WHERE timestamp > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
                LIMIT 20
            '''.format(hours)).fetchall()
        
        return {
            "period_hours": hours,
            "summary": basic_metrics,
            "recent_api_calls": [
                {
                    "endpoint": call[0],
                    "method": call[1],
                    "response_time": call[2],
                    "status_code": call[3],
                    "timestamp": call[4]
                }
                for call in recent_calls
            ],
            "recent_errors": [
                {
                    "error_type": error[0],
                    "message": error[1],
                    "timestamp": error[2]
                }
                for error in recent_errors
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get detailed metrics: {e}")

@monitoring_router.get("/logs")
async def get_recent_logs(lines: int = 100) -> Dict[str, Any]:
    """Get recent application logs.
    
    Args:
        lines: Number of log lines to return (default: 100)
        
    Returns:
        Dict containing recent log entries
    """
    try:
        try:
            with open(LOG_FILE, 'r') as f:
                log_lines = f.readlines()
                recent_logs = log_lines[-lines:] if len(log_lines) > lines else log_lines
        except FileNotFoundError:
            recent_logs = ["No log file found"]
        
        return {
            "log_file": str(LOG_FILE),
            "total_lines": len(recent_logs),
            "logs": recent_logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {e}")

@monitoring_router.post("/usage")
async def record_usage_event(request: Request, usage_event: UsageEvent) -> Dict[str, str]:
    """Record a usage event.
    
    Args:
        request: FastAPI request object
        usage_event: Usage event data
        
    Returns:
        Confirmation message
    """
    try:
        user_agent = request.headers.get("user-agent")
        client_ip = request.client.host if request.client else None
        
        metrics.record_usage_event(usage_event.event_type, user_agent, client_ip, usage_event.details)
        
        return {"message": "Usage event recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record usage event: {e}")

@monitoring_router.get("/status")
async def system_status() -> Dict[str, Any]:
    """Get overall system status including health, metrics, and recent activity.
    
    Returns:
        Dict containing comprehensive system status
    """
    try:
        # Get health status
        health_results = health_checker.run_all_checks()
        overall_health = all(health_results.values())
        
        # Get recent metrics
        recent_metrics = metrics.get_metrics_summary(1)  # Last hour
        
        # Get recent errors
        with sqlite3.connect(metrics.db_path) as conn:
            recent_error_count = conn.execute('''
                SELECT COUNT(*) FROM errors 
                WHERE timestamp > datetime('now', '-1 hour')
            ''').fetchone()[0]
        
        return {
            "status": "operational" if overall_health else "degraded",
            "health": {
                "overall": overall_health,
                "checks": health_results
            },
            "performance": {
                "api_calls_last_hour": recent_metrics.get('total_api_calls', 0),
                "avg_response_time": recent_metrics.get('avg_response_time', 0),
                "errors_last_hour": recent_error_count
            },
            "timestamp": "2024-01-01T00:00:00Z"  # You can add proper timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {e}") 