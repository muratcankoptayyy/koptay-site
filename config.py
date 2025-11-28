"""
Configuration for Tevkil Platform
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tevkil.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # SQL query logging
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # HTTPS'de True olmalı
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # CSRF token süresiz
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = False  # HTTPS'de True olmalı
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Upload
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # Pagination
    POSTS_PER_PAGE = 20
    APPLICATIONS_PER_PAGE = 10
    MESSAGES_PER_PAGE = 50
    NOTIFICATIONS_PER_PAGE = 20
    
    # Application Settings
    APP_NAME = 'UTAP - Ulusal Tevkil Ağı'
    ADMIN_EMAIL = 'admin@utap.com'
    SUPPORT_EMAIL = 'destek@utap.com'
    
    # Dev Mode - Login bypass for development
    DEV_MODE = os.environ.get('DEV_MODE', 'True') == 'True'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DEV_MODE = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DEV_MODE = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # Production database (PostgreSQL recommended)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
