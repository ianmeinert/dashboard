"""
Weather API Router

Provides endpoints for current weather, 5-day forecast, and air quality.
"""
from typing import Any, Dict

import httpx
from fastapi import APIRouter, HTTPException, Query

from ..utils.weather import get_current_weather, get_forecast, get_lat_lon

weather_router = APIRouter()

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

