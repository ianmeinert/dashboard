"""
SQLAlchemy ORM Models and Async DB Setup

Defines the database models and async session for the project.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./data/dashboard.db"

Base = declarative_base()

class GroceryItem(Base):
    __tablename__ = "grocery_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    quantity = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    priority = Column(String(10), nullable=False, default="medium")
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class WeatherSettings(Base):
    __tablename__ = "weather_settings"
    id = Column(Integer, primary_key=True, index=True, default=1)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    lat = Column(String(32), nullable=True)
    lon = Column(String(32), nullable=True)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)

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