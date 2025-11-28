"""Centralized logging configuration for Tevkil Platform."""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    """
    Configure application logging with environment-specific settings.
    
    - Development: Human-readable console logs
    - Production: JSON structured logs + file rotation
    
    Args:
        app: Flask application instance
        
    Returns:
        Configured logger instance
    """
    
    # Log seviyesi (DEV_MODE'a göre)
    log_level = logging.DEBUG if app.config.get('DEV_MODE') else logging.INFO
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Mevcut handler'ları temizle (duplicate log engelleme)
    root_logger.handlers.clear()
    
    # 1. CONSOLE HANDLER
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if app.config.get('DEV_MODE'):
        # Development: Human readable format
        formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Production: Daha detaylı format
        formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 2. FILE HANDLER (Production only)
    if not app.config.get('DEV_MODE'):
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Main application log
        file_handler = RotatingFileHandler(
            log_dir / 'tevkil.log',
            maxBytes=10_485_760,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Error log (sadece ERROR ve üstü)
        error_handler = RotatingFileHandler(
            log_dir / 'tevkil_errors.log',
            maxBytes=5_242_880,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    # 3. APP LOGGER
    app.logger.setLevel(log_level)
    
    # Werkzeug (Flask's built-in server) log seviyesini ayarla
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING if not app.config.get('DEV_MODE') else logging.INFO)
    
    # SQLAlchemy logging (sadece development'ta SQL query'leri göster)
    if app.config.get('DEV_MODE') and app.config.get('SQLALCHEMY_ECHO'):
        sql_logger = logging.getLogger('sqlalchemy.engine')
        sql_logger.setLevel(logging.INFO)
    
    app.logger.info(f"Logging configured - Level: {logging.getLevelName(log_level)}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Usage:
        logger = get_logger(__name__)
        logger.info("Something happened")
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
