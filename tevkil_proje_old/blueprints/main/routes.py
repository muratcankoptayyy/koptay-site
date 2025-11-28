#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main Blueprint Routes - Part 1: Dashboard & Homepage
Core routes for homepage, dashboard, and statistics
"""

import logging
from datetime import datetime, timezone, timedelta

from flask import render_template, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user

from models import db, TevkilPost, Application, Notification, Rating
from blueprints.main import main_bp

# DIAGNOSTIC ROUTE
@main_bp.route('/diagnostic')
def diagnostic():
    """Diagnostic test page"""
    from flask import current_app
    return render_template('diagnostic.html', now=datetime.now(), config=current_app.config)

# SIMPLE MESSAGES (NO ALPINE.JS)
@main_bp.route('/messages-simple')
@login_required
def simple_messages():
    """Simple messages page without Alpine.js"""
    from models import Message
    received = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.created_at.desc()).all()
    sent = Message.query.filter_by(sender_id=current_user.id).order_by(Message.created_at.desc()).all()
    unread_count = Message.query.filter_by(receiver_id=current_user.id, read_at=None).count()
    return render_template('simple_messages.html', received=received, sent=sent, unread_count=unread_count, datetime=datetime)

# TEMPORARY TEST ROUTE
@main_bp.route('/test-simple')
def test_simple():
    """Basit test sayfası - JavaScript olmadan"""
    return render_template('test_simple.html', now=datetime.now())
from blueprints.main.helpers import (
    get_user_stats,
    get_platform_stats,
    get_dashboard_metrics,
    get_chart_data,
    to_utc
)
from blueprints.decorators import dev_login_optional
from sqlalchemy import func

logger = logging.getLogger(__name__)


@main_bp.route('/')
def index():
    """Ana sayfa - Giriş yapmışsa dashboard'a yönlendir"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    recent_posts = TevkilPost.query.filter_by(status='active').order_by(TevkilPost.created_at.desc()).limit(6).all()
    return render_template('phoenix/static/home.html', posts=recent_posts)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Kullanıcı dashboard"""
    try:
        # Kullanıcının ilanları
        my_posts = TevkilPost.query.filter_by(user_id=current_user.id).order_by(TevkilPost.created_at.desc()).all()
        
        # Kullanıcının başvuruları
        my_applications = Application.query.filter_by(applicant_id=current_user.id).order_by(Application.created_at.desc()).all()
        
        # Gelen başvurular (kullanıcının ilanlarına)
        incoming_applications = db.session.query(Application).join(TevkilPost).filter(
            TevkilPost.user_id == current_user.id
        ).order_by(Application.created_at.desc()).all()
        
        # Okunmamış bildirimler
        unread_notifications = Notification.query.filter_by(user_id=current_user.id, read_at=None).count()
    except Exception as e:
        logger.error(f"❌ Dashboard error in initial queries: {str(e)}")
        flash('Dashboard yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Get helper data
        user_stats = get_user_stats(current_user.id) or {}
        metrics = get_dashboard_metrics(current_user.id)
        chart_data = get_chart_data(current_user.id, months=6)
        
        # Performance stats
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_completed = TevkilPost.query.filter(
            TevkilPost.user_id == current_user.id,
            TevkilPost.status == 'completed',
            TevkilPost.updated_at >= month_start
        ).count()
        
        # Tahmini toplam kazanç
        completed_posts = TevkilPost.query.filter_by(
            user_id=current_user.id,
            status='completed'
        ).all()
        total_earnings = sum(
            p.price_min for p in completed_posts if p.price_min is not None
        )
        
        # Ortalama rating
        ratings = Rating.query.filter_by(reviewed_id=current_user.id).all()
        avg_rating = sum([r.rating for r in ratings]) / len(ratings) if ratings else 0
        
        # Workflows (recent posts)
        status_labels = {
            'active': 'Aktif',
            'assigned': 'Atandı',
            'completed': 'Tamamlandı',
            'cancelled': 'İptal edildi',
        }
        status_variants = {
            'active': 'brand',
            'assigned': 'amber',
            'completed': 'emerald',
            'cancelled': 'slate',
        }
        
        workflows = []
        for post in sorted(my_posts, key=lambda item: to_utc(item.updated_at) or to_utc(item.created_at) or now, reverse=True)[:5]:
            deadline_source = post.deadline or post.court_date
            if deadline_source:
                deadline_text = (to_utc(deadline_source) or now).strftime('%d %b %Y')
            else:
                deadline_text = 'Takvimlenmedi'
            workflows.append({
                'title': post.title,
                'category': post.category,
                'city': post.city or post.location or 'Konum belirtilmedi',
                'status': status_labels.get(post.status, post.status.title()),
                'status_variant': status_variants.get(post.status, 'slate'),
                'deadline': deadline_text,
                'applications': post.applications_count or 0,
                'url': url_for('posts.post_detail', post_id=post.id),
            })
        
        # Upcoming hearings
        upcoming_posts = TevkilPost.query.filter(
            TevkilPost.user_id == current_user.id,
            TevkilPost.court_date.isnot(None),
            TevkilPost.court_date >= now
        ).order_by(TevkilPost.court_date.asc()).limit(4).all()
        
        hearings = []
        turkish_months = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']
        for item in upcoming_posts:
            court_dt = to_utc(item.court_date) or now
            hearings.append({
                'day': court_dt.strftime('%d'),
                'month': turkish_months[court_dt.month - 1],
                'time': court_dt.strftime('%H:%M'),
                'title': item.title,
                'location': item.courthouse or item.city or 'Mahkeme bilgisi yok',
                'url': url_for('posts.post_detail', post_id=item.id),
            })
        
        # Notifications feed
        notification_icon_map = {
            'new_application': 'inbox',
            'application_accepted': 'thumb_up',
            'application_rejected': 'thumb_down',
            'message': 'chat',
            'post_expiring': 'schedule',
            'system': 'notifications',
        }
        
        recent_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
            Notification.created_at.desc()
        ).limit(5).all()
        
        notifications_feed = []
        for notif in recent_notifications:
            created_at = to_utc(notif.created_at) or now
            notifications_feed.append({
                'icon': notification_icon_map.get(notif.type, 'notifications'),
                'title': notif.title or notif.message or 'Bildirim',
                'description': notif.message or '',
                'time': notif.time_ago if hasattr(notif, 'time_ago') else created_at.strftime('%d %b %Y %H:%M'),
                'url': notif.action_url,
                'is_new': getattr(notif, 'is_new', False),
            })
        
        # Activity timeline
        timeline_entries = []
        
        for post in my_posts[:5]:
            timeline_entries.append({
                'timestamp': to_utc(post.created_at) or now,
                'icon': 'add_circle',
                'variant': 'brand',
                'title': 'Yeni ilan oluşturdunuz',
                'description': post.title,
                'url': url_for('posts.post_detail', post_id=post.id),
            })
        
        for app_item in my_applications[:5]:
            timeline_entries.append({
                'timestamp': to_utc(app_item.created_at) or now,
                'icon': 'send',
                'variant': 'purple',
                'title': 'Başvuru yaptınız',
                'description': app_item.post.title if app_item.post else 'Bir ilana başvuru yapıldı',
                'url': url_for('posts.post_detail', post_id=app_item.post_id),
            })
        
        for incoming in incoming_applications[:5]:
            applicant_name = incoming.applicant.masked_full_name if incoming.applicant else 'Başvuru sahibi'
            timeline_entries.append({
                'timestamp': to_utc(incoming.created_at) or now,
                'icon': 'inbox',
                'variant': 'emerald',
                'title': 'Yeni başvuru aldınız',
                'description': f"{applicant_name} başvurdu",
                'url': url_for('applications.received'),
            })
        
        sorted_timeline = sorted(timeline_entries, key=lambda item: item['timestamp'], reverse=True)[:6]
        for entry in sorted_timeline:
            entry['time_display'] = entry['timestamp'].strftime('%d %b %Y, %H:%M')
        
        # Quick actions
        quick_actions = [
            {
                'label': 'Yeni ilan',
                'icon': 'add_circle',
                'url': url_for('posts.create_post'),
                'variant': 'brand',
            },
            {
                'label': 'İlan ara',
                'icon': 'search',
                'url': url_for('posts.list_posts'),
                'variant': 'emerald',
            },
            {
                'label': 'Mesajlar',
                'icon': 'forum',
                'url': url_for('chat.chat_index'),
                'variant': 'purple',
            },
            {
                'label': 'Harita',
                'icon': 'map',
                'url': url_for('posts.map_view'),
                'variant': 'amber',
            },
        ]
        
        # Dashboard stats
        completed_posts = sum(1 for post in my_posts if post.status == 'completed')
        pending_applications_count = sum(1 for app in my_applications if app.status == 'pending')
        
        dashboard_stats = {
            'rating_average': round(avg_rating or 0, 1) if avg_rating else 0,
            'rating_count': user_stats.get('rating_count', 0),
            'success_rate': user_stats.get('success_rate', 0),
            'completed_jobs': completed_posts,
            'avg_response': user_stats.get('average_response_time', 0),
            'active_applications': pending_applications_count,
        }
        
        return render_template(
            'phoenix/dashboard/overview.html',
            metrics=metrics,
            workflows=workflows,
            hearings=hearings,
            notifications_feed=notifications_feed,
            activity_timeline=sorted_timeline,
            quick_actions=quick_actions,
            stats=dashboard_stats,
            my_posts=my_posts,
            my_applications=my_applications,
            incoming_applications=incoming_applications,
            chart_months=chart_data['months'],
            chart_incoming=chart_data['incoming'],
            chart_outgoing=chart_data['outgoing'],
            category_labels=chart_data['category_labels'],
            category_counts=chart_data['category_counts'],
            monthly_completed=monthly_completed,
            total_earnings=total_earnings,
            avg_rating=avg_rating,
            unread_notifications=unread_notifications,
            unread_notif_count=unread_notifications,
            user_stats=user_stats,
        )
    except Exception as e:
        logger.error(f"❌ Dashboard error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Minimal dashboard göster
        return render_template('phoenix/dashboard/overview.html',
                             metrics=[],
                             workflows=[],
                             hearings=[],
                             notifications_feed=[],
                             activity_timeline=[],
                             quick_actions=[],
                             stats={},
                             my_posts=my_posts,
                             my_applications=my_applications,
                             incoming_applications=incoming_applications,
                             unread_notifications=unread_notifications,
                             unread_notif_count=unread_notifications,
                             chart_months=[],
                             chart_incoming=[],
                             chart_outgoing=[],
                             category_labels=[],
                             category_counts=[],
                             monthly_completed=0,
                             total_earnings=0,
                             avg_rating=0,
                             user_stats={})


@main_bp.route('/stats')
@dev_login_optional
def stats_page():
    """Detaylı istatistikler sayfası"""
    # Kullanıcı istatistikleri
    user_stats = get_user_stats(current_user.id)
    
    # Platform istatistikleri (admin için tüm platform)
    platform_stats = get_platform_stats() if current_user.is_admin else None
    
    # Son 30 günlük aktivite grafiği
    now = datetime.now(timezone.utc)
    daily_stats = []
    
    for i in range(29, -1, -1):  # Son 30 gün
        day_date = now - timedelta(days=i)
        day_start = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        # O günkü yeni ilanlar
        posts_count = TevkilPost.query.filter(
            TevkilPost.user_id == current_user.id,
            TevkilPost.created_at >= day_start,
            TevkilPost.created_at < day_end
        ).count()
        
        # O günkü başvurular
        applications_count = Application.query.filter(
            Application.applicant_id == current_user.id,
            Application.created_at >= day_start,
            Application.created_at < day_end
        ).count()
        
        # O günkü görüntülenmeler
        views_count = db.session.query(func.sum(TevkilPost.view_count)).filter(
            TevkilPost.user_id == current_user.id,
            TevkilPost.last_viewed_at >= day_start,
            TevkilPost.last_viewed_at < day_end
        ).scalar() or 0
        
        daily_stats.append({
            'date': day_start.strftime('%d %b'),
            'posts': posts_count,
            'applications': applications_count,
            'views': int(views_count),
        })
    
    return render_template(
        'phoenix/stats.html',
        user_stats=user_stats,
        platform_stats=platform_stats,
        daily_stats=daily_stats
    )


# ============================================
# PROFILE & SETTINGS ROUTES
# ============================================

@main_bp.route('/profile/<int:user_id>')
def user_profile(user_id):
    """Kullanıcı profili"""
    from models import User
    user = User.query.get_or_404(user_id)
    
    # Kullanıcının tamamladığı işler
    completed_posts = TevkilPost.query.filter_by(assigned_to=user_id, status='completed').all()
    
    # Aldığı değerlendirmeler
    ratings = Rating.query.filter_by(reviewed_id=user_id).order_by(Rating.created_at.desc()).all()
    
    return render_template('phoenix/profile/view.html', user=user, completed_posts=completed_posts, ratings=ratings)


@main_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Profil düzenle"""
    from flask import request
    from models import User
    
    if request.method == 'POST':
        data = request.form
        
        # Bar registration uniqueness check
        new_bar_assoc = data.get('bar_association')
        new_bar_reg_num = data.get('bar_registration_number')
        
        if new_bar_assoc and new_bar_reg_num:
            if (new_bar_assoc != current_user.bar_association or 
                new_bar_reg_num != current_user.bar_registration_number):
                existing_user = User.query.filter(
                    User.id != current_user.id,
                    User.bar_association == new_bar_assoc,
                    User.bar_registration_number == new_bar_reg_num
                ).first()
                
                if existing_user:
                    flash(f'{new_bar_assoc} - {new_bar_reg_num} sicil numarası ile zaten kayıtlı başka bir kullanıcı var', 'error')
                    return redirect(url_for('main.edit_profile'))
        
        current_user.full_name = data.get('full_name')
        current_user.phone = data.get('phone')
        current_user.whatsapp_number = data.get('whatsapp_number')
        current_user.tc_number = data.get('tc_number')
        current_user.bar_association = new_bar_assoc
        current_user.bar_registration_number = new_bar_reg_num
        current_user.city = data.get('city')
        current_user.district = data.get('district')
        current_user.bio = data.get('bio')
        current_user.specializations = data.get('specializations', '').split(',') if data.get('specializations') else []
        current_user.avatar_url = data.get('avatar_url') if data.get('avatar_url') else None
        current_user.linkedin_url = data.get('linkedin_url') if data.get('linkedin_url') else None
        current_user.twitter_url = data.get('twitter_url') if data.get('twitter_url') else None
        current_user.instagram_url = data.get('instagram_url') if data.get('instagram_url') else None
        current_user.website_url = data.get('website_url') if data.get('website_url') else None
        
        if current_user.is_admin and data.get('lawyer_type'):
            current_user.lawyer_type = data.get('lawyer_type')
        
        db.session.commit()
        flash('Profil güncellendi!', 'success')
        return redirect(url_for('main.user_profile', user_id=current_user.id))
    
    return render_template('phoenix/profile/edit.html')


