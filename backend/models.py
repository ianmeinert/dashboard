"""
SQLAlchemy ORM Models and Async DB Setup

Defines the async session and engine for the project.

Note: Model classes are now in models/grocery.py, models/weather.py, etc.
"""

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from .models.base import Base

DATABASE_URL = "sqlite+aiosqlite:///./data/dashboard.db"

# Async engine and session setup
engine = create_async_engine(
    DATABASE_URL, echo=False, future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    """Create all tables (run at startup if needed)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 