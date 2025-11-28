"""
Admin Blueprint Routes - Admin panel with analytics and user management
"""
from flask import render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from datetime import datetime, timezone
from io import StringIO
import csv

from blueprints.admin import admin_bp
from blueprints.decorators import admin_required
from blueprints.admin.helpers import _parse_analytics_filters, _gather_analytics_stats
from models import db, User, Report
from constants import CITIES
from utils.logger import get_logger
import security_utils

logger = get_logger(__name__)

# POST_CATEGORIES constant (temporary - should be in constants.py)
POST_CATEGORIES = [
    'baro_kayit', 'baro_sorgulama', 'dilekce_alma', 'durusma_takibi',
    'evrak_teslim', 'ifade_tutanak', 'icra_takip', 'mudurluk_islem',
    'noter_islem', 'sahitlik', 'sozlesmeler', 'tercume', 'diger'
]


@admin_bp.route('/analytics')
@admin_required
def analytics():
    """Admin analytics dashboard with filtering"""
    filters = _parse_analytics_filters(request.args)
    stats = _gather_analytics_stats(filters)

    template_filters = {
        'start_date': filters.get('start_date'),
        'end_date': filters.get('end_date'),
        'city': filters.get('city'),
        'category': filters.get('category'),
        'has_active': filters.get('has_active'),
    }

    user_registrations = stats.get('user_registrations_by_month') or []
    user_registration_labels = [
        f"{int(row.year)}-{int(row.month):02d}" for row in user_registrations
    ]
    user_registration_counts = [int(row.count) for row in user_registrations]

    category_rows = stats.get('posts_by_category') or []
    category_labels = [(row.category or 'Belirtilmemiş') for row in category_rows]
    category_counts = [int(row.count) for row in category_rows]

    city_rows = stats.get('posts_by_city') or []
    city_labels = [(row.city or 'Belirtilmemiş') for row in city_rows]
    city_counts = [int(row.count) for row in city_rows]

    post_status_counts = [
        int(stats.get('active_posts') or 0),
        int(stats.get('completed_posts') or 0),
        int(stats.get('cancelled_posts') or 0),
    ]

    context = {
        **stats,
        'avg_rating': round(stats.get('avg_rating') or 0, 2),
        'filters': template_filters,
        'filter_query_params': filters.get('query_params', {}),
        'cities': CITIES,
        'categories': POST_CATEGORIES,
        'user_registration_labels': user_registration_labels,
        'user_registration_counts': user_registration_counts,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'city_labels': city_labels,
        'city_counts': city_counts,
        'post_status_counts': post_status_counts,
    }

    context['analytics_chart_data'] = {
        'user_registration_labels': user_registration_labels,
        'user_registration_counts': user_registration_counts,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'city_labels': city_labels,
        'city_counts': city_counts,
        'post_status_counts': post_status_counts,
    }

    return render_template('phoenix/admin/dashboard.html', **context)


@admin_bp.route('/analytics/export')
@admin_required
def export_analytics():
    """Export analytics data as CSV"""
    filters = _parse_analytics_filters(request.args)
    stats = _gather_analytics_stats(filters)

    output = StringIO()
    writer = csv.writer(output)

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    writer.writerow(['Analytics Report', timestamp])
    if stats.get('filter_summary'):
        writer.writerow(['Filters', stats['filter_summary']])
    elif filters.get('has_active'):
        query_params = filters.get('query_params', {})
        joined_filters = ', '.join(
            f"{key}={value}" for key, value in query_params.items()
        )
        writer.writerow(['Filters', joined_filters])
    writer.writerow([])

    writer.writerow(['User Statistics'])
    writer.writerow(['Total Users', stats['total_users']])
    writer.writerow(['Active (7 days)', stats['active_users_week']])
    writer.writerow(['Active (30 days)', stats['active_users_month']])
    writer.writerow(['New (7 days)', stats['new_users_week']])
    writer.writerow(['New (30 days)', stats['new_users_month']])
    writer.writerow([])

    writer.writerow(['Post Statistics'])
    writer.writerow(['Total Posts', stats['total_posts']])
    writer.writerow(['Active Posts', stats['active_posts']])
    writer.writerow(['Completed Posts', stats['completed_posts']])
    writer.writerow(['Cancelled Posts', stats['cancelled_posts']])
    writer.writerow(['Posts (7 days)', stats['posts_this_week']])
    writer.writerow(['Posts (30 days)', stats['posts_this_month']])
    writer.writerow([])

    writer.writerow(['Application Statistics'])
    writer.writerow(['Total Applications', stats['total_applications']])
    writer.writerow(['Pending Applications', stats['pending_applications']])
    writer.writerow(['Accepted Applications', stats['accepted_applications']])
    writer.writerow(['Rejected Applications', stats['rejected_applications']])
    writer.writerow(['Applications (7 days)', stats['applications_this_week']])
    writer.writerow([])

    writer.writerow(['Messaging'])
    writer.writerow(['Total Messages', stats['total_messages']])
    writer.writerow(['Messages (7 days)', stats['messages_this_week']])
    writer.writerow([])

    avg_rating_value = stats.get('avg_rating') or 0
    writer.writerow(['Ratings'])
    writer.writerow(['Total Ratings', stats['total_ratings']])
    writer.writerow(['Average Rating', round(float(avg_rating_value), 2)])
    writer.writerow(['Ratings (7 days)', stats['ratings_this_week']])
    writer.writerow([])

    writer.writerow(['Reports'])
    writer.writerow(['Total Reports', stats['total_reports']])
    writer.writerow(['Pending Reports', stats['pending_reports']])

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = (
        f'attachment; filename=analytics_export_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.csv'
    )
    response.headers['Content-Type'] = 'text/csv'

    security_utils.log_security_event(
        current_user.id,
        'admin_export_analytics',
        description='Analytics CSV export oluşturuldu',
        metadata={'filters': filters.get('query_params', {})}
    )

    return response


