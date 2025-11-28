"""
Tevkil Platform - Main Application
Avukatlar arası iş devri ve tevkil platformu
"""
import os
from dotenv import load_dotenv

# Load environment variables early so that config import sees them
load_dotenv()
from datetime import datetime, timedelta, timezone
from flask import request, jsonify, render_template, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import emit, join_room, leave_room, send
from flask_wtf.csrf import generate_csrf
from werkzeug.utils import secure_filename
from models import db, User, TevkilPost, Application, Rating, Message, Notification, Favorite, PasswordReset, Conversation, Report, mask_name, DeviceToken
from models import UserSession, SecurityLog, PasswordHistory, LoginAttempt
from sqlalchemy import or_, and_, func
import secrets
from constants import (
    CITIES,
    COURTHOUSES,
    POST_CATEGORIES,
    BAR_ASSOCIATIONS,
    TASK_CATEGORY_DEFINITIONS,
    TASK_CATEGORY_OPTIONS,
    CATEGORY_ABBREVIATIONS,
)
from functools import wraps
import security_utils
import input_validation
from tevkil.app_factory import create_app
from tevkil.extensions import csrf, limiter, login_manager, socketio
from utils.logger import get_logger
from utils.error_handlers import register_error_handlers
from blueprints import register_blueprints

# Initialize Flask app via factory
app = create_app()

# Initialize logger
logger = get_logger(__name__)

# Register global error handlers
register_error_handlers(app)

# Register all blueprints
register_blueprints(app)
logger.info("Application initialized with blueprints")

# =============================================================================
# MAINTENANCE MODE - Temporarily redirect all traffic to coming soon page
# =============================================================================
MAINTENANCE_MODE = True  # Set to False to restore normal operation

@app.before_request
def check_maintenance_mode():
    """Redirect all requests to maintenance page when in maintenance mode"""
    if MAINTENANCE_MODE:
        # Allow static files to load (CSS, JS, images, logo)
        if request.path.startswith('/static/'):
            return None
        # Show maintenance page for all other routes
        if request.path != '/maintenance':
            return render_template('maintenance.html'), 503
    return None

@app.route('/maintenance')
def maintenance_page():
    """Dedicated maintenance page route"""
    return render_template('maintenance.html'), 503

# Disable CSP in development mode
@app.after_request
def disable_csp_in_dev(response):
    """Development mode: Remove Content Security Policy to allow JavaScript execution"""
    if app.config.get('DEV_MODE'):
        # Remove any CSP headers that might be set
        response.headers.pop('Content-Security-Policy', None)
        response.headers.pop('Content-Security-Policy-Report-Only', None)
        # Add permissive CSP for development
        response.headers['Content-Security-Policy'] = "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:; script-src * 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline';"
        logger.debug("🔓 DEV MODE: CSP disabled for JavaScript execution")
    return response

TASK_CATEGORY_LABELS = {
    key: value.get('label', key.replace('_', ' ').title())
    for key, value in TASK_CATEGORY_DEFINITIONS.items()
}

