#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main Blueprint Helpers
Helper functions for dashboard, profile, and other main routes
"""

import logging
from datetime import datetime, timezone, timedelta
from models import db, TevkilPost, Application, Notification, Rating
from sqlalchemy import func

logger = logging.getLogger(__name__)


def get_user_stats(user_id):
    """
    Calculate comprehensive user statistics
    
    Args:
        user_id: User ID to get stats for
        
    Returns:
        dict: User statistics including ratings, success rate, response time, etc.
    """
    try:
        from models import User
        user = User.query.get(user_id)
        if not user:
            return {}
        
        # Rating stats
        ratings = Rating.query.filter_by(reviewed_id=user_id).all()
        rating_count = len(ratings)
        rating_average = sum(r.rating for r in ratings) / rating_count if rating_count > 0 else 0
        
        # Success rate (completed vs cancelled)
        total_posts = TevkilPost.query.filter_by(user_id=user_id).count()
        completed_posts = TevkilPost.query.filter_by(user_id=user_id, status='completed').count()
        success_rate = (completed_posts / total_posts * 100) if total_posts > 0 else 0
        
        # Average response time (simplified - could be more sophisticated)
        average_response_time = 24  # Default 24 hours
        
        return {
            'rating_count': rating_count,
            'rating_average': round(rating_average, 1),
            'success_rate': round(success_rate, 1),
            'total_posts': total_posts,
            'completed_posts': completed_posts,
            'average_response_time': average_response_time,
        }
    except Exception as e:
        logger.error(f"❌ Error getting user stats: {e}")
        return {}


def get_platform_stats():
    """
    Get platform-wide statistics (for admin dashboard)
    
    Returns:
        dict: Platform statistics
    """
    try:
        from models import User
        
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        total_posts = TevkilPost.query.count()
        active_posts = TevkilPost.query.filter_by(status='active').count()
        total_applications = Application.query.count()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_posts': total_posts,
            'active_posts': active_posts,
            'total_applications': total_applications,
        }
    except Exception as e:
        logger.error(f"❌ Error getting platform stats: {e}")
        return {}


def get_dashboard_metrics(user_id):
    """
    Get dashboard metrics for a user
    
    Args:
        user_id: User ID
        
    Returns:
        list: List of metric dictionaries
    """
    try:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        # Active posts
        my_posts = TevkilPost.query.filter_by(user_id=user_id).all()
        active_posts_count = sum(1 for post in my_posts if post.status == 'active')
        new_active_posts = sum(
            1 for post in my_posts
            if post.status == 'active' and (post.created_at or datetime.now(timezone.utc)) >= week_ago
        )
        
        # Incoming applications
        incoming_applications = db.session.query(Application).join(TevkilPost).filter(
            TevkilPost.user_id == user_id
        ).all()
        incoming_total = len(incoming_applications)
        incoming_recent = sum(1 for app in incoming_applications if (app.created_at or datetime.now(timezone.utc)) >= week_ago)
        
        # Outgoing applications
        my_applications = Application.query.filter_by(applicant_id=user_id).all()
        outgoing_total = len(my_applications)
        outgoing_recent = sum(1 for app in my_applications if (app.created_at or datetime.now(timezone.utc)) >= week_ago)
        
        # Notifications
        unread_notifications = Notification.query.filter_by(user_id=user_id, read_at=None).count()
        recent_notifications_count = Notification.query.filter_by(user_id=user_id).filter(
            Notification.created_at >= week_ago
        ).count()
        
        def _metric_subtitle(delta):
            return f"Son 7 gün +{delta}" if delta else "Son 7 gün değişiklik yok"
        
        return [
            {
                "label": "Aktif ilanlar",
                "icon": "work",
                "value": active_posts_count,
                "subtitle": _metric_subtitle(new_active_posts),
                "url": "list_posts",  # Will be converted by smart_url_for
            },
            {
                "label": "Gelen başvurular",
                "icon": "inbox",
                "value": incoming_total,
                "subtitle": _metric_subtitle(incoming_recent),
                "url": "applications_received",
            },
            {
                "label": "Başvurularım",
                "icon": "send",
                "value": outgoing_total,
                "subtitle": _metric_subtitle(outgoing_recent),
                "url": "applications_sent",
            },
            {
                "label": "Okunmamış bildirim",
                "icon": "notifications",
                "value": unread_notifications,
                "subtitle": _metric_subtitle(recent_notifications_count),
                "url": "notifications",
            },
        ]
    except Exception as e:
        logger.error(f"❌ Error getting dashboard metrics: {e}")
        return []


def get_chart_data(user_id, months=6):
    """
    Get chart data for dashboard
    
    Args:
        user_id: User ID
        months: Number of months to include
        
    Returns:
        dict: Chart data with labels and datasets
    """
    try:
        now = datetime.now(timezone.utc)
        chart_months = []
        chart_incoming = []
        chart_outgoing = []
        
        turkish_months = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']
        
        for i in range(months - 1, -1, -1):
            month_date = now - timedelta(days=30 * i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if i == 0:
                month_end = now
            else:
                next_month = month_start.replace(day=28) + timedelta(days=4)
                month_end = next_month - timedelta(days=next_month.day)
            
            chart_months.append(turkish_months[month_start.month - 1])
            
            # Gelen başvurular
            incoming_count = db.session.query(Application).join(TevkilPost).filter(
                TevkilPost.user_id == user_id,
                Application.created_at >= month_start,
                Application.created_at <= month_end
            ).count()
            chart_incoming.append(incoming_count)
            
            # Yaptığım başvurular
            outgoing_count = Application.query.filter(
                Application.applicant_id == user_id,
                Application.created_at >= month_start,
                Application.created_at <= month_end
            ).count()
            chart_outgoing.append(outgoing_count)
        
        # Kategori dağılımı
        category_data = db.session.query(
            TevkilPost.category,
            func.count(TevkilPost.id)
        ).filter_by(user_id=user_id).group_by(TevkilPost.category).all()
        
        return {
            'months': chart_months,
            'incoming': chart_incoming,
            'outgoing': chart_outgoing,
            'category_labels': [cat[0] or 'Diğer' for cat in category_data],
            'category_counts': [cat[1] for cat in category_data],
        }
    except Exception as e:
        logger.error(f"❌ Error getting chart data: {e}")
        return {
            'months': [],
            'incoming': [],
            'outgoing': [],
            'category_labels': [],
            'category_counts': [],
        }


def to_utc(dt):
    """
    Convert datetime to UTC timezone
    
    Args:
        dt: datetime object
        
    Returns:
        datetime: UTC datetime
    """
    if not dt:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
