"""Global error handlers for Flask application."""

from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import traceback

from utils.exceptions import TevkilException
from utils.logger import get_logger

logger = get_logger(__name__)


def register_error_handlers(app):
    """
    Register global error handlers for the Flask app.
    
    Usage:
        from utils.error_handlers import register_error_handlers
        register_error_handlers(app)
    """
    
    @app.errorhandler(TevkilException)
    def handle_tevkil_exception(e):
        """Handle custom Tevkil exceptions."""
        logger.warning(
            f"Tevkil exception occurred: {e.message}",
            extra={
                'status_code': e.status_code,
                'payload': e.payload,
                'path': request.path,
                'method': request.method
            }
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify(e.to_dict()), e.status_code
        
        return render_template(
            'error.html',
            error=e.message,
            status_code=e.status_code
        ), e.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle Werkzeug HTTP exceptions (404, 405, etc.)."""
        logger.info(
            f"HTTP exception: {e.code} - {e.name}",
            extra={
                'path': request.path,
                'method': request.method,
                'description': e.description
            }
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': e.description or e.name,
                'status_code': e.code
            }), e.code
        
        return render_template(
            'error.html',
            error=e.description or e.name,
            status_code=e.code
        ), e.code
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(e):
        """Handle SQLAlchemy integrity constraint violations."""
        logger.error(
            "Database integrity error",
            extra={
                'error': str(e.orig),
                'path': request.path,
                'method': request.method
            }
        )
        
        # Parse common integrity errors
        error_str = str(e.orig).lower()
        
        if 'unique constraint' in error_str or 'duplicate' in error_str:
            message = "Bu kayıt zaten mevcut"
        elif 'foreign key constraint' in error_str:
            message = "İlişkili kayıt bulunamadı"
        elif 'not null constraint' in error_str:
            message = "Zorunlu alan eksik"
        else:
            message = "Veritabanı kısıtlama hatası"
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': message,
                'status_code': 400
            }), 400
        
        return render_template(
            'error.html',
            error=message,
            status_code=400
        ), 400
    
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(e):
        """Handle other SQLAlchemy errors."""
        logger.error(
            "Database error occurred",
            extra={
                'error': str(e),
                'path': request.path,
                'method': request.method
            },
            exc_info=True
        )
        
        message = "Veritabanı hatası oluştu"
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': message,
                'status_code': 500
            }), 500
        
        return render_template(
            'error.html',
            error=message,
            status_code=500
        ), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        """Handle unexpected exceptions (catch-all)."""
        logger.critical(
            f"Unexpected error: {str(e)}",
            extra={
                'path': request.path,
                'method': request.method,
                'traceback': traceback.format_exc()
            },
            exc_info=True
        )
        
        message = "Beklenmeyen bir hata oluştu"
        
        # In development, show detailed error
        if app.debug:
            message = f"DEBUG: {str(e)}"
        
        if request.is_json or request.path.startswith('/api/'):
            response = {
                'error': message,
                'status_code': 500
            }
            if app.debug:
                response['traceback'] = traceback.format_exc()
            return jsonify(response), 500
        
        return render_template(
            'error.html',
            error=message,
            status_code=500,
            traceback=traceback.format_exc() if app.debug else None
        ), 500
    
    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle 404 Not Found errors."""
        logger.info(
            f"404 Not Found: {request.path}",
            extra={
                'method': request.method,
                'referrer': request.referrer
            }
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Sayfa bulunamadı',
                'status_code': 404
            }), 404
        
        return render_template(
            'error.html',
            error='Aradığınız sayfa bulunamadı',
            status_code=404
        ), 404
    
    @app.errorhandler(403)
    def handle_forbidden(e):
        """Handle 403 Forbidden errors."""
        logger.warning(
            f"403 Forbidden: {request.path}",
            extra={
                'method': request.method,
                'user': getattr(request, 'user', None)
            }
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Bu işlem için yetkiniz yok',
                'status_code': 403
            }), 403
        
        return render_template(
            'error.html',
            error='Bu işlem için yetkiniz yok',
            status_code=403
        ), 403
    
    @app.errorhandler(429)
    def handle_rate_limit(e):
        """Handle rate limit errors from Flask-Limiter."""
        logger.warning(
            f"Rate limit exceeded: {request.path}",
            extra={
                'method': request.method,
                'ip': request.remote_addr
            }
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Çok fazla istek. Lütfen daha sonra tekrar deneyin.',
                'status_code': 429
            }), 429
        
        return render_template(
            'error.html',
            error='Çok fazla istek. Lütfen daha sonra tekrar deneyin.',
            status_code=429
        ), 429
    
    logger.info("Global error handlers registered successfully")