# Development Mode: Login bypass decorator
def dev_login_optional(f):
    """Geliştirme modunda login zorunluluğunu kaldırır"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if app.config['DEV_MODE']:
            # Geliştirme modunda: Eğer kullanıcı login değilse, ilk kullanıcıyı otomatik login yap
            if not current_user.is_authenticated:
                first_user = User.query.first()
                if first_user:
                    login_user(first_user, remember=True)
                    logger.info(f"🔓 DEV MODE: Auto-logged in as {first_user.email}")
            return f(*args, **kwargs)
        else:
            # Production modunda: Normal login_required davranışı
            return login_required(f)(*args, **kwargs)
    return decorated_function


def generate_post_title(category: str, city: str | None = None, courthouse: str | None = None, district: str | None = None) -> str:
    """Kategori kısaltmasını ve görev yerini kullanarak otomatik başlık üretir."""
    location_candidates = [courthouse, district, city]
    location = next((item.strip() for item in location_candidates if item and item.strip()), 'Görev')
    abbreviation = CATEGORY_ABBREVIATIONS.get(category, 'GEN')
    return f"{location} - {abbreviation}"

# Admin Required Decorator
def admin_required(f):
    """Sadece admin kullanıcıların erişimine izin verir"""
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

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# =============================================================================
# SETTINGS ROUTES - User Settings Management
# Routes for profile updates, avatar management, privacy, 2FA, notifications
# =============================================================================

@app.route('/settings/profile', methods=['POST'])
@login_required
def update_profile():
    """Profil bilgilerini güncelle (AJAX)"""
    try:
        data = request.get_json()
        
        # Update user fields
        if 'full_name' in data:
            current_user.full_name = data['full_name'].strip()
        if 'phone' in data:
            current_user.phone = data['phone'].strip()
        if 'bio' in data:
            current_user.bio = data['bio'].strip()
        if 'city' in data:
            current_user.city = data['city']
        if 'bar_association' in data:
            current_user.bar_association = data['bar_association']
        if 'bar_registration_number' in data:
            current_user.bar_registration_number = data['bar_registration_number'].strip()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profil bilgileriniz güncellendi.'})
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Bir hata oluştu.'}), 500


@app.route('/rate/<int:user_id>', methods=['GET', 'POST'])
@login_required
def rate_user(user_id):
    """Kullanıcıyı değerlendir"""
    user = db.session.get(User, user_id)
    if not user:
        flash('Kullanıcı bulunamadı.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        rating_value = request.form.get('rating')
        comment = request.form.get('comment', '').strip()
        
        if not rating_value or not rating_value.isdigit() or int(rating_value) < 1 or int(rating_value) > 5:
            flash('Geçerli bir puan seçiniz (1-5).', 'error')
            return redirect(url_for('rate_user', user_id=user_id))
        
        # Check if already rated
        existing_rating = Rating.query.filter_by(
            rater_id=current_user.id,
            rated_user_id=user_id
        ).first()
        
        if existing_rating:
            flash('Bu kullanıcıyı zaten değerlendirdiniz.', 'warning')
            return redirect(url_for('main.user_profile', user_id=user_id))
        
        new_rating = Rating(
            rater_id=current_user.id,
            rated_user_id=user_id,
            rating=int(rating_value),
            comment=comment
        )
        db.session.add(new_rating)
        db.session.commit()
        
        flash('Değerlendirmeniz kaydedildi.', 'success')
        return redirect(url_for('main.user_profile', user_id=user_id))
    
    return render_template('rate_user.html', user=user)


@app.route('/report/<report_type>/<int:item_id>', methods=['GET', 'POST'])
@login_required
def report_content(report_type, item_id):
    """İçerik şikayet et"""
    if report_type not in ['post', 'user', 'message']:
        abort(404)
    
    if request.method == 'POST':
        reason = request.form.get('reason', '').strip()
        description = request.form.get('description', '').strip()
        
        if not reason or not description:
            flash('Lütfen şikayet nedenini ve açıklamasını giriniz.', 'error')
            return redirect(url_for('report_content', report_type=report_type, item_id=item_id))
        
        # Check for existing report
        existing_report = Report.query.filter_by(
            reporter_id=current_user.id,
            report_type=report_type,
            item_id=item_id
        ).first()
        
        if existing_report:
            flash('Bu içeriği zaten şikayet ettiniz.', 'warning')
            return redirect(url_for('main.dashboard'))
        
        new_report = Report(
            reporter_id=current_user.id,
            report_type=report_type,
            item_id=item_id,
            reason=reason,
            description=description
        )
        db.session.add(new_report)
        db.session.commit()
        
        flash('Şikayetiniz alındı. En kısa sürede incelenecektir.', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('report.html', report_type=report_type, item_id=item_id)


@app.route('/settings/avatar', methods=['POST'])
@login_required
def update_avatar():
    """Profil fotoğrafını güncelle"""
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': 'Dosya bulunamadı.'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Dosya seçilmedi.'}), 400
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'success': False, 'message': 'Geçersiz dosya türü. PNG, JPG, JPEG veya GIF kullanınız.'}), 400
    
    # Save file
    filename = secure_filename(f"avatar_{current_user.id}_{secrets.token_hex(8)}.{file.filename.rsplit('.', 1)[1].lower()}")
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'avatars')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # Update user avatar
    current_user.avatar = f"/static/uploads/avatars/{filename}"
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Profil fotoğrafınız güncellendi.', 'avatar_url': current_user.avatar})


@app.route('/settings/avatar/remove', methods=['POST'])
@login_required
def remove_avatar():
    """Profil fotoğrafını kaldır"""
    current_user.avatar = None
    db.session.commit()
    return jsonify({'success': True, 'message': 'Profil fotoğrafınız kaldırıldı.'})


@app.route('/settings/privacy', methods=['POST'])
@login_required
def update_privacy_settings():
    """Gizlilik ayarlarını güncelle"""
    data = request.get_json()
    current_user.privacy_settings = data
    db.session.commit()
    return jsonify({'success': True, 'message': 'Gizlilik ayarlarınız güncellendi.'})


@app.route('/settings/2fa/setup', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    """İki faktörlü kimlik doğrulamayı kur"""
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        
        if not code:
            flash('Doğrulama kodu gereklidir.', 'error')
            return redirect(url_for('setup_2fa'))
        
        # Verify code (placeholder - implement actual 2FA logic)
        if code == '123456':  # Placeholder
            current_user.two_factor_enabled = True
            current_user.two_factor_secret = secrets.token_hex(16)
            db.session.commit()
            flash('İki faktörlü kimlik doğrulama etkinleştirildi.', 'success')
            return redirect(url_for('main.settings'))
        else:
            flash('Geçersiz doğrulama kodu.', 'error')
            return redirect(url_for('setup_2fa'))
    
    # Generate QR code (placeholder)
    qr_code_url = "https://placeholder-qr-code.com"
    return render_template('setup_2fa.html', qr_code_url=qr_code_url)


@app.route('/settings/2fa/disable', methods=['POST'])
@login_required
def disable_2fa():
    """İki faktörlü kimlik doğrulamayı kapat"""
    password = request.form.get('password', '').strip()
    
    if not password or not current_user.check_password(password):
        return jsonify({'success': False, 'message': 'Geçersiz şifre.'}), 400
    
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'İki faktörlü kimlik doğrulama kapatıldı.'})


@app.route('/settings/notifications', methods=['POST'])
@login_required
def update_notification_settings():
    """Bildirim ayarlarını güncelle"""
    data = request.get_json()
    current_user.notification_settings = data
    db.session.commit()
    return jsonify({'success': True, 'message': 'Bildirim ayarlarınız güncellendi.'})


@app.route('/settings/account/delete', methods=['POST'])
@login_required
def delete_account():
    """Hesabı sil"""
    password = request.form.get('password', '').strip()
    confirmation = request.form.get('confirmation', '').strip()
    
    if not password or not current_user.check_password(password):
        flash('Geçersiz şifre.', 'error')
        return redirect(url_for('main.settings'))
    
    if confirmation != 'SIL':
        flash('Hesap silme işlemini onaylamak için "SIL" yazınız.', 'error')
        return redirect(url_for('main.settings'))
    
    # Soft delete - mark as inactive
    current_user.is_active = False
    current_user.deleted_at = datetime.now(timezone.utc)
    db.session.commit()
    
    logout_user()
    flash('Hesabınız başarıyla silindi.', 'success')
    return redirect(url_for('auth.login'))


@app.route('/settings/password', methods=['POST'])
@login_required
def change_password():
    """Şifre değiştir"""
    current_password = request.form.get('current_password', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    if not current_password or not current_user.check_password(current_password):
        flash('Mevcut şifreniz hatalı.', 'error')
        return redirect(url_for('main.settings'))
    
    if not new_password or len(new_password) < 8:
        flash('Yeni şifre en az 8 karakter olmalıdır.', 'error')
        return redirect(url_for('main.settings'))
    
    if new_password != confirm_password:
        flash('Yeni şifreler eşleşmiyor.', 'error')
        return redirect(url_for('main.settings'))
    
    # Check password history
    password_history = PasswordHistory.query.filter_by(user_id=current_user.id).order_by(PasswordHistory.created_at.desc()).limit(5).all()
    for old_pw in password_history:
        if old_pw.check_password(new_password):
            flash('Yeni şifre son 5 şifrenizden biri olamaz.', 'error')
            return redirect(url_for('main.settings'))
    
    # Save old password to history
    old_password_hash = current_user.password_hash
    history_entry = PasswordHistory(user_id=current_user.id, password_hash=old_password_hash)
    db.session.add(history_entry)
    
    # Update password
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('Şifreniz başarıyla değiştirildi.', 'success')
    return redirect(url_for('main.settings'))


# =============================================================================
# NOTIFICATIONS ROUTES - Notification Management
# Routes for viewing, marking read, archiving notifications
# =============================================================================

@app.route('/notifications')
@login_required
def notifications():
    """Bildirimleri listele"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    notifications_query = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc())
    
    pagination = notifications_query.paginate(page=page, per_page=per_page, error_out=False)
    notifications_list = pagination.items
    
    # Mark as read
    unread_notifications = [n for n in notifications_list if not n.is_read]
    for notif in unread_notifications:
        notif.is_read = True
    if unread_notifications:
        db.session.commit()
    
    return render_template('notifications.html', 
                         notifications=notifications_list,
                         pagination=pagination)