@main_bp.route('/settings')
@login_required
def settings():
    """Ayarlar sayfası"""
    two_fa_enabled = current_user.two_factor_enabled
    backup_codes = []
    if current_user.two_factor_backup_codes:
        import json
        try:
            backup_codes = json.loads(current_user.two_factor_backup_codes)
        except:
            backup_codes = []
    
    return render_template('settings.html', 
                         two_fa_enabled=two_fa_enabled,
                         backup_codes=backup_codes)


# ============================================
# FAVORITES ROUTES
# ============================================

@main_bp.route('/favorites')
@login_required
def favorites():
    """Favoriler sayfası"""
    from models import Favorite
    
    favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc()).all()
    posts = [fav.post for fav in favorites if fav.post]
    
    return render_template('phoenix/favorites.html', posts=posts)


@main_bp.route('/favorites/toggle/<int:post_id>', methods=['POST'])
@login_required
def toggle_favorite(post_id):
    """Favori ekle/çıkar"""
    from models import Favorite
    
    post = TevkilPost.query.get_or_404(post_id)
    existing_fav = Favorite.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if existing_fav:
        db.session.delete(existing_fav)
        db.session.commit()
        return jsonify({'success': True, 'action': 'removed', 'message': 'Favorilerden kaldırıldı'})
    else:
        fav = Favorite(user_id=current_user.id, post_id=post_id)
        db.session.add(fav)
        db.session.commit()
        return jsonify({'success': True, 'action': 'added', 'message': 'Favorilere eklendi'})


