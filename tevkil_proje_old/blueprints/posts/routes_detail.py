"""
Posts Blueprint - Detail View Route
Separated for better organization (large file)
"""
from flask import render_template
from flask_login import current_user
from datetime import datetime, timedelta, timezone
import os

from models import TevkilPost, Application, Favorite
from blueprints.helpers import update_post_view, get_post_stats
from constants import TASK_CATEGORY_LABELS


def post_detail_view(post_id):
    """İlan detayı"""
    post = TevkilPost.query.get_or_404(post_id)
    
    # Update view count
    update_post_view(post_id, current_user.id if current_user.is_authenticated else None)
    
    # Get applications
    applications = Application.query.filter_by(post_id=post_id).order_by(Application.created_at.desc()).all()
    
    # Check if favorited
    is_favorited = False
    if current_user.is_authenticated:
        is_favorited = Favorite.query.filter_by(user_id=current_user.id, post_id=post_id).first() is not None
    
    # Get stats
    post_stats = get_post_stats(post_id) or {}

    now = datetime.now(timezone.utc)
    soon_threshold = now + timedelta(days=3)

    urgency_variants = {
        'very_urgent': {'label': 'Çok acil', 'variant': 'rose', 'icon': 'warning'},
        'urgent': {'label': 'Acil', 'variant': 'amber', 'icon': 'priority_high'},
        'normal': {'label': 'Normal', 'variant': 'slate', 'icon': 'schedule'},
        None: {'label': 'Normal', 'variant': 'slate', 'icon': 'schedule'},
    }

    status_variants = {
        'active': {'label': 'Aktif', 'variant': 'emerald'},
        'assigned': {'label': 'Atandı', 'variant': 'indigo'},
        'completed': {'label': 'Tamamlandı', 'variant': 'slate'},
        'cancelled': {'label': 'İptal edildi', 'variant': 'rose'},
    }

    def _to_utc(dt):
        if not dt:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    def _format_datetime(dt, fmt='%d %b %Y, %H:%M'):
        dt = _to_utc(dt)
        if not dt:
            return None
        return dt.strftime(fmt)

    def _time_ago(dt):
        dt = _to_utc(dt)
        if not dt:
            return ''
        delta = now - dt
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return 'az önce'
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} dk önce"
        hours = minutes // 60
        if hours < 24:
            return f"{hours} sa önce"
        days = hours // 24
        if days < 7:
            return f"{days} gün önce"
        weeks = days // 7
        if weeks < 5:
            return f"{weeks} hf önce"
        months = max(days // 30, 1)
        return f"{months} ay önce"

    def _format_currency(value):
        try:
            return f"{int(value):,}".replace(',', '.')
        except (TypeError, ValueError):
            return None

    price_display = None
    if post.price_min and post.price_max and post.price_min != post.price_max:
        price_display = f"{_format_currency(post.price_min)} - {_format_currency(post.price_max)} ₺"
    elif post.price_min:
        price_display = f"{_format_currency(post.price_min)} ₺"
    elif post.price_max:
        price_display = f"{_format_currency(post.price_max)} ₺"

    deadline_info = {'display': None, 'state': 'none', 'badge': None}
    deadline_source = post.court_date or post.deadline or post.expires_at
    deadline_dt = _to_utc(deadline_source)
    if deadline_dt:
        deadline_info['display'] = deadline_dt.strftime('%d %b %Y, %H:%M')
        if deadline_dt < now:
            deadline_info['state'] = 'overdue'
            deadline_info['badge'] = 'Süresi doldu'
        elif deadline_dt <= soon_threshold:
            deadline_info['state'] = 'soon'
            remaining = deadline_dt - now
            days_left = max(int(remaining.total_seconds() // 86400), 0)
            deadline_info['badge'] = 'Bugün' if days_left == 0 else f'{days_left} gün kaldı'
        else:
            deadline_info['state'] = 'scheduled'
            deadline_info['badge'] = 'Takvimde'

    location_display = (
        post.formatted_address
        or post.location
        or ', '.join(filter(None, [post.courthouse, post.district, post.city]))
        or 'Belirtilmemiş'
    )

    application_breakdown = {
        'total': len(applications),
        'pending': post_stats.get('pending_count', 0),
        'accepted': post_stats.get('accepted_count', 0),
        'rejected': post_stats.get('rejected_count', 0),
    }

    stats_cards = [
        {
            'label': 'Görüntülenme',
            'value': post_stats.get('view_count', post.view_count or post.views or 0),
            'icon': 'visibility',
            'variant': 'slate',
        },
        {
            'label': 'Toplam başvuru',
            'value': application_breakdown['total'],
            'icon': 'inbox',
            'variant': 'brand',
            'subtitle': f"{application_breakdown['pending']} bekliyor",
        },
        {
            'label': 'Kabul edilen',
            'value': application_breakdown['accepted'],
            'icon': 'task_alt',
            'variant': 'emerald',
            'subtitle': f"{application_breakdown['rejected']} reddedildi",
        },
        {
            'label': 'İlk başvuru süresi',
            'value': f"{post_stats.get('avg_time_to_apply_hours', 0)} sa",
            'icon': 'schedule',
            'variant': 'amber',
            'subtitle': 'İlk başvuruya kadar geçen süre',
        },
    ]

    detail_context = {
        'category_label': TASK_CATEGORY_LABELS.get(
            post.category,
            (post.category or 'diger').replace('_', ' ').title()
        ),
        'status': status_variants.get(post.status, {'label': post.status.title() if post.status else 'Durum yok', 'variant': 'slate'}),
        'urgency': urgency_variants.get(post.urgency_level, urgency_variants[None]),
        'deadline': deadline_info,
        'price_display': price_display,
        'created_display': _format_datetime(post.created_at),
        'created_ago': _time_ago(post.created_at),
        'last_viewed_display': _format_datetime(post_stats.get('last_viewed_at')),
        'court_date_display': _format_datetime(post.court_date),
        'expires_display': _format_datetime(post.expires_at),
        'deadline_due_display': _format_datetime(post.deadline),
        'location_display': location_display,
        'city': post.city,
        'courthouse': post.courthouse,
        'remote_allowed': bool(post.remote_allowed),
        'applications': application_breakdown,
        'favorite': is_favorited,
    }

    google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    return render_template('phoenix/posts/detail.html',
                         post=post,
                         applications=applications,
                         is_favorited=is_favorited,
                         post_stats=post_stats,
                         google_maps_key=google_maps_key,
                         detail=detail_context,
                         stats_cards=stats_cards)
