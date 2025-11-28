"""
Admin Blueprint Helpers - Analytics and user management utilities
"""
from datetime import datetime, timedelta, timezone
from flask import flash, current_app
from sqlalchemy import extract, func
from sqlalchemy.exc import ProgrammingError

from models import db, User, TevkilPost, Application, Message, Rating, Report
from utils.logger import get_logger

logger = get_logger(__name__)


def _apply_date_range(query, column, start_dt=None, end_dt=None):
    """Apply optional start/end datetime filters to a SQLAlchemy query"""
    if start_dt:
        query = query.filter(column >= start_dt)
    if end_dt:
        query = query.filter(column < end_dt)
    return query


def _parse_analytics_filters(args):
    """Normalize incoming analytics filter query parameters"""
    filters = {
        'start_date': (args.get('start_date') or '').strip(),
        'end_date': (args.get('end_date') or '').strip(),
        'city': (args.get('city') or '').strip(),
        'category': (args.get('category') or '').strip(),
    }

    start_dt = None
    end_dt = None
    date_format = '%Y-%m-%d'

    if filters['start_date']:
        try:
            start_dt = datetime.strptime(filters['start_date'], date_format)
        except ValueError:
            flash('Geçersiz başlangıç tarihi formatı. YYYY-MM-DD kullanın.', 'error')
            filters['start_date'] = ''

    if filters['end_date']:
        try:
            end_dt = datetime.strptime(filters['end_date'], date_format) + timedelta(days=1)
        except ValueError:
            flash('Geçersiz bitiş tarihi formatı. YYYY-MM-DD kullanın.', 'error')
            filters['end_date'] = ''

    if start_dt and end_dt and end_dt <= start_dt:
        flash('Bitiş tarihi başlangıç tarihinden sonra olmalıdır.', 'error')
        start_dt = None
        end_dt = None
        filters['start_date'] = ''
        filters['end_date'] = ''

    filters['start_dt'] = start_dt
    filters['end_dt'] = end_dt
    filters['query_params'] = {
        key: value for key, value in filters.items()
        if key in ('start_date', 'end_date', 'city', 'category') and value
    }
    filters['has_active'] = any(filters['query_params'].values())
    return filters


