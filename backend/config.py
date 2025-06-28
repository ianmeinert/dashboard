"""
Configuration Management

Centralized configuration using Pydantic Settings for environment variables,
with secure defaults and validation.
"""

import os
import secrets
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Family Dashboard API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    console_logging: bool = Field(default=False, env="CONSOLE_LOGGING")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Security
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        env="SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    allowed_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        env="ALLOWED_ORIGINS"
    )
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/dashboard.db",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    
    # API Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # External APIs
    openweathermap_api_key: Optional[str] = Field(default=None, env="OPENWEATHERMAP_API_KEY")
    openweathermap_base_url: str = Field(
        default="https://api.openweathermap.org",
        env="OPENWEATHERMAP_BASE_URL"
    )
    openweathermap_timeout: int = Field(default=10, env="OPENWEATHERMAP_TIMEOUT")
    
    # Google Calendar
    google_calendar_id: str = Field(default="primary", env="GOOGLE_CALENDAR_ID")
    google_credentials_file: str = Field(
        default="./data/credentials.json",
        env="GOOGLE_CREDENTIALS_FILE"
    )
    google_token_file: str = Field(
        default="./data/token.json",
        env="GOOGLE_TOKEN_FILE"
    )
    
    # File Paths
    data_dir: Path = Field(default=Path("./data"), env="DATA_DIR")
    logs_dir: Path = Field(default=Path("./logs"), env="LOGS_DIR")
    
    # Monitoring
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_db_path: str = Field(
        default="./data/metrics.db",
        env="METRICS_DB_PATH"
    )
    prometheus_multiproc_dir: str = Field(
        default="./tmp/prometheus_multiproc",
        env="PROMETHEUS_MULTIPROC_DIR"
    )
    
    # Cache
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    cache_ttl: int = Field(default=300, env="CACHE_TTL")  # seconds
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins string."""
        if isinstance(v, str):
            return v
        return "http://localhost:5173,http://127.0.0.1:5173"
    
    @field_validator("data_dir", "logs_dir", "prometheus_multiproc_dir", mode="before")
    @classmethod
    def create_directories(cls, v):
        """Ensure directories exist."""
        if isinstance(v, str):
            path = Path(v)
        else:
            path = v
        path.mkdir(parents=True, exist_ok=True)
        return str(path)  # Always return a string!
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        """Ensure secret key is secure in production."""
        if not os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"):
            if v == secrets.token_urlsafe(32):  # Default value
                raise ValueError(
                    "SECRET_KEY must be set in production environment. "
                    "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )
        return v
    
    @field_validator("openweathermap_api_key")
    @classmethod
    def validate_weather_api_key(cls, v):
        """Warn if weather API key is missing."""
        if not v:
            print("⚠️  WARNING: OPENWEATHERMAP_API_KEY not set. Weather features will be disabled.")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
