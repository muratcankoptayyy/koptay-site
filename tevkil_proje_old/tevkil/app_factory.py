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
    
    # Register Jinja2 custom url_for for blueprint compatibility
    _register_jinja_globals(app)

    return app


def _register_jinja_globals(app: Flask) -> None:
    """Register custom Jinja2 global functions for template compatibility."""
    from flask import url_for as flask_url_for
    
    # Auth blueprint endpoint mapping
    AUTH_ENDPOINT_MAP = {
        'register': 'auth.register',
        'login': 'auth.login',
        'logout': 'auth.logout',
        'forgot_password': 'auth.forgot_password',
        'reset_password': 'auth.reset_password',
        'verify_2fa': 'auth.verify_2fa',
    }
    
    # Main blueprint endpoint mapping
    MAIN_ENDPOINT_MAP = {
        'index': 'main.index',
        'dashboard': 'main.dashboard',
        'stats_page': 'main.stats_page',
        'user_profile': 'main.user_profile',
        'edit_profile': 'main.edit_profile',
        'settings': 'main.settings',
        'favorites': 'main.favorites',
        'toggle_favorite': 'main.toggle_favorite',
        'contact': 'main.contact',
        'privacy_policy': 'main.privacy_policy',
        'terms_of_service': 'main.terms_of_service',
        'cookie_policy': 'main.cookie_policy',
        'health_check': 'main.health_check',
        'manifest': 'main.manifest',
        'service_worker': 'main.service_worker',
    }
    
    # Applications blueprint endpoint mapping
    APPLICATIONS_ENDPOINT_MAP = {
        'applications_received': 'applications.received',
        'applications_sent': 'applications.sent',
        'accept_application': 'applications.accept_application',
        'reject_application': 'applications.reject_application',
        'get_authorization_info': 'applications.authorization_info',
        'generate_authorization_pdf': 'applications.generate_authorization_pdf',
    }
    
    # Posts blueprint endpoint mapping
    POSTS_ENDPOINT_MAP = {
        'list_posts': 'posts.list_posts',
        'create_post': 'posts.create_post',
        'post_detail': 'posts.post_detail',
        'edit_post': 'posts.edit_post',
        'delete_post': 'posts.delete_post',
        'apply_to_post': 'posts.apply_to_post',
        'map_view': 'posts.map_view',
    }
    
    # Chat blueprint endpoint mapping
    CHAT_ENDPOINT_MAP = {
        'chat': 'chat.chat_index',
        'chat_conversation': 'chat.conversation',
        'start_chat': 'chat.start_conversation',
        'send_chat_message': 'chat.send_message',
        'get_new_messages': 'chat.get_new_messages',
        'chat_typing_indicator': 'chat.typing_indicator',
        'upload_chat_file': 'chat.upload_file',
    }
    
    # Admin blueprint endpoint mapping
    ADMIN_ENDPOINT_MAP = {
        'admin_analytics': 'admin.analytics',
        'export_analytics': 'admin.export_analytics',
        'admin_users': 'admin.users',
        'admin_user_detail': 'admin.user_detail',
        'admin_toggle_user_status': 'admin.toggle_user_status',
        'admin_verify_user': 'admin.verify_user',
        'admin_update_report': 'admin.update_report',
    }
    
    API_ENDPOINT_MAP = {
        'api_posts': 'api.posts',
        'api_courthouses': 'api.courthouses',
        'whatsapp_webhook': 'api.whatsapp_webhook',
        'whatsapp_test': 'api.whatsapp_test',
        'api_mobile_login': 'api.mobile_login',
        'api_mobile_logout': 'api.mobile_logout',
        'api_mobile_verify': 'api.mobile_verify',
        'register_device_token': 'api.register_device_token',
        'unregister_device_token': 'api.unregister_device_token',
        'submit_contact_form': 'api.submit_contact_form',
    }
    
    def smart_url_for(endpoint, **values):
        """Smart url_for with automatic blueprint endpoint mapping."""
        # Map old endpoints to blueprint endpoints
        if endpoint in AUTH_ENDPOINT_MAP:
            endpoint = AUTH_ENDPOINT_MAP[endpoint]
        elif endpoint in MAIN_ENDPOINT_MAP:
            endpoint = MAIN_ENDPOINT_MAP[endpoint]
        elif endpoint in APPLICATIONS_ENDPOINT_MAP:
            endpoint = APPLICATIONS_ENDPOINT_MAP[endpoint]
        elif endpoint in POSTS_ENDPOINT_MAP:
            endpoint = POSTS_ENDPOINT_MAP[endpoint]
        elif endpoint in CHAT_ENDPOINT_MAP:
            endpoint = CHAT_ENDPOINT_MAP[endpoint]
        elif endpoint in ADMIN_ENDPOINT_MAP:
            endpoint = ADMIN_ENDPOINT_MAP[endpoint]
        elif endpoint in API_ENDPOINT_MAP:
            endpoint = API_ENDPOINT_MAP[endpoint]
        
        return flask_url_for(endpoint, **values)
    
    # Override default url_for in Jinja2
    app.jinja_env.globals['url_for'] = smart_url_for
    app.logger.info("Jinja2 custom url_for registered for blueprint compatibility")


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
