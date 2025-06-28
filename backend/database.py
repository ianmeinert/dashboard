"""
Database Configuration and Session Management

Provides async database setup with connection pooling, proper session management,
and error handling to prevent memory leaks and improve performance.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.pool import NullPool, QueuePool

from .core.config import settings
from .models.base import Base

# Database engine with connection pooling
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Session factory with proper configuration
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session with proper error handling and cleanup.
    
    Yields:
        AsyncSession: Database session
        
    Raises:
        Exception: Database connection errors
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    
    Yields:
        AsyncSession: Database session
    """
    async with get_db_session() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


# Database event listeners for better monitoring
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configure SQLite for better performance and reliability."""
    if "sqlite" in settings.database_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()


# Health check for database connectivity
async def check_db_health() -> bool:
    """Check if database is accessible."""
    try:
        async with get_db_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception:
        return False


# Database metrics
class DatabaseMetrics:
    """Track database performance metrics."""
    
    def __init__(self):
        self.connection_count = 0
        self.query_count = 0
        self.error_count = 0
    
    def record_connection(self):
        """Record a new database connection."""
        self.connection_count += 1
    
    def record_query(self):
        """Record a database query."""
        self.query_count += 1
    
    def record_error(self):
        """Record a database error."""
        self.error_count += 1
    
    def get_stats(self) -> dict:
        """Get current database statistics."""
        return {
            "connection_count": self.connection_count,
            "query_count": self.query_count,
            "error_count": self.error_count,
            "pool_size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
        }


# Global metrics instance
db_metrics = DatabaseMetrics() 