@app.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Tüm bildirimleri okundu işaretle"""
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})


@app.route('/notifications/<int:notification_id>/click', methods=['POST'])
@login_required
def notification_click(notification_id):
    """Bildirime tıklandığında okundu işaretle"""
    notification = db.session.get(Notification, notification_id)
    if notification and notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
    return jsonify({'success': True})


@app.route('/notifications/<int:notification_id>/archive', methods=['POST'])
@login_required
def notification_archive(notification_id):
    """Bildirimi arşivle"""
    notification = db.session.get(Notification, notification_id)
    if notification and notification.user_id == current_user.id:
        notification.is_archived = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404


@app.route('/notifications/settings')
@login_required
def notification_settings():
    """Bildirim ayarları sayfası"""
    return render_template('notification_settings.html', user=current_user)


@app.route('/notifications/settings/update', methods=['POST'])
@login_required
def update_notification_preferences():
    """Bildirim tercihlerini güncelle"""
    data = request.get_json()
    
    if 'email_notifications' in data:
        current_user.email_notifications = data['email_notifications']
    if 'push_notifications' in data:
        current_user.push_notifications = data['push_notifications']
    if 'sms_notifications' in data:
        current_user.sms_notifications = data['sms_notifications']
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Bildirim ayarlarınız güncellendi.'})


@app.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notification_read():
    """Belirli bildirimi okundu işaretle (AJAX)"""
    data = request.get_json()
    notification_id = data.get('notification_id')
    
    if not notification_id:
        return jsonify({'success': False, 'message': 'Bildirim ID gerekli.'}), 400
    
    notification = db.session.get(Notification, notification_id)
    if notification and notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Bildirim bulunamadı.'}), 404


# =============================================================================
# LEGACY MESSAGES ROUTES - Old Message System (Deprecated)
# These routes are kept for backward compatibility
# New chat system is in blueprints/chat/routes.py
# =============================================================================

@app.route('/messages')
@login_required
def messages():
    """Mesajları listele (Eski sistem - geriye dönük uyumluluk için)"""
    flash('Mesajlaşma sistemi güncellenmiştir. Lütfen Chat bölümünü kullanınız.', 'info')
    return redirect(url_for('chat.chat_index'))


@app.route('/messages/send/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def send_message(receiver_id):
    """Mesaj gönder (Eski sistem - geriye dönük uyumluluk için)"""
    return redirect(url_for('chat.start_conversation', user_id=receiver_id))


@app.route('/messages/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Mesajı okundu işaretle (Eski sistem)"""
    message = db.session.get(Message, message_id)
    if message and message.receiver_id == current_user.id:
        message.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404


