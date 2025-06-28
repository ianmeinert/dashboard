"""
WeatherSettings SQLAlchemy ORM model

Defines the WeatherSettings table for storing weather widget settings.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from .base import Base


class WeatherSettings(Base):
    __tablename__ = "weather_settings"
    id = Column(Integer, primary_key=True, index=True, default=1)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    lat = Column(String(32), nullable=True)
    lon = Column(String(32), nullable=True)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow) 