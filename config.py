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
    # PostgreSQL için DATABASE_URL environment variable'ı kontrol edilir
    # Örnek: postgresql://user:password@localhost/dbname
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///tevkil.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # SQL query logging
    
    # Database Connection Pooling (Fix for "Internal Server Error")
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,        # Check connection before using
        'pool_recycle': 300,          # Recycle connections every 5 minutes
        'pool_timeout': 30,           # Wait max 30s for a connection
        'pool_size': 10,              # Keep 10 connections open
        'max_overflow': 5             # Allow 5 more temporary connections
    }
    
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
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', 'G-QRCQ663WPD')
    
    # Netgsm SMS Configuration
    NETGSM_USERNAME = os.environ.get('NETGSM_USERNAME')
    NETGSM_PASSWORD = os.environ.get('NETGSM_PASSWORD')
    NETGSM_SENDER = os.environ.get('NETGSM_SENDER', 'TEVKIL')

    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', ADMIN_EMAIL)
    
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
