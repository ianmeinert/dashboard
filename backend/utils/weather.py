"""
Weather/AQI Utility Functions

Fetches current weather, AQI, and 5-day forecast from OpenWeatherMap.
"""
import json
import os
from typing import Any, Dict

import aiohttp

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CREDENTIALS_FILE = os.path.join(DATA_DIR, "credentials.json")

with open(CREDENTIALS_FILE, encoding="utf-8") as f:
    creds = json.load(f)
API_KEY = creds["openweathermap_api_key"]

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
GEOCODE_ZIP_URL = "https://api.openweathermap.org/geo/1.0/zip"

async def get_current_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch current weather for given coordinates using /data/2.5/weather."""
    async with aiohttp.ClientSession() as session:
        url = f"{WEATHER_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=imperial"
        async with session.get(url) as resp:
            data = await resp.json()
        return {"weather": data}

async def get_forecast(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch 5-day/3-hour forecast for given coordinates using /data/2.5/forecast."""
    async with aiohttp.ClientSession() as session:
        url = f"{FORECAST_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=imperial"
        async with session.get(url) as resp:
            data = await resp.json()
        return {"forecast": data}

async def get_lat_lon(lat: float = None, lon: float = None, city: str = None, state: str = None, zip_code: str = None, country: str = "US") -> (float, float):
    """Resolve lat/lon from direct input or by geocoding city/state/zip."""
    if lat is not None and lon is not None:
        return float(lat), float(lon)
    async with aiohttp.ClientSession() as session:
        if zip_code:
            url = f"{GEOCODE_ZIP_URL}?zip={zip_code},{country}&appid={API_KEY}"
            async with session.get(url) as resp:
                data = await resp.json()
            return data["lat"], data["lon"]
        elif city:
            q = city
            if state:
                q += f",{state}"
            url = f"{GEOCODE_URL}?q={q},{country}&limit=1&appid={API_KEY}"
            async with session.get(url) as resp:
                data = await resp.json()
            if not data:
                raise ValueError("Location not found")
            return data[0]["lat"], data[0]["lon"]
        else:
            raise ValueError("Must provide lat/lon or city or zip_code") 