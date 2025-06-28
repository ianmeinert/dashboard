"""
HTTP Client Management

Provides a centralized HTTP client with connection pooling, timeout handling,
and proper resource management to prevent memory leaks.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Optional

import aiohttp
from aiohttp import ClientSession, ClientTimeout
from aiohttp.connector import TCPConnector

from .config import settings


class HTTPClientManager:
    """Manages HTTP client sessions with connection pooling."""
    
    def __init__(self):
        self._session: Optional[ClientSession] = None
        self._lock = asyncio.Lock()
    
    async def get_session(self) -> ClientSession:
        """Get or create HTTP client session."""
        if self._session is None or self._session.closed:
            async with self._lock:
                if self._session is None or self._session.closed:
                    await self._create_session()
        return self._session
    
    async def _create_session(self):
        """Create a new HTTP client session with proper configuration."""
        timeout = ClientTimeout(total=settings.openweathermap_timeout)
        connector = TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=30,  # Connections per host
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )
        
        self._session = ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                "User-Agent": f"{settings.app_name}/{settings.app_version}",
                "Accept": "application/json",
            }
        )
    
    async def close(self):
        """Close the HTTP client session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[ClientSession, None]:
        """Context manager for HTTP client session."""
        session = await self.get_session()
        try:
            yield session
        except Exception:
            # If session is broken, recreate it
            if session.closed:
                await self._create_session()
            raise


# Global HTTP client manager
http_client = HTTPClientManager()


async def make_request(
    method: str,
    url: str,
    **kwargs
) -> Dict:
    """
    Make HTTP request with proper error handling and timeout.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        **kwargs: Additional request parameters
        
    Returns:
        Dict: Response data
        
    Raises:
        HTTPException: If request fails
    """
    try:
        async with http_client.session() as session:
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500,
            detail=f"HTTP request failed: {str(e)}"
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Request timeout"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


async def get_json(url: str, **kwargs) -> Dict:
    """Make GET request and return JSON response."""
    return await make_request("GET", url, **kwargs)


async def post_json(url: str, data: Dict, **kwargs) -> Dict:
    """Make POST request with JSON data."""
    kwargs.setdefault("json", data)
    return await make_request("POST", url, **kwargs)


# Weather API specific client
class WeatherAPIClient:
    """Client for OpenWeatherMap API with caching and error handling."""
    
    def __init__(self):
        self.base_url = settings.openweathermap_base_url
        self.api_key = settings.openweathermap_api_key
        self.timeout = settings.openweathermap_timeout
    
    async def get_current_weather(self, lat: float, lon: float) -> Dict:
        """Get current weather data."""
        url = f"{self.base_url}/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "imperial"
        }
        
        data = await get_json(url, params=params)
        return {"weather": data}
    
    async def get_forecast(self, lat: float, lon: float) -> Dict:
        """Get 5-day weather forecast."""
        url = f"{self.base_url}/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "imperial"
        }
        
        data = await get_json(url, params=params)
        return {"forecast": data}
    
    async def geocode_city(self, city: str, state: str, country: str = "US") -> tuple[float, float]:
        """Geocode city name to coordinates."""
        url = f"{self.base_url}/geo/1.0/direct"
        params = {
            "q": f"{city},{state},{country}",
            "limit": 1,
            "appid": self.api_key
        }
        
        data = await get_json(url, params=params)
        if not data:
            raise ValueError("Location not found")
        
        return data[0]["lat"], data[0]["lon"]
    
    async def geocode_zip(self, zip_code: str, country: str = "US") -> tuple[float, float]:
        """Geocode ZIP code to coordinates."""
        url = f"{self.base_url}/geo/1.0/zip"
        params = {
            "zip": f"{zip_code},{country}",
            "appid": self.api_key
        }
        
        data = await get_json(url, params=params)
        return data["lat"], data["lon"]


# Global weather API client
weather_client = WeatherAPIClient() 