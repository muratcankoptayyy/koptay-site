"""Flask application factory for the Tevkil platform."""

from __future__ import annotations

from pathlib import Path

from flask import Flask
from dotenv import load_dotenv

from cache_config import init_cache
from models import db
from tevkil.config import get_config
from tevkil.extensions import init_extensions


def create_app() -> Flask:
    """Create, configure and return a Flask application instance."""

    load_dotenv()

    config_class = get_config()

    project_root = Path(__file__).resolve().parent.parent

    app = Flask(
        __name__,
        static_folder=str(project_root / "static"),
        template_folder=str(project_root / "templates"),
    )
    app.config.from_object(config_class)
    app.config.update(
        WHATSAPP_ENABLED=config_class.WHATSAPP_ENABLED,
        EMAIL_ENABLED=config_class.EMAIL_ENABLED,
        DEV_MODE=config_class.DEV_MODE,
        GOOGLE_MAPS_API_KEY=config_class.GOOGLE_MAPS_API_KEY,
    )

    db.init_app(app)
    init_extensions(app)

    cache = init_cache(app)
    app.extensions["cache"] = cache

    if app.config.get("EMAIL_ENABLED"):
        try:
            from email_service import init_mail

            app.extensions["mail"] = init_mail(app)
        except Exception as exc:  # pragma: no cover - safeguard logging
            app.logger.warning("Email service initialisation failed: %s", exc)
            app.config["EMAIL_ENABLED"] = False

    try:
        from sms_service import NetgsmSMSService

        app.extensions["sms_service"] = NetgsmSMSService()
    except Exception as exc:  # pragma: no cover - optional dependency
        app.logger.warning("SMS service initialisation failed: %s", exc)

    _init_monitoring(app)

    return app


def _init_monitoring(app: Flask) -> None:
    """Initialise optional monitoring integrations such as Sentry."""

    dsn = app.config.get("SENTRY_DSN")
    if not dsn:
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            dsn=dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=app.config.get("SENTRY_TRACES_SAMPLE_RATE", 0.0),
            environment=app.config.get(
                "SENTRY_ENVIRONMENT",
                "development" if app.config.get("DEV_MODE") else "production",
            ),
        )
        app.logger.info("Sentry monitoring initialised")
    except ImportError as exc:  # pragma: no cover - dependency missing
        app.logger.warning("Sentry SDK not available: %s", exc)
    except Exception as exc:  # pragma: no cover - defensive log
        app.logger.warning("Sentry initialisation failed: %s", exc)
