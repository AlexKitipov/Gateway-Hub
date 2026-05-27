from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/gateway_hub"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    APP_NAME: str = "Gateway Hub"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "https://app.example.com"]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    REDIS_URL: Optional[str] = "redis://localhost:6379"

    # Free Tier Limits
    FREE_TIER_LINKS_PER_MONTH: int = 5
    FREE_TIER_CLICKS_PER_LINK: int = 100

    # Premium Tier (unlimited or very high)
    PREMIUM_TIER_LINKS_PER_MONTH: int = 1000000
    PREMIUM_TIER_CLICKS_PER_LINK: int = 1000000

    # Stripe
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Analytics
    GEO_IP_DATABASE: Optional[str] = None  # MaxMind GeoIP2 path
    TRACK_ANALYTICS: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
