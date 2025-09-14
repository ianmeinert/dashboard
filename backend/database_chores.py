"""
Family Chores Database Configuration and Session Management

Provides async database setup with connection pooling, proper session management,
and error handling for the family chores system using a separate SQLite database.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.pool import NullPool, QueuePool

from .core.config import settings
from .models.chores import Base as ChoresBase

# Family chores database URL
CHORES_DATABASE_URL = "sqlite+aiosqlite:///./data/family_chores.db"

# Database engine with connection pooling
chores_engine: AsyncEngine = create_async_engine(
    CHORES_DATABASE_URL,
    echo=settings.debug,
    future=True,
)

# Session factory with proper configuration
ChoresAsyncSessionLocal = async_sessionmaker(
    bind=chores_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@asynccontextmanager
async def get_chores_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a family chores database session with proper error handling and cleanup.
    
    Yields:
        AsyncSession: Database session for family chores
        
    Raises:
        Exception: Database connection errors
    """
    session = ChoresAsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_chores_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for family chores database sessions.
    
    Yields:
        AsyncSession: Database session for family chores
    """
    async with get_chores_db_session() as session:
        yield session


async def init_chores_db() -> None:
    """Initialize family chores database tables."""
    async with chores_engine.begin() as conn:
        await conn.run_sync(ChoresBase.metadata.create_all)


async def close_chores_db() -> None:
    """Close family chores database connections."""
    await chores_engine.dispose()


# Database event listeners for better monitoring
@event.listens_for(chores_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configure SQLite for better performance and reliability."""
    if "sqlite" in CHORES_DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()


# Health check for family chores database connectivity
async def check_chores_db_health() -> bool:
    """Check if family chores database is accessible."""
    try:
        async with get_chores_db_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception:
        return False


# Database metrics for family chores
class ChoresDatabaseMetrics:
    """Track family chores database performance metrics."""
    
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
            "pool_size": chores_engine.pool.size(),
            "checked_in": chores_engine.pool.checkedin(),
            "checked_out": chores_engine.pool.checkedout(),
            "overflow": chores_engine.pool.overflow(),
        }


# Global metrics instance for family chores
chores_db_metrics = ChoresDatabaseMetrics()