# ============================================
# LEGAL & PWA ROUTES
# ============================================

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('phoenix/static/contact.html')


@main_bp.route('/privacy-policy')
def privacy_policy():
    """Privacy policy page (KVKK compliance)"""
    return render_template('phoenix/static/legal/privacy_policy.html', current_date='2025')


@main_bp.route('/terms-of-service')
def terms_of_service():
    """Terms of service page"""
    return render_template('phoenix/static/legal/terms_of_service.html', current_date='2025')


@main_bp.route('/cookie-policy')
def cookie_policy():
    """Cookie policy page"""
    return render_template('phoenix/static/legal/cookie_policy.html', current_date='2025')


@main_bp.route('/health')
@main_bp.route('/healthz')
def health_check():
    """Health check endpoint"""
    from sqlalchemy import text
    from flask import current_app
    
    try:
        db.session.execute(text('SELECT 1'))
        db.session.rollback()
    except Exception as exc:
        current_app.logger.error('Health check failed: %s', exc)
        db.session.rollback()
        return jsonify({'status': 'unhealthy', 'detail': str(exc)}), 500

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200


@main_bp.route('/manifest.json')
def manifest():
    """PWA manifest"""
    from flask import send_from_directory, current_app
    return send_from_directory(current_app.static_folder, 'manifest.json')


