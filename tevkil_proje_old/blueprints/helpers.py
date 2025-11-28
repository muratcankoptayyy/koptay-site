"""
Shared helper functions for blueprints.

Common utility functions used across multiple blueprints.
"""

from flask import request, jsonify
from datetime import datetime, timezone
from utils.logger import get_logger

logger = get_logger(__name__)


def get_client_ip():
    """
    Get client IP address from request.
    
    Handles X-Forwarded-For header for proxied requests.
    
    Returns:
        str: Client IP address
    """
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


def is_ajax_request():
    """
    Check if the current request is an AJAX request.
    
    Returns:
        bool: True if AJAX request, False otherwise
    """
    return (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        request.is_json or
        request.path.startswith('/api/')
    )


def json_response(success=True, message='', data=None, status_code=200):
    """
    Create standardized JSON response.
    
    Args:
        success (bool): Success status
        message (str): Response message
        data (dict): Additional data to include
        status_code (int): HTTP status code
    
    Returns:
        tuple: (JSON response, status code)
    """
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    if data:
        response.update(data)
    
    return jsonify(response), status_code


def error_response(message, status_code=400, **kwargs):
    """
    Create standardized error JSON response.
    
    Args:
        message (str): Error message
        status_code (int): HTTP status code
        **kwargs: Additional fields to include
    
    Returns:
        tuple: (JSON response, status code)
    """
    return json_response(
        success=False,
        message=message,
        data=kwargs,
        status_code=status_code
    )


def success_response(message, data=None, status_code=200):
    """
    Create standardized success JSON response.
    
    Args:
        message (str): Success message
        data (dict): Additional data to include
        status_code (int): HTTP status code
    
    Returns:
        tuple: (JSON response, status code)
    """
    return json_response(
        success=True,
        message=message,
        data=data,
        status_code=status_code
    )


def paginate_query(query, page=None, per_page=20):
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page (int): Page number (1-indexed), defaults to request arg 'page'
        per_page (int): Items per page
    
    Returns:
        dict: Pagination data with items, total, pages, current_page
    """
    if page is None:
        page = request.args.get('page', 1, type=int)
    
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next,
        'prev_page': pagination.prev_num,
        'next_page': pagination.next_num
    }


def flash_form_errors(form):
    """
    Flash all WTForm validation errors.
    
    Args:
        form: WTForms form instance with errors
    """
    from flask import flash
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')


def generate_post_title(category, city=None, courthouse=None, district=None):
    """
    Generate automatic post title from category and location.
    
    Args:
        category (str): Post category
        city (str): City name
        courthouse (str): Courthouse name
        district (str): District name
    
    Returns:
        str: Generated title
    """
    from constants import CATEGORY_ABBREVIATIONS
    
    location_candidates = [courthouse, district, city]
    location = next((item.strip() for item in location_candidates if item and item.strip()), 'Görev')
    abbreviation = CATEGORY_ABBREVIATIONS.get(category, 'GEN')
    
    return f"{location} - {abbreviation}"


def sanitize_filename(filename):
    """
    Sanitize uploaded filename to prevent security issues.
    
    Args:
        filename (str): Original filename
    
    Returns:
        str: Sanitized filename
    """
    from werkzeug.utils import secure_filename
    import secrets
    from pathlib import Path
    
    # Get file extension
    ext = Path(filename).suffix.lower()
    
    # Generate secure base name
    base = secure_filename(Path(filename).stem)
    if not base:
        base = 'file'
    
    # Add random suffix to prevent collisions
    random_suffix = secrets.token_hex(8)
    
    return f"{base}_{random_suffix}{ext}"


def allowed_file(filename, allowed_extensions):
    """
    Check if file extension is allowed.
    
    Args:
        filename (str): Filename to check
        allowed_extensions (set): Set of allowed extensions (with dots)
    
    Returns:
        bool: True if allowed, False otherwise
    """
    from pathlib import Path
    return Path(filename).suffix.lower() in allowed_extensions


def create_notification(user_id, notification_type, title, message, related_post_id=None, 
                       related_user_id=None, priority='normal', category='general', 
                       action_url=None, action_text=None):
    """
    Create a new notification for a user.
    
    Args:
        user_id: User ID to receive notification
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        related_post_id: Related post ID
        related_user_id: Related user ID
        priority: Priority level (low, normal, high, urgent)
        category: Category (application, message, system, warning)
        action_url: URL to navigate to
        action_text: Action button text
    
    Returns:
        Notification object or None
    """
    from models import db, User, Notification
    
    user = User.query.get(user_id)
    if not user:
        return None
    
    # Check notification preferences
    if notification_type == 'new_application' and not user.notify_new_application:
        return None
    elif notification_type in ['application_accepted', 'application_rejected'] and not user.notify_application_status:
        return None
    elif notification_type == 'new_message' and not user.notify_new_message:
        return None
    elif notification_type == 'new_rating' and not user.notify_new_rating:
        return None
    elif notification_type == 'post_expiring' and not user.notify_post_expiring:
        return None
    elif notification_type == 'system' and not user.notify_system:
        return None
    
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        related_post_id=related_post_id,
        related_user_id=related_user_id,
        priority=priority,
        category=category,
        action_url=action_url,
        action_text=action_text
    )
    db.session.add(notification)
    db.session.commit()
    return notification


def get_post_stats(post_id):
    """Get statistics for a post."""
    from models import PostView, Application
    from sqlalchemy import func
    
    stats = {
        'view_count': PostView.query.filter_by(post_id=post_id).count(),
        'unique_viewers': PostView.query.filter_by(post_id=post_id).with_entities(
            func.count(func.distinct(PostView.user_id))
        ).scalar() or 0,
        'last_viewed_at': None,
        'pending_count': Application.query.filter_by(post_id=post_id, status='pending').count(),
        'accepted_count': Application.query.filter_by(post_id=post_id, status='accepted').count(),
        'rejected_count': Application.query.filter_by(post_id=post_id, status='rejected').count(),
        'avg_time_to_apply_hours': 0,
    }
    
    last_view = PostView.query.filter_by(post_id=post_id).order_by(
        PostView.viewed_at.desc()
    ).first()
    if last_view:
        stats['last_viewed_at'] = last_view.viewed_at
    
    return stats


def update_post_view(post_id, user_id=None):
    """Update post view count."""
    from models import db, PostView, TevkilPost
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        post = TevkilPost.query.get(post_id)
        if post:
            if post.view_count is None:
                post.view_count = 0
            post.view_count += 1
        
        if user_id:
            view = PostView(post_id=post_id, user_id=user_id)
            db.session.add(view)
        
        db.session.commit()
    except Exception as e:
        logger.error(f"Error updating post view: {e}")
        db.session.rollback()
