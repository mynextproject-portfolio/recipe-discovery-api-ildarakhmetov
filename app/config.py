"""Application configuration."""

import os
from typing import List


class Settings:
    """Application settings loaded from environment variables."""
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    
    # API Configuration
    API_TITLE: str = os.getenv("API_TITLE", "Recipe Discovery API")
    API_DESCRIPTION: str = os.getenv(
        "API_DESCRIPTION", 
        "A simple FastAPI service for recipe discovery"
    )
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


# Global settings instance
settings = Settings()