@admin_bp.route('/users')
@admin_required
def users():
    """User management panel"""
    # Filters
    search = request.args.get('search', '').strip()
    city = request.args.get('city', '').strip()
    bar_association = request.args.get('bar_association', '').strip()
    status = request.args.get('status', '').strip()
    verified = request.args.get('verified', '').strip()
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Base query
    query = User.query
    
    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term),
                User.phone.ilike(search_term),
                User.bar_registration_number.ilike(search_term)
            )
        )
    
    # City filter
    if city:
        query = query.filter(User.city == city)
    
    # Bar filter
    if bar_association:
        query = query.filter(User.bar_association == bar_association)
    
    # Status filter
    if status == 'active':
        query = query.filter(User.is_active == True)
    elif status == 'inactive':
        query = query.filter(User.is_active == False)
    
    # Verification filter
    if verified == 'yes':
        query = query.filter(User.verified == True)
    elif verified == 'no':
        query = query.filter(User.verified == False)
    
    # Sorting
    if sort_by == 'name':
        order_col = User.full_name
    elif sort_by == 'email':
        order_col = User.email
    elif sort_by == 'city':
        order_col = User.city
    elif sort_by == 'rating':
        order_col = User.rating_average
    elif sort_by == 'total_jobs':
        order_col = User.total_jobs
    else:
        order_col = User.created_at
    
    if order == 'asc':
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users_list = pagination.items
    
    # Stats
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    verified_users = User.query.filter_by(verified=True).count()
    admin_users_count = User.query.filter_by(is_admin=True).count()
    
    # Unique bar associations
    bar_associations = db.session.query(User.bar_association).distinct().filter(
        User.bar_association.isnot(None),
        User.bar_association != ''
    ).all()
    bar_associations = sorted([b[0] for b in bar_associations])
    
    return render_template('phoenix/admin/users.html',
                         users=users_list,
                         pagination=pagination,
                         search=search,
                         city=city,
                         bar_association=bar_association,
                         status=status,
                         verified=verified,
                         sort_by=sort_by,
                         order=order,
                         cities=CITIES,
                         bar_associations=bar_associations,
                         total_users=total_users,
                         active_users=active_users,
                         verified_users=verified_users,
                         admin_users=admin_users_count)


@admin_bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """User detail page"""
    user = User.query.get_or_404(user_id)
    return render_template('admin_user_detail.html', user=user)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    if user.is_admin and user.id != current_user.id:
        flash('Diğer admin kullanıcılarının durumunu değiştiremezsiniz.', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status_text = 'aktif' if user.is_active else 'pasif'
    flash(f'Kullanıcı durumu {status_text} olarak güncellendi.', 'success')
    
    security_utils.log_security_event(
        current_user.id,
        'admin_toggle_user_status',
        description=f'Kullanıcı {user_id} durumu değiştirildi: {status_text}',
        metadata={'user_id': user_id, 'new_status': user.is_active}
    )
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/verify', methods=['POST'])
@admin_required
def verify_user(user_id):
    """Verify user"""
    user = User.query.get_or_404(user_id)
    
    user.verified = True
    user.verified_at = datetime.now(timezone.utc)
    db.session.commit()
    
    flash('Kullanıcı başarıyla doğrulandı.', 'success')
    
    security_utils.log_security_event(
        current_user.id,
        'admin_verify_user',
        description=f'Kullanıcı {user_id} doğrulandı',
        metadata={'user_id': user_id}
    )
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/reports/<int:report_id>/update', methods=['POST'])
@admin_required
def update_report(report_id):
    """Update report status"""
    report = Report.query.get_or_404(report_id)
    
    new_status = request.form.get('status')
    admin_notes = request.form.get('admin_notes', '')
    
    if new_status not in ['pending', 'reviewed', 'resolved', 'dismissed']:
        flash('Geçersiz durum.', 'error')
        return redirect(url_for('admin.analytics'))
    
    report.status = new_status
    report.admin_notes = admin_notes
    report.reviewed_by = current_user.id
    report.reviewed_at = datetime.now(timezone.utc)
    db.session.commit()
    
    flash('Rapor güncellendi.', 'success')
    
    security_utils.log_security_event(
        current_user.id,
        'admin_update_report',
        description=f'Rapor {report_id} güncellendi',
        metadata={'report_id': report_id, 'new_status': new_status}
    )
    
    return redirect(url_for('admin.analytics'))