def _gather_analytics_stats(filters):
    """Collect analytics metrics respecting the active filter set"""
    now = datetime.now(timezone.utc)
    start_dt = filters.get('start_dt')
    end_dt = filters.get('end_dt')
    city = filters.get('city') or None
    category = filters.get('category') or None

    week_threshold = now - timedelta(days=7)
    month_threshold = now - timedelta(days=30)
    year_threshold = now - timedelta(days=365)

    week_start = max(week_threshold, start_dt) if start_dt else week_threshold
    month_start = max(month_threshold, start_dt) if start_dt else month_threshold
    year_start = max(year_threshold, start_dt) if start_dt else year_threshold

    # User stats
    user_query = _apply_date_range(User.query, User.created_at, start_dt, end_dt)
    total_users = user_query.count()
    active_users_week = _apply_date_range(User.query, User.last_active, week_start, end_dt).count()
    active_users_month = _apply_date_range(User.query, User.last_active, month_start, end_dt).count()
    new_users_week = _apply_date_range(User.query, User.created_at, week_start, end_dt).count()
    new_users_month = _apply_date_range(User.query, User.created_at, month_start, end_dt).count()

    registrations_query = db.session.query(
        extract('year', User.created_at).label('year'),
        extract('month', User.created_at).label('month'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= year_start)
    registrations_query = _apply_date_range(registrations_query, User.created_at, start_dt, end_dt)
    user_registrations_by_month = registrations_query.group_by('year', 'month').order_by('year', 'month').all()

    # Post stats with filters
    post_conditions = []
    if city:
        post_conditions.append(TevkilPost.city == city)
    if category:
        post_conditions.append(TevkilPost.category == category)

    def _filtered_post_query():
        query = TevkilPost.query
        for condition in post_conditions:
            query = query.filter(condition)
        return query

    post_query = _apply_date_range(_filtered_post_query(), TevkilPost.created_at, start_dt, end_dt)

    total_posts = post_query.count()
    active_posts = post_query.filter(TevkilPost.status == 'active').count()
    completed_posts = post_query.filter(TevkilPost.status == 'completed').count()
    cancelled_posts = post_query.filter(TevkilPost.status == 'cancelled').count()

    posts_this_week = _apply_date_range(_filtered_post_query(), TevkilPost.created_at, week_start, end_dt).count()
    posts_this_month = _apply_date_range(_filtered_post_query(), TevkilPost.created_at, month_start, end_dt).count()

    posts_by_category_query = db.session.query(
        TevkilPost.category,
        func.count(TevkilPost.id).label('count')
    )
    for condition in post_conditions:
        posts_by_category_query = posts_by_category_query.filter(condition)
    posts_by_category = _apply_date_range(
        posts_by_category_query, TevkilPost.created_at, start_dt, end_dt
    ).group_by(TevkilPost.category).order_by(func.count(TevkilPost.id).desc()).all()

    posts_by_city_query = db.session.query(
        TevkilPost.city,
        func.count(TevkilPost.id).label('count')
    )
    for condition in post_conditions:
        posts_by_city_query = posts_by_city_query.filter(condition)
    posts_by_city = _apply_date_range(
        posts_by_city_query, TevkilPost.created_at, start_dt, end_dt
    ).group_by(TevkilPost.city).order_by(func.count(TevkilPost.id).desc()).limit(10).all()

    # Application stats
    def _filtered_application_query():
        query = Application.query
        if post_conditions:
            query = query.join(TevkilPost, Application.post_id == TevkilPost.id)
            for condition in post_conditions:
                query = query.filter(condition)
        return query

    applications_query = _apply_date_range(_filtered_application_query(), Application.created_at, start_dt, end_dt)

    total_applications = applications_query.count()
    pending_applications = applications_query.filter(Application.status == 'pending').count()
    accepted_applications = applications_query.filter(Application.status == 'accepted').count()
    rejected_applications = applications_query.filter(Application.status == 'rejected').count()
    applications_this_week = _apply_date_range(_filtered_application_query(), Application.created_at, week_start, end_dt).count()

    # Message stats
    message_query = _apply_date_range(Message.query, Message.created_at, start_dt, end_dt)
    total_messages = message_query.count()
    messages_this_week = _apply_date_range(Message.query, Message.created_at, week_start, end_dt).count()

    # Rating stats
    rating_query = _apply_date_range(Rating.query, Rating.created_at, start_dt, end_dt)
    total_ratings = rating_query.count()
    avg_rating = rating_query.with_entities(func.avg(Rating.rating)).scalar() or 0
    ratings_this_week = _apply_date_range(Rating.query, Rating.created_at, week_start, end_dt).count()

    # Top creators and applicants
    top_post_creators_query = db.session.query(
        User.full_name,
        User.email,
        func.count(TevkilPost.id).label('post_count')
    ).join(TevkilPost, TevkilPost.user_id == User.id)
    for condition in post_conditions:
        top_post_creators_query = top_post_creators_query.filter(condition)
    top_post_creators = _apply_date_range(
        top_post_creators_query, TevkilPost.created_at, start_dt, end_dt
    ).group_by(User.id).order_by(func.count(TevkilPost.id).desc()).limit(10).all()

    top_applicants_query = db.session.query(
        User.full_name,
        User.email,
        func.count(Application.id).label('application_count')
    ).join(Application, Application.applicant_id == User.id)
    if post_conditions:
        top_applicants_query = top_applicants_query.join(TevkilPost, Application.post_id == TevkilPost.id)
        for condition in post_conditions:
            top_applicants_query = top_applicants_query.filter(condition)
    top_applicants = _apply_date_range(
        top_applicants_query, Application.created_at, start_dt, end_dt
    ).group_by(User.id).order_by(func.count(Application.id).desc()).limit(10).all()

    # Report stats
    total_reports = 0
    pending_reports = 0
    pending_reports_list = []
    report_table_available = True
    try:
        reports_query = _apply_date_range(Report.query, Report.created_at, start_dt, end_dt)
        total_reports = reports_query.count()
        pending_reports_query = reports_query.filter(Report.status == 'pending')
        pending_reports = pending_reports_query.count()
        pending_reports_list = pending_reports_query.order_by(Report.created_at.desc()).limit(10).all()
    except ProgrammingError as exc:
        db.session.rollback()
        current_app.logger.warning('Report tablosu bulunamadı: %s', exc)
        report_table_available = False

    # Filter summary
    filter_summary_parts = []
    if filters.get('start_date'):
        filter_summary_parts.append(f"Başlangıç: {filters['start_date']}")
    if filters.get('end_date'):
        display_end = filters['end_date']
        filter_summary_parts.append(f"Bitiş: {display_end}")
    if city:
        filter_summary_parts.append(f"Şehir: {city}")
    if category:
        filter_summary_parts.append(f"Kategori: {category}")

    return {
        'total_users': total_users,
        'active_users_week': active_users_week,
        'active_users_month': active_users_month,
        'new_users_week': new_users_week,
        'new_users_month': new_users_month,
        'user_registrations_by_month': user_registrations_by_month,
        'total_posts': total_posts,
        'active_posts': active_posts,
        'completed_posts': completed_posts,
        'cancelled_posts': cancelled_posts,
        'posts_this_week': posts_this_week,
        'posts_this_month': posts_this_month,
        'posts_by_category': posts_by_category,
        'posts_by_city': posts_by_city,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'accepted_applications': accepted_applications,
        'rejected_applications': rejected_applications,
        'applications_this_week': applications_this_week,
        'total_messages': total_messages,
        'messages_this_week': messages_this_week,
        'total_ratings': total_ratings,
        'avg_rating': avg_rating,
        'ratings_this_week': ratings_this_week,
        'top_post_creators': top_post_creators,
        'top_applicants': top_applicants,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'pending_reports_list': pending_reports_list,
        'report_table_available': report_table_available,
        'filter_summary': ', '.join(filter_summary_parts) if filter_summary_parts else '',
    }
