"""
Weather Schemas

Pydantic models for weather settings and queries.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WeatherSettingsBase(BaseModel):
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    lat: Optional[str] = Field(None, max_length=32)
    lon: Optional[str] = Field(None, max_length=32)

class WeatherSettingsCreate(WeatherSettingsBase):
    pass

class WeatherSettingsResponse(WeatherSettingsBase):
    last_updated: datetime

    class Config:
        from_attributes = True 