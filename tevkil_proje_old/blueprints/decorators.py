"""
Shared decorators for blueprints.

These decorators are used across multiple blueprints to handle
common concerns like authentication, authorization, and validation.
"""

from functools import wraps
from flask import flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from utils.logger import get_logger

logger = get_logger(__name__)


def admin_required(f):
    """
    Decorator to require admin privileges.
    
    Usage:
        @blueprint.route('/admin/something')
        @admin_required
        def admin_function():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Bu sayfaya erişim için giriş yapmalısınız.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Bu sayfaya erişim yetkiniz yok.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def dev_login_optional(f):
    """
    Development mode: login bypass decorator.
    
    In development mode, automatically logs in the first user if not authenticated.
    In production mode, behaves like normal login_required.
    
    Usage:
        @blueprint.route('/test')
        @dev_login_optional
        def test_function():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get('DEV_MODE', False):
            # Development mode: auto-login first user if not authenticated
            if not current_user.is_authenticated:
                from models import User
                from flask_login import login_user
                first_user = User.query.first()
                if first_user:
                    login_user(first_user, remember=True)
                    logger.info(f"DEV MODE: Auto-logged in as {first_user.email}")
            return f(*args, **kwargs)
        else:
            # Production mode: normal login_required behavior
            return login_required(f)(*args, **kwargs)
    return decorated_function


def verified_user_required(f):
    """
    Decorator to require verified user status.
    
    Usage:
        @blueprint.route('/verified-only')
        @verified_user_required
        def verified_function():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Bu sayfaya erişim için giriş yapmalısınız.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_verified:
            flash('Bu işlem için hesabınızın doğrulanmış olması gerekir.', 'warning')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def ajax_login_required(f):
    """
    Decorator for AJAX requests that require authentication.
    Returns JSON error instead of redirecting.
    
    Usage:
        @blueprint.route('/api/something', methods=['POST'])
        @ajax_login_required
        def ajax_function():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            from flask import jsonify
            return jsonify({
                'success': False,
                'error': 'Kimlik doğrulaması gerekli',
                'redirect': url_for('auth.login')
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def ownership_required(model_class, id_param='id', owner_field='user_id'):
    """
    Decorator to verify user owns the resource.
    
    Args:
        model_class: SQLAlchemy model class
        id_param: URL parameter name for resource ID
        owner_field: Field name in model that stores owner user_id
    
    Usage:
        @blueprint.route('/posts/<int:post_id>/edit')
        @ownership_required(TevkilPost, 'post_id', 'user_id')
        def edit_post(post_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Bu sayfaya erişim için giriş yapmalısınız.', 'error')
                return redirect(url_for('auth.login'))
            
            # Get resource ID from URL parameters
            resource_id = kwargs.get(id_param)
            if not resource_id:
                flash('Geçersiz istek.', 'error')
                return redirect(url_for('main.dashboard'))
            
            # Get resource from database
            from models import db
            resource = db.session.get(model_class, resource_id)
            if not resource:
                flash('Kayıt bulunamadı.', 'error')
                return redirect(url_for('main.dashboard'))
            
            # Check ownership (unless user is admin)
            owner_id = getattr(resource, owner_field, None)
            if owner_id != current_user.id and not current_user.is_admin:
                flash('Bu işlem için yetkiniz yok.', 'error')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