@main_bp.route('/service-worker.js')
def service_worker():
    """Service worker"""
    from flask import send_from_directory, current_app
    return send_from_directory(current_app.static_folder, 'service-worker.js')


# ============================================
# MESSAGES ROUTES
# ============================================

@main_bp.route('/messages')
@login_required
def messages():
    """Mesajlar sayfası"""
    from models import Message
    
    # Gelen mesajlar
    received = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.created_at.desc()).all()
    
    # Gönderilen mesajlar
    sent = Message.query.filter_by(sender_id=current_user.id).order_by(Message.created_at.desc()).all()
    
    # Okunmamış mesaj sayısı
    unread_count = Message.query.filter_by(receiver_id=current_user.id, read_at=None).count()
    
    return render_template('messages.html', 
                         received=received, 
                         sent=sent, 
                         unread_count=unread_count)


@main_bp.route('/messages/send/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def send_message(receiver_id):
    """Mesaj gönder"""
    from flask import request
    from models import Message, User
    
    receiver = User.query.get_or_404(receiver_id)
    
    if request.method == 'POST':
        content = request.form.get('content')
        subject = request.form.get('subject', 'Konu Yok')
        
        if content:
            message = Message(
                sender_id=current_user.id,
                receiver_id=receiver_id,
                subject=subject,
                content=content
            )
            db.session.add(message)
            db.session.commit()
            
            flash('Mesajınız gönderildi!', 'success')
            return redirect(url_for('main.messages'))
        else:
            flash('Mesaj içeriği boş olamaz!', 'error')
    
    return render_template('send_message.html', receiver=receiver)


@main_bp.route('/messages/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Mesajı okundu olarak işaretle"""
    from models import Message
    
    message = Message.query.get_or_404(message_id)
    
    if message.receiver_id != current_user.id:
        abort(403)
    
    if not message.read_at:
        message.read_at = datetime.now(timezone.utc)
        db.session.commit()
    
    return jsonify({'success': True})




# ============================================
# EXPLORE / POSTS LIST ROUTES
# ============================================

@main_bp.route('/explore')
@login_required
def explore():
    """İlanları keşfet sayfası"""
    from flask import request
    
    # Filtreler
    category = request.args.get('category', None)
    city = request.args.get('city', None)
    status = request.args.get('status', 'active')
    search = request.args.get('search', None)
    
    # Query
    query = TevkilPost.query
    
    if category:
        query = query.filter_by(category=category)
    if city:
        query = query.filter_by(city=city)
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(TevkilPost.title.ilike(f'%{search}%'))
    
    # Sıralama
    posts = query.order_by(TevkilPost.created_at.desc()).all()
    
    # Constants
    from constants import CITIES, POST_CATEGORIES
    
    filter_state = {
        'category': category,
        'city': city,
        'status': status,
        'search': search
    }
    
    return render_template('posts_list.html', 
                         posts=posts, 
                         cities=CITIES,
                         categories=POST_CATEGORIES,
                         filter_state=filter_state)


# ============================================
# APPLICATIONS ROUTES
# ============================================

@main_bp.route('/applications/sent')
@login_required
def applications_sent():
    """Gönderilen başvurular"""
    applications = Application.query.filter_by(applicant_id=current_user.id).order_by(Application.created_at.desc()).all()
    return render_template('applications_sent.html', applications=applications)


@main_bp.route('/applications/received')
@login_required
def applications_received():
    """Gelen başvurular"""
    # Kullanıcının ilanlarına gelen başvurular
    applications = db.session.query(Application).join(TevkilPost).filter(
        TevkilPost.user_id == current_user.id
    ).order_by(Application.created_at.desc()).all()
    
    return render_template('applications_received.html', applications=applications)
