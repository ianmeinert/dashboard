"""
Weather API Router

Provides endpoints for current weather, 5-day forecast, and air quality.
"""
from datetime import datetime
from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models import AsyncSessionLocal, WeatherSettings
from ..schemas.weather import WeatherSettingsCreate, WeatherSettingsResponse
from ..utils.weather import get_current_weather, get_forecast, get_lat_lon

weather_router = APIRouter()

# Dependency for DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@weather_router.get("/current", response_model=Dict[str, Any])
async def current_weather(
    lat: float = Query(None),
    lon: float = Query(None),
    city: str = Query(None),
    state: str = Query(None),
    zip_code: str = Query(None),
    country: str = Query("US")
):
    """Get current weather for a given location (city/state or zip)."""
    try:
        if lat is not None and lon is not None:
            resolved_lat, resolved_lon = lat, lon
        elif city and state:
            resolved_lat, resolved_lon = await get_lat_lon(city=city, state=state)
        elif zip_code:
            resolved_lat, resolved_lon = await get_lat_lon(zip_code=zip_code)
        else:
            raise HTTPException(status_code=400, detail="Must provide lat/lon or city or zip_code")
        return await get_current_weather(lat=resolved_lat, lon=resolved_lon)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch current weather: {exc}")

@weather_router.get("/forecast", response_model=Dict[str, Any])
async def forecast(
    lat: float = Query(None),
    lon: float = Query(None),
    city: str = Query(None),
    state: str = Query(None),
    zip_code: str = Query(None),
    country: str = Query("US")
):
    """Get 5-day weather forecast for a given location (lat/lon, city/state, or zip)."""
    try:
        resolved_lat, resolved_lon = await get_lat_lon(lat=lat, lon=lon, city=city, state=state, zip_code=zip_code, country=country)
        return await get_forecast(lat=resolved_lat, lon=resolved_lon)
    except Exception as e:
        print(f"Internal error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Get current preferred weather location
@weather_router.get("/settings", response_model=WeatherSettingsResponse)
async def get_weather_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WeatherSettings).where(WeatherSettings.id == 1))
    settings = result.scalar_one_or_none()
    if not settings:
        # Return empty/default if not set
        return WeatherSettingsResponse(
            city=None, state=None, zip_code=None, lat=None, lon=None, last_updated=datetime.utcnow()
        )
    return WeatherSettingsResponse.model_validate(settings)

# Set preferred weather location
@weather_router.post("/settings", response_model=WeatherSettingsResponse)
async def set_weather_settings(
    settings: WeatherSettingsCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(WeatherSettings).where(WeatherSettings.id == 1))
    existing = result.scalar_one_or_none()
    now = datetime.utcnow()
    if existing:
        for field, value in settings.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)
        existing.last_updated = now
        await db.commit()
        await db.refresh(existing)
        return WeatherSettingsResponse.model_validate(existing)
    else:
        new_settings = WeatherSettings(
            id=1,
            last_updated=now,
            **settings.model_dump(exclude_unset=True)
        )
        db.add(new_settings)
        await db.commit()
        await db.refresh(new_settings)
        return WeatherSettingsResponse.model_validate(new_settings)

