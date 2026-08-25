"""
Application configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # QuickCommerce API
    QUICKCOMMERCE_API_KEY: str
    QUICKCOMMERCE_BASE_URL: str = "https://api.quickcommerceapi.com"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/quickcompare"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 60

    # Application
    ENVIRONMENT: str = "development"
    APP_NAME: str = "QuickCommerce Comparison API"

    # Default location (Chennai)
    DEFAULT_LATITUDE: float = 13.0827
    DEFAULT_LONGITUDE: float = 80.2707

    # Default platforms
    DEFAULT_PLATFORMS: str = "BlinkIt,Zepto,Swiggy"

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
