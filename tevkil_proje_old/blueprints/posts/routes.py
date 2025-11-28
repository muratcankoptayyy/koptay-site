"""
Posts Blueprint Routes - Post listing, creation, editing, deletion
"""
from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from sqlalchemy import or_

from blueprints.posts import posts_bp
from blueprints.decorators import dev_login_optional
from blueprints.helpers import (
    generate_post_title,
    update_post_view, get_post_stats
)
from geocoding_service import get_coordinates
from models import db, TevkilPost, Application, Favorite
from constants import CITIES, COURTHOUSES, TASK_CATEGORY_OPTIONS, TASK_CATEGORY_DEFINITIONS, CATEGORY_ABBREVIATIONS

# Temporary - should be moved to constants.py
TASK_CATEGORY_LABELS = {
    'baro_kayit': 'Baro Kayıt',
    'baro_sorgulama': 'Baro Sorgulama',
    'dilekce_alma': 'Dilekçe Alma',
    'durusma_takibi': 'Duruşma Takibi',
    'evrak_teslim': 'Evrak Teslim',
    'ifade_tutanak': 'İfade/Tutanak',
    'icra_takip': 'İcra Takip',
    'mudurluk_islem': 'Müdürlük İşlem',
    'noter_islem': 'Noter İşlem',
    'sahitlik': 'Şahitlik',
    'sozlesmeler': 'Sözleşmeler',
    'tercume': 'Tercüme',
    'diger': 'Diğer'
}


@posts_bp.route('/')
@dev_login_optional
def list_posts():
    """İlan listesi - Gelişmiş Filtreleme"""
    # Filters
    user_filter = request.args.get('filter')
    filter_type = request.args.get('filter_type', 'all')
    category = request.args.get('category')
    city = request.args.get('city')
    urgency = request.args.get('urgency')
    search = request.args.get('search')

    # Advanced Filters
    price_min = request.args.get('price_min', type=int)
    price_max = request.args.get('price_max', type=int)
    hearing_date_from = request.args.get('hearing_date_from')
    hearing_date_to = request.args.get('hearing_date_to')
    urgent_only = request.args.get('urgent_only') in ('1', 'on', 'true', 'True')
    remote_allowed = request.args.get('remote_allowed') in ('1', 'on', 'true', 'True')

    now = datetime.now(timezone.utc)

    # Base query
    if user_filter == 'my_active':
        query = TevkilPost.query.filter_by(user_id=current_user.id, status='active')
    elif user_filter == 'my_completed':
        query = TevkilPost.query.filter_by(user_id=current_user.id, status='completed')
    elif user_filter == 'my_all':
        query = TevkilPost.query.filter_by(user_id=current_user.id)
    else:
        query = TevkilPost.query.filter_by(status='active')
    
    # Basic filters
    if category:
        query = query.filter_by(category=category)
    if city:
        query = query.filter_by(city=city)
    if urgency:
        query = query.filter_by(urgency_level=urgency)
    if search:
        query = query.filter(or_(
            TevkilPost.title.ilike(f'%{search}%'),
            TevkilPost.description.ilike(f'%{search}%')
        ))
    
    # Price filters
    if price_min is not None:
        query = query.filter(TevkilPost.price_min >= price_min)
    if price_max is not None:
        query = query.filter(or_(
            TevkilPost.price_min <= price_max,
            TevkilPost.price_min.is_(None)
        ))
    
    # Date filters
    if hearing_date_from:
        try:
            from_date = datetime.strptime(hearing_date_from, '%Y-%m-%d')
            query = query.filter(TevkilPost.hearing_date >= from_date)
        except ValueError:
            pass
    
    if hearing_date_to:
        try:
            to_date = datetime.strptime(hearing_date_to, '%Y-%m-%d')
            query = query.filter(TevkilPost.hearing_date <= to_date)
        except ValueError:
            pass
    
    # Urgent only filter
    if urgent_only:
        query = query.filter(TevkilPost.urgency_level.in_(['urgent', 'very_urgent']))
    
    # Remote allowed filter
    if remote_allowed:
        query = query.filter_by(remote_allowed=True)
    
    # Order and paginate
    query = query.order_by(TevkilPost.created_at.desc())
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items
    
    # Create filter state for template
    filter_state = {
        'search': search,
        'city': city,
        'category': category,
        'urgency': urgency,
        'hearing_date_from': hearing_date_from,
        'hearing_date_to': hearing_date_to,
        'urgent_only': urgent_only,
        'remote_allowed': remote_allowed
    }
    
    return render_template('phoenix/posts/explore.html',
                         posts=posts,
                         pagination=pagination,
                         cities=CITIES,
                         category_labels=TASK_CATEGORY_LABELS,
                         filter_state=filter_state)


