"""Blueprints package for modular route organization."""

from flask import Blueprint

# Import all blueprints
from blueprints.auth import auth_bp
from blueprints.posts import posts_bp
from blueprints.applications import applications_bp
from blueprints.chat import chat_bp
from blueprints.admin import admin_bp
from blueprints.api import api_bp
from blueprints.main import main_bp

__all__ = [
    'auth_bp',
    'posts_bp',
    'applications_bp',
    'chat_bp',
    'admin_bp',
    'api_bp',
    'main_bp',
]


def register_blueprints(app):
    """
    Register all blueprints with the Flask app.
    
    Args:
        app: Flask application instance
    """
    # Main/Public routes (no prefix)
    app.register_blueprint(main_bp)
    
    # Authentication routes (no prefix for compatibility)
    app.register_blueprint(auth_bp)
    
    # Posts routes
    app.register_blueprint(posts_bp, url_prefix='/posts')
    
    # Applications routes
    app.register_blueprint(applications_bp, url_prefix='/applications')
    
    # Chat routes
    app.register_blueprint(chat_bp, url_prefix='/chat')
    
    # Admin routes
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # API routes
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("All blueprints registered successfully")
