"""Application configuration helpers."""

from __future__ import annotations

import os
from datetime import timedelta
from typing import Any, Dict, Type, cast

from database_pooling_config import DATABASE_CONFIG

DATABASE_OPTIONS: Dict[str, Any] = cast(Dict[str, Any], DATABASE_CONFIG)


def _coerce_bool(value: str | None, *, default: bool = False) -> bool:
    """Return a boolean for various truthy string representations."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_database_uri(default: str = "sqlite:///tevkil.db") -> str:
    """Normalize DATABASE_URL for SQLAlchemy."""
    database_url = os.getenv("DATABASE_URL", default)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    return database_url


class Config:
    """Default production configuration."""

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = DATABASE_OPTIONS

    DEV_MODE = False

    WHATSAPP_ENABLED = _coerce_bool(os.getenv("WHATSAPP_ENABLED"), default=False)
    EMAIL_ENABLED = _coerce_bool(os.getenv("EMAIL_ENABLED"), default=True)
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_REFRESH_EACH_REQUEST = True

    REMEMBER_COOKIE_DURATION = timedelta(hours=24)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = False

    SEND_FILE_MAX_AGE_DEFAULT = 31536000

    RATELIMIT_DEFAULT = "10000 per day;500 per hour"
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_STRATEGY = "fixed-window"

    SOCKETIO_ASYNC_MODE = "threading"
    SOCKETIO_ALLOWED_ORIGINS = [
        "https://tevkil.fly.dev",
        "https://www.tevkil.fly.dev",
        os.getenv("FRONTEND_URL", "https://tevkil.fly.dev"),
    ]

    CORS_ALLOWED_ORIGINS = SOCKETIO_ALLOWED_ORIGINS
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization", "X-CSRFToken"]
    CORS_SUPPORTS_CREDENTIALS = True


class DevelopmentConfig(Config):
    """Relaxed defaults for local development."""

    DEV_MODE = True

    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

    CORS_ALLOWED_ORIGINS = ["*"]
    SOCKETIO_ALLOWED_ORIGINS = ["*"]
    CORS_SUPPORTS_CREDENTIALS = False


def get_config() -> Type[Config]:
    """Return the appropriate config class based on FLASK_ENV."""

    env = os.getenv("FLASK_ENV", "production").lower()
    if env in {"development", "dev"}:
        return DevelopmentConfig
    return Config
