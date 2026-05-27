import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Gateway Hub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost/gateway_hub",
    )

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


    # CORS
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    ).split(",")
    CORS_ALLOW_METHODS: list[str] = os.getenv(
        "CORS_ALLOW_METHODS",
        "GET,POST,PUT,PATCH,DELETE,OPTIONS",
    ).split(",")
    CORS_ALLOW_HEADERS: list[str] = os.getenv(
        "CORS_ALLOW_HEADERS",
        "Authorization,Content-Type",
    ).split(",")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # Short URL Settings
    SHORT_CODE_LENGTH: int = 6
    SHORT_CODE_ALPHABET: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    # Free Tier Limits
    FREE_TIER_LINKS_PER_MONTH: int = 5
    FREE_TIER_CLICKS_PER_LINK: int = 100

    # Premium Tier Limits
    PREMIUM_TIER_LINKS_PER_MONTH: int = 10000
    PREMIUM_TIER_CLICKS_PER_LINK: int = 1000000

    # Redis (optional)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    REDIS_ENABLED: bool = REDIS_URL is not None

    # Email (optional)
    SMTP_SERVER: Optional[str] = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SENDER_EMAIL: Optional[str] = os.getenv("SENDER_EMAIL", "noreply@gatewayhub.com")
    EMAIL_ENABLED: bool = SMTP_SERVER is not None

    class Config:
        env_file = ".env"


settings = Settings()
