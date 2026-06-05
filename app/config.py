from typing import Any, Optional

from pydantic import field_validator, model_validator
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
)


_PLACEHOLDER_SECRET_KEYS = {
    "your-secret-key-change-in-production",
    "your-super-secret-key-change-in-production",
    "dev-secret-key",
}


def _parse_allowed_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


class CommaSeparatedEnvSettingsSource(EnvSettingsSource):
    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name == "ALLOWED_ORIGINS" and isinstance(value, str):
            stripped_value = value.strip()
            if not stripped_value:
                return []
            if not stripped_value.startswith("["):
                return _parse_allowed_origins(stripped_value)

        return super().prepare_field_value(field_name, field, value, value_is_complex)


class CommaSeparatedDotEnvSettingsSource(DotEnvSettingsSource):
    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name == "ALLOWED_ORIGINS" and isinstance(value, str):
            stripped_value = value.strip()
            if not stripped_value:
                return []
            if not stripped_value.startswith("["):
                return _parse_allowed_origins(stripped_value)

        return super().prepare_field_value(field_name, field, value, value_is_complex)


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

    # Short Links
    SHORT_CODE_LENGTH: int = 6
    SHORT_CODE_ALPHABET: str = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )
    SHORT_URL_BASE: str = "http://localhost:8000/r"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "https://app.example.com"]

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

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: Any) -> Any:
        if isinstance(value, str):
            return _parse_allowed_origins(value)

        return value

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.ENVIRONMENT.lower() == "production":
            secret_key = self.SECRET_KEY.strip()
            if not secret_key or secret_key in _PLACEHOLDER_SECRET_KEYS:
                raise ValueError(
                    "SECRET_KEY must be set to a non-placeholder value when "
                    "ENVIRONMENT=production"
                )

        return self

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            CommaSeparatedEnvSettingsSource(settings_cls),
            CommaSeparatedDotEnvSettingsSource(settings_cls),
            file_secret_settings,
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