@posts_bp.route('/map')
@dev_login_optional
def map_view():
    """Harita görünümü"""
    import os
    
    posts = TevkilPost.query.filter_by(status='active').order_by(TevkilPost.created_at.desc()).all()
    
    posts_json = []
    for post in posts:
        if post.latitude and post.longitude:
            posts_json.append({
                'id': post.id,
                'title': post.title,
                'description': post.description[:100] + '...' if len(post.description) > 100 else post.description,
                'category': post.category,
                'urgency_level': post.urgency_level,
                'location': post.location,
                'formatted_address': post.formatted_address or post.location,
                'latitude': post.latitude,
                'longitude': post.longitude,
                'created_at': post.created_at.strftime('%d.%m.%Y'),
                'user_name': post.user.masked_full_name if post.user else 'Anonim'
            })
    
    google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    return render_template('phoenix/posts/map.html', 
                         posts=posts,
                         posts_json=posts_json,
                         google_maps_key=google_maps_key)


@posts_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_post():
    """Yeni ilan oluştur"""
    if request.method == 'POST':
        from spam_detector import is_spam, is_inappropriate, check_flood, sanitize_text
        
        data = request.form
        category = (data.get('category') or '').strip()
        description = data.get('description', '')
        task_date_raw = data.get('task_date')
        task_time_raw = data.get('task_time')
        city = (data.get('city') or '').strip()
        courthouse = (data.get('courthouse') or '').strip()
        district = (data.get('district') or '').strip()
        location_hidden = (data.get('location') or '').strip()

        if not category:
            flash('Görev türü seçmek zorunludur.', 'error')
            return redirect(url_for('posts.create_post'))

        if not task_date_raw or not task_time_raw:
            flash('Görev tarihi ve saatini belirtmelisınız.', 'error')
            return redirect(url_for('posts.create_post'))

        try:
            task_datetime = datetime.strptime(f"{task_date_raw} {task_time_raw}", '%Y-%m-%d %H:%M')
        except ValueError:
            flash('Görev tarihi veya saati geçersiz. Lütfen formatı kontrol edin.', 'error')
            return redirect(url_for('posts.create_post'))

        auto_title = generate_post_title(category, city=city, courthouse=courthouse, district=district)
        
        # SPAM checks
        if is_spam(auto_title) or is_spam(description):
            flash('İlanınız spam içerik tespit edildiği için oluşturulamadı.', 'danger')
            return redirect(url_for('posts.create_post'))
        
        if is_inappropriate(auto_title) or is_inappropriate(description):
            flash('İlanınız uygunsuz içerik tespit edildiği için oluşturulamadı.', 'danger')
            return redirect(url_for('posts.create_post'))
        
        if check_flood(current_user.id, db.session, action_type='post', max_count=5, time_window_minutes=60):
            flash('Çok fazla ilan oluşturdunuz. Lütfen bir süre bekleyin.', 'warning')
            return redirect(url_for('main.dashboard'))
        
        # Sanitize
        description = sanitize_text(description, max_length=5000)
        auto_title = sanitize_text(auto_title, max_length=200)
        category = sanitize_text(category, max_length=50)
        city = sanitize_text(city, max_length=50) if city else None
        district = sanitize_text(district, max_length=100) if district else None
        courthouse = sanitize_text(courthouse, max_length=150) if courthouse else None
        
        # Geocode location
        primary_location = courthouse or (f"{district} {city}".strip() if district and city else district) or city or location_hidden
        location_str = primary_location or location_hidden
        coords = get_coordinates(location_str) if location_str else {}
        
        price_raw = data.get('price')
        price_value = float(price_raw) if price_raw else None

        post = TevkilPost(
            user_id=current_user.id,
            title=auto_title,
            description=description,
            category=category,
            urgency_level=data.get('urgency_level', 'normal'),
            location=location_str,
            city=city,
            district=district,
            courthouse=courthouse,
            remote_allowed=data.get('remote_allowed') == 'on',
            price_min=price_value,
            price_max=price_value,
            court_date=task_datetime,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            latitude=coords.get('latitude'),
            longitude=coords.get('longitude'),
            formatted_address=coords.get('formatted_address')
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('İlan başarıyla oluşturuldu!', 'success')
        return redirect(url_for('posts.post_detail', post_id=post.id))
    
    return render_template('phoenix/posts/create.html',
                         cities=CITIES,
                         courthouses=COURTHOUSES,
                         task_category_options=TASK_CATEGORY_OPTIONS,
                         category_definitions=TASK_CATEGORY_DEFINITIONS,
                         category_abbreviations=CATEGORY_ABBREVIATIONS)


@posts_bp.route('/<int:post_id>')
def post_detail(post_id):
    """İlan detayı - See routes_detail.py"""
    from blueprints.posts.routes_detail import post_detail_view
    return post_detail_view(post_id)


@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """İlan düzenle"""
    post = TevkilPost.query.get_or_404(post_id)
    
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    if request.method == 'POST':
        data = request.form
        post.description = data.get('description', post.description)
        post.urgency_level = data.get('urgency_level', post.urgency_level)
        post.remote_allowed = data.get('remote_allowed') == 'on'
        
        price_raw = data.get('price')
        if price_raw:
            price_value = float(price_raw)
            post.price_min = price_value
            post.price_max = price_value
        
        db.session.commit()
        flash('İlan başarıyla güncellendi!', 'success')
        return redirect(url_for('posts.post_detail', post_id=post.id))
    
    return render_template('phoenix/posts/edit.html', 
                         post=post,
                         task_category_options=TASK_CATEGORY_OPTIONS)


@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """İlan sil"""
    post = TevkilPost.query.get_or_404(post_id)
    
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    
    flash('İlan başarıyla silindi.', 'success')
    return redirect(url_for('posts.list_posts'))


@posts_bp.route('/<int:post_id>/apply', methods=['POST'])
@login_required
def apply_to_post(post_id):
    """İlana başvur"""
    from blueprints.helpers import create_notification
    import os
    
    post = TevkilPost.query.get_or_404(post_id)
    
    if post.user_id == current_user.id:
        flash('Kendi ilanınıza başvuramazsınız.', 'error')
        return redirect(url_for('posts.post_detail', post_id=post_id))
    
    existing = Application.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if existing:
        flash('Bu ilana zaten başvurdunuz.', 'warning')
        return redirect(url_for('posts.post_detail', post_id=post_id))
    
    application = Application(
        post_id=post_id,
        user_id=current_user.id,
        status='pending'
    )
    db.session.add(application)
    db.session.commit()
    
    # Notification
    create_notification(
        user_id=post.user_id,
        notification_type='new_application',
        title='Yeni Başvuru',
        message=f'{current_user.masked_full_name} ilanınıza başvurdu.',
        related_post_id=post_id,
        related_user_id=current_user.id,
        action_url=url_for('applications.received'),
        action_text='Başvuruları Gör'
    )
    
    flash('Başvurunuz gönderildi!', 'success')
    return redirect(url_for('posts.post_detail', post_id=post_id))