# =============================================================================
# WHATSAPP ROUTES - WhatsApp Integration
# Routes for WhatsApp post sharing and setup
# =============================================================================

@app.route('/whatsapp-ilan')
@dev_login_optional
def whatsapp_ilan():
    """WhatsApp ile ilan paylaş"""
    flash('WhatsApp entegrasyonu yakında aktif olacaktır.', 'info')
    return redirect(url_for('main.dashboard'))


@app.route('/whatsapp/setup')
@login_required
def whatsapp_setup():
    """WhatsApp kurulum sayfası"""
    return render_template('whatsapp_setup.html')


# =============================================================================
# SECURITY ROUTES - Security Settings & Session Management
# Routes for security settings, session management, password strength
# =============================================================================

@app.route('/security/settings', methods=['GET'])
@login_required
def security_settings():
    """Güvenlik ayarları sayfası"""
    active_sessions = UserSession.query.filter_by(user_id=current_user.id, is_active=True).all()
    recent_logs = SecurityLog.query.filter_by(user_id=current_user.id).order_by(SecurityLog.created_at.desc()).limit(10).all()
    
    return render_template('security_settings.html', 
                         active_sessions=active_sessions,
                         recent_logs=recent_logs)


@app.route('/security/sessions/terminate/<int:session_id>', methods=['POST'])
@login_required
def terminate_session(session_id):
    """Belirli oturumu sonlandır"""
    user_session = db.session.get(UserSession, session_id)
    
    if not user_session or user_session.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Oturum bulunamadı.'}), 404
    
    user_session.is_active = False
    user_session.ended_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Oturum sonlandırıldı.'})


