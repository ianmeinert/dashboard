"""
Weather API Router

Provides endpoints for current weather, 5-day forecast, and weather settings
with enhanced security, input validation, and error handling.
"""
import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..database import get_db
from ..exceptions import (DatabaseException, ExternalAPIException,
                          ValidationException)
from ..http_client import weather_client
from ..models import WeatherSettings
from ..schemas.weather import WeatherSettingsCreate, WeatherSettingsResponse
from ..security import validate_coordinates, validate_location_input

logger = logging.getLogger(__name__)
weather_router = APIRouter()

@weather_router.get("/current", response_model=Dict[str, Any])
async def current_weather(
    request: Request,
    lat: float = Query(None, description="Latitude (-90 to 90)"),
    lon: float = Query(None, description="Longitude (-180 to 180)"),
    city: str = Query(None, description="City name"),
    state: str = Query(None, description="State/province"),
    zip_code: str = Query(None, description="ZIP/postal code"),
    country: str = Query("US", description="Country code")
):
    """Get current weather for a given location with input validation."""
    try:
        # Validate input parameters
        if lat is not None and lon is not None:
            # Validate coordinates
            resolved_lat, resolved_lon = validate_coordinates(lat, lon)
        elif city and state:
            # Validate location input
            validate_location_input(city=city, state=state)
            resolved_lat, resolved_lon = await weather_client.geocode_city(
                city=city, state=state, country=country
            )
        elif zip_code:
            # Validate ZIP code
            validate_location_input(zip_code=zip_code)
            resolved_lat, resolved_lon = await weather_client.geocode_zip(
                zip_code=zip_code, country=country
            )
        else:
            raise ValidationException(
                "Must provide lat/lon, city/state, or zip_code",
                details={"required": "One of: coordinates, city+state, or zip_code"}
            )
        
        return await weather_client.get_current_weather(
            lat=resolved_lat, lon=resolved_lon
        )
    except ValidationException:
        raise
    except ValueError as e:
        raise ValidationException(str(e))
    except Exception as e:
        logger.error(f"Weather API error: {e}", exc_info=True)
        raise ExternalAPIException("OpenWeatherMap", "Failed to fetch current weather data")

@weather_router.get("/forecast", response_model=Dict[str, Any])
async def forecast(
    request: Request,
    lat: float = Query(None, description="Latitude (-90 to 90)"),
    lon: float = Query(None, description="Longitude (-180 to 180)"),
    city: str = Query(None, description="City name"),
    state: str = Query(None, description="State/province"),
    zip_code: str = Query(None, description="ZIP/postal code"),
    country: str = Query("US", description="Country code")
):
    """Get 5-day weather forecast for a given location with input validation."""
    try:
        # Validate input parameters
        if lat is not None and lon is not None:
            # Validate coordinates
            resolved_lat, resolved_lon = validate_coordinates(lat, lon)
        elif city and state:
            # Validate location input
            validate_location_input(city=city, state=state)
            resolved_lat, resolved_lon = await weather_client.geocode_city(
                city=city, state=state, country=country
            )
        elif zip_code:
            # Validate ZIP code
            validate_location_input(zip_code=zip_code)
            resolved_lat, resolved_lon = await weather_client.geocode_zip(
                zip_code=zip_code, country=country
            )
        else:
            raise ValidationException(
                "Must provide lat/lon, city/state, or zip_code",
                details={"required": "One of: coordinates, city+state, or zip_code"}
            )
        
        return await weather_client.get_forecast(
            lat=resolved_lat, lon=resolved_lon
        )
    except ValidationException:
        raise
    except ValueError as e:
        raise ValidationException(str(e))
    except Exception as e:
        logger.error(f"Weather forecast error: {e}", exc_info=True)
        raise ExternalAPIException("OpenWeatherMap", "Failed to fetch forecast data")

@weather_router.get("/settings", response_model=WeatherSettingsResponse)
async def get_weather_settings(db: AsyncSession = Depends(get_db)):
    """Get current preferred weather location."""
    try:
        result = await db.execute(
            select(WeatherSettings).where(WeatherSettings.id == 1)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            # Return empty/default if not set
            return WeatherSettingsResponse(
                city=None, 
                state=None, 
                zip_code=None, 
                lat=None, 
                lon=None, 
                last_updated=datetime.utcnow()
            )
        
        return WeatherSettingsResponse.model_validate(settings)
    except Exception as e:
        logger.error(f"Error getting weather settings: {e}", exc_info=True)
        raise DatabaseException("Failed to retrieve weather settings", operation="select")

@weather_router.post("/settings", response_model=WeatherSettingsResponse)
async def set_weather_settings(
    settings: WeatherSettingsCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Set preferred weather location with validation."""
    try:
        # Validate input data
        if settings.city:
            validate_location_input(city=settings.city)
        if settings.state:
            validate_location_input(state=settings.state)
        if settings.zip_code:
            validate_location_input(zip_code=settings.zip_code)
        if settings.lat is not None and settings.lon is not None:
            validate_coordinates(settings.lat, settings.lon)
        
        result = await db.execute(
            select(WeatherSettings).where(WeatherSettings.id == 1)
        )
        existing = result.scalar_one_or_none()
        now = datetime.utcnow()
        
        if existing:
            # Update existing settings
            update_data = settings.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing, field, value)
            existing.last_updated = now
            await db.commit()
            await db.refresh(existing)
            return WeatherSettingsResponse.model_validate(existing)
        else:
            # Create new settings
            new_settings = WeatherSettings(
                id=1,
                last_updated=now,
                **settings.model_dump(exclude_unset=True)
            )
            db.add(new_settings)
            await db.commit()
            await db.refresh(new_settings)
            return WeatherSettingsResponse.model_validate(new_settings)
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error setting weather settings: {e}", exc_info=True)
        raise DatabaseException("Failed to update weather settings", operation="upsert")

