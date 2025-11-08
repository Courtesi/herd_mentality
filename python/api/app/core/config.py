"""
Configuration settings for the FastAPI application.
Uses environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv


class Settings(BaseSettings):
    load_dotenv()

    # API Configuration
    API_V1_STR: str = os.getenv("API_V1_STR")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    INTERNAL_API_KEY: str = os.getenv("INTERNAL_API_KEY")

    # Environment Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # Default to development for safety

    # Redis Configuration (shared with Spring Boot)
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = os.getenv("REDIS_PORT")
    REDIS_DB: int = os.getenv("REDIS_DB")
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_KEY_PREFIX: str = os.getenv("REDIS_KEY_PREFIX")

    # Cache TTL settings (in seconds)
    CACHE_TTL_SHORT: int = os.getenv("CACHE_TTL_SHORT")
    CACHE_TTL_MEDIUM: int = os.getenv("CACHE_TTL_MEDIUM")
    CACHE_TTL_LONG: int = os.getenv("CACHE_TTL_LONG")

    # Database Configuration
    MYSQL_HOST: str = os.getenv("MYSQL_HOST")
    MYSQL_PORT: int = os.getenv("MYSQL_PORT")
    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE")

    SPRINGBOOT_URL: str = os.getenv("SPRINGBOOT_URL")

    PROCESS_EXPIRED_POLLS_MIN_INTERVAL: int = os.getenv("PROCESS_EXPIRED_POLLS_MIN_INTERVAL")
    CREATE_POLL_HOUR_INTERVAL: int = os.getenv("CREATE_POLL_HOUR_INTERVAL")

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    # Kalshi API Configuration
    KALSHI_API_KEY: str = os.getenv("KALSHI_API_KEY")
    KALSHI_RSA_KEY_PATH: str = os.getenv("KALSHI_RSA_KEY_PATH")
    KALSHI_BASE_URL: str = os.getenv("KALSHI_BASE_URL")


settings = Settings()