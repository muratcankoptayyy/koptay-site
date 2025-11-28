"""Shared Flask extension instances."""

from __future__ import annotations

from flask_cors import CORS
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect

# Instantiate extensions once and initialise them in the app factory.
login_manager = LoginManager()
csrf = CSRFProtect()
socketio = SocketIO()
limiter = Limiter(key_func=get_remote_address)
cors = CORS()


def init_extensions(app) -> None:
    """Attach extensions to the given app instance."""

    login_manager.init_app(app)
    csrf.init_app(app)
    origins_cfg = app.config.get("CORS_ALLOWED_ORIGINS", ["*"])
    if origins_cfg == ["*"]:
        origins_cfg = "*"

    resources = {
        r"/*": {
            "origins": origins_cfg,
            "methods": app.config.get("CORS_METHODS", ["GET", "POST", "OPTIONS"]),
            "allow_headers": app.config.get(
                "CORS_ALLOW_HEADERS", ["Content-Type", "Authorization", "X-CSRFToken"]
            ),
            "supports_credentials": app.config.get("CORS_SUPPORTS_CREDENTIALS", True),
        }
    }
    cors.init_app(app, resources=resources)

    # Respect Flask-Limiter config keys (RATELIMIT_*) defined in app.config
    limiter.init_app(app)

    allowed_origins = app.config.get("SOCKETIO_ALLOWED_ORIGINS", ["*"])
    async_mode = app.config.get("SOCKETIO_ASYNC_MODE", "threading")
    socketio.init_app(app, cors_allowed_origins=allowed_origins, async_mode=async_mode)

    # Update to blueprint-qualified login view
    login_manager.login_view = "auth.login"  # type: ignore[attr-defined]
    login_manager.login_message_category = "error"