@app.route('/security/sessions/terminate-all', methods=['POST'])
@login_required
def terminate_all_sessions():
    """Tüm diğer oturumları sonlandır"""
    current_session_id = session.get('session_id')
    
    UserSession.query.filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True,
        UserSession.id != current_session_id
    ).update({'is_active': False, 'ended_at': datetime.now(timezone.utc)})
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Tüm diğer oturumlar sonlandırıldı.'})


@app.route('/security/password/check-strength', methods=['POST'])
@login_required
def check_password_strength():
    """Şifre gücünü kontrol et (AJAX)"""
    data = request.get_json()
    password = data.get('password', '')
    
    strength = security_utils.check_password_strength(password)
    return jsonify({'success': True, 'strength': strength})


@app.route('/security/logs', methods=['GET'])
@login_required
def security_logs():
    """Güvenlik loglarını görüntüle"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    logs_query = SecurityLog.query.filter_by(user_id=current_user.id).order_by(SecurityLog.created_at.desc())
    pagination = logs_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('security_logs.html', 
                         logs=pagination.items,
                         pagination=pagination)


# =============================================================================
# SOCKETIO EVENTS - Real-time Communication
# WebSocket handlers for chat, notifications, typing indicators
# =============================================================================

@socketio.on('connect')
def handle_connect():
    """Socket.IO bağlantı event'i"""
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        logger.info(f"User {current_user.id} connected to Socket.IO")


@socketio.on('disconnect')
def handle_disconnect():
    """Socket.IO bağlantı kesme event'i"""
    if current_user.is_authenticated:
        leave_room(f'user_{current_user.id}')
        logger.info(f"User {current_user.id} disconnected from Socket.IO")


@socketio.on('join_conversation')
def handle_join_conversation(data):
    """Sohbet odasına katıl"""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        join_room(f'conversation_{conversation_id}')
        logger.info(f"User {current_user.id} joined conversation {conversation_id}")


@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    """Sohbet odasından ayrıl"""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        leave_room(f'conversation_{conversation_id}')
        logger.info(f"User {current_user.id} left conversation {conversation_id}")


@socketio.on('new_message')
def handle_new_message(data):
    """Yeni mesaj event'i"""
    conversation_id = data.get('conversation_id')
    message_content = data.get('message')
    
    if not conversation_id or not message_content:
        return
    
    # Broadcast to conversation room
    emit('message_received', {
        'conversation_id': conversation_id,
        'message': message_content,
        'sender_id': current_user.id,
        'sender_name': current_user.full_name,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }, room=f'conversation_{conversation_id}')


@socketio.on('typing')
def handle_typing(data):
    """Yazıyor göstergesi"""
    conversation_id = data.get('conversation_id')
    is_typing = data.get('is_typing', False)
    
    if conversation_id:
        emit('user_typing', {
            'user_id': current_user.id,
            'user_name': current_user.full_name,
            'is_typing': is_typing
        }, room=f'conversation_{conversation_id}', include_self=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
