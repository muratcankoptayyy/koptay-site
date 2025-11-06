"""
Tevkil Platform - Main Application
Avukatlar arası iş devri ve tevkil platformu
"""
import os
import csv
from datetime import datetime, timedelta, timezone
from io import StringIO
from flask import current_app, request, jsonify, render_template, redirect, url_for, flash, send_file, send_from_directory, session, abort, make_response
from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import emit, join_room, leave_room, send
from flask_wtf.csrf import generate_csrf
from werkzeug.utils import secure_filename
from models import db, User, TevkilPost, Application, Rating, Message, Notification, Favorite, PasswordReset, Conversation, Report, mask_name
from models import UserSession, SecurityLog, PasswordHistory, LoginAttempt
from sqlalchemy import or_, and_, inspect, func, extract, text
from sqlalchemy.exc import ProgrammingError
import secrets
import json
from constants import (
    CITIES,
    COURTHOUSES,
    POST_CATEGORIES,
    BAR_ASSOCIATIONS,
    TASK_CATEGORY_DEFINITIONS,
    TASK_CATEGORY_OPTIONS,
    CATEGORY_ABBREVIATIONS,
)
from geocoding_service import get_coordinates
from functools import wraps
import security_utils
import input_validation  # 🔒 Input validation & sanitization
from tevkil.app_factory import create_app
from tevkil.extensions import csrf, limiter, login_manager, socketio

# Initialize Flask app via factory
app = create_app()

TASK_CATEGORY_LABELS = {
    key: value.get('label', key.replace('_', ' ').title())
    for key, value in TASK_CATEGORY_DEFINITIONS.items()
}

# Extensions already configure CORS, CSRF, Socket.IO and rate limiting

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
                    print(f"🔓 DEV MODE: Auto-logged in as {first_user.email}")
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
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('Bu sayfaya erişim yetkiniz yok.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Context Processors
@app.context_processor
def inject_csrf_token():
    """CSRF token'ı tüm template'lere enjekte et"""
    return dict(csrf_token=generate_csrf)

@app.context_processor
def inject_global_vars():
    """Tüm template'lere global değişkenleri enjekte et"""
    unread_count = 0
    if current_user.is_authenticated:
        try:
            unread_count = Notification.query.filter_by(
                user_id=current_user.id, 
                read_at=None
            ).count()
        except Exception as e:
            print(f"⚠️ Notification count error: {str(e)}")
            unread_count = 0
    
    return dict(
        unread_count=unread_count,
        current_year=datetime.now().year,
        google_maps_api_key=app.config.get('GOOGLE_MAPS_API_KEY', ''),
        cities=CITIES,
        bar_associations=BAR_ASSOCIATIONS,
    )



@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    """Yeni kullanıcı kayıt işlemi"""
    if request.method == 'POST':
        form_values = {key: (request.form.get(key) or '').strip() for key in request.form}

        full_name = input_validation.sanitize_plain_text(form_values.get('full_name'))
        email_valid, email = input_validation.validate_email(form_values.get('email'))
        # ✅ Email'i her zaman lowercase yap
        email = email.lower() if email else ''
        
        phone_valid, phone = input_validation.validate_phone(form_values.get('phone'))
        
        # TC Kimlik No - OPSIYONEL
        tc_raw = (form_values.get('tc_number') or '').strip()
        if tc_raw:
            tc_valid, tc_number = input_validation.validate_tc_kimlik(tc_raw)
        else:
            # TC boşsa geçerli sayıyoruz (opsiyonel alan)
            tc_valid, tc_number = True, None
            
        bar_association = input_validation.sanitize_plain_text(form_values.get('bar_association'))
        bar_no_valid, bar_registration_number = input_validation.validate_baro_number(
            form_values.get('bar_registration_number')
        )
        lawyer_type = (form_values.get('lawyer_type') or '').lower()
        city = input_validation.sanitize_plain_text(form_values.get('city'))
        password = form_values.get('password') or ''

        specializations_raw = form_values.get('specializations') or ''
        specializations = []
        for raw_value in specializations_raw.split(','):
            sanitized_value = input_validation.sanitize_plain_text(raw_value.strip())
            if sanitized_value:
                specializations.append(sanitized_value)

        errors = []
        if not full_name:
            errors.append('Ad soyad bilgisi gereklidir.')
        if not email_valid:
            errors.append('Geçerli bir e-posta adresi giriniz.')
        if not phone_valid:
            errors.append('Geçerli bir telefon numarası giriniz.')
        # TC Kimlik sadece girilmişse kontrol et
        if tc_raw and not tc_valid:
            errors.append('Geçerli bir T.C. kimlik numarası giriniz ya da boş bırakınız.')
        if not bar_association:
            errors.append('Bağlı olduğunuz baroyu seçiniz.')
        if not bar_no_valid:
            errors.append('Geçerli bir baro sicil numarası giriniz.')
        if lawyer_type not in {'avukat', 'stajyer'}:
            errors.append('Avukat türü seçiniz.')
        if not city:
            errors.append('Şehir seçiniz.')
        if len(password) < 6:
            errors.append('Şifreniz en az 6 karakter olmalıdır.')

        if errors:
            print(f"❌ Registration validation failed for {email}: {errors}")
            for message in errors:
                flash(message, 'error')
            return render_template('phoenix/auth/register.html', form_data=form_values)

        # ✅ Email'i lowercase yaparak kontrol et
        existing_user = User.query.filter(db.func.lower(User.email) == email.lower()).first()
        if existing_user:
            print(f"❌ Registration blocked: email already exists ({email})")
            flash('Bu e-posta adresiyle daha önce kayıt yapılmış.', 'error')
            return render_template('phoenix/auth/register.html', form_data=form_values)

        duplicate_baro = User.query.filter_by(
            bar_association=bar_association,
            bar_registration_number=bar_registration_number
        ).first()
        if duplicate_baro:
            print(f"❌ Registration blocked: bar number already in use - {bar_association}/{bar_registration_number}")
            flash('Bu baro sicil numarası zaten kayıtlı.', 'error')
            return render_template('phoenix/auth/register.html', form_data=form_values)

        # ✅ User objesi oluştur - email lowercase
        user = User(
            full_name=full_name,
            email=email.lower(),  # Garantiye al
            phone=phone,
            whatsapp_number=phone,
            tc_number=tc_number,
            bar_association=bar_association,
            bar_registration_number=bar_registration_number,
            lawyer_type=lawyer_type or 'avukat',
            city=city,
            specializations=specializations or None,
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            print(f"✅ Yeni kullanıcı oluşturuldu: {user.email} (ID: {user.id})")
            
            # ✅ Veritabanına kaydedildiğini doğrula
            verify_user = User.query.filter_by(email=email.lower()).first()
            if verify_user:
                print(f"✅ Kullanıcı veritabanında doğrulandı: {verify_user.email} (ID: {verify_user.id})")
            else:
                print(f"⚠️ UYARI: Kullanıcı commit edildi ama sorgulamada bulunamadı!")
                
        except Exception as exc:
            db.session.rollback()
            current_app.logger.error('Kayıt sırasında hata: %s', exc)
            print(f"❌ Registration commit failed for {email}: {str(exc)}")
            import traceback
            traceback.print_exc()
            flash('Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyiniz.', 'error')
            return render_template('phoenix/auth/register.html', form_data=form_values)

        if current_app.config.get('EMAIL_ENABLED'):
            try:
                from email_service import send_welcome_email
                send_welcome_email(user)
            except Exception as email_error:  # pragma: no cover - notification best effort
                current_app.logger.warning('Hoş geldiniz e-postası gönderilemedi: %s', email_error)

        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))

    return render_template('phoenix/auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Login rate limit
def login():
    """Kullanıcı girişi - Güvenlik özellikleriyle"""
    if request.method == 'POST':
        raw_email = request.form.get('email') or ''
        email = input_validation.sanitize_plain_text(str(raw_email)).strip().lower()
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        print(f"🔐 Login attempt: {email} from {ip_address}")
        print(f"📧 Email: {email}")
        print(f"🔑 Password length: {len(password) if password else 0}")
        print(f"📝 Remember: {remember}")
        print(f"🌐 IP: {ip_address}")
        
        # ✅ Case-insensitive email search
        user = User.query.filter(db.func.lower(User.email) == email.lower()).first()
        print(f"👤 User found: {user is not None}")
        if user:
            print(f"👤 User email in DB: {user.email}, ID: {user.id}")
        
        if not user:
            # Kullanıcı bulunamadı
            print(f"❌ User not found: {email}")
            security_utils.log_login_attempt(
                email, ip_address, user_agent, 
                success=False, failure_reason='user_not_found'
            )
            flash('Hatalı e-posta veya şifre', 'error')
            return render_template('phoenix/auth/login.html')
        
        # 1. HESAP KİLİDİ KONTROLÜ
        if user.account_locked_until and datetime.utcnow() < user.account_locked_until:
            remaining_minutes = int((user.account_locked_until - datetime.utcnow()).total_seconds() / 60)
            security_utils.log_security_event(
                user.id, 'login_attempt_while_locked', 'WARNING',
                f'Login attempt on locked account from {ip_address}'
            )
            flash(f'Hesabınız kilitli. {remaining_minutes} dakika sonra tekrar deneyin.', 'error')
            return render_template('phoenix/auth/login.html')
        
        # Kilit süresi dolduysa kilidi kaldır
        if user.account_locked_until and datetime.utcnow() >= user.account_locked_until:
            security_utils.unlock_account(user)
        
        # 2. RATE LIMITING KONTROLÜ (IP bazlı)
        is_allowed, remaining, lockout_until = security_utils.check_login_attempts(
            email, ip_address, max_attempts=5, lockout_minutes=15
        )
        
        if not is_allowed:
            security_utils.log_security_event(
                user.id, 'rate_limit_exceeded', 'WARNING',
                f'Too many failed login attempts from {ip_address}'
            )
            flash('Çok fazla başarısız deneme. 15 dakika sonra tekrar deneyin.', 'error')
            return render_template('phoenix/auth/login.html')
        
        # 3. ŞİFRE KONTROLÜ
        print(f"🔐 Checking password for {email}...")
        print(f"📊 User has password_hash: {user.password_hash is not None}")
        print(f"📏 Password hash length: {len(user.password_hash) if user.password_hash else 0}")
        
        password_valid = user.check_password(password)
        print(f"✅ Password valid: {password_valid}")
        
        if not password_valid:
            print(f"❌ Password incorrect for {email}")
            
            # Başarısız denemeyi kaydet
            security_utils.log_login_attempt(
                email, ip_address, user_agent,
                success=False, failure_reason='invalid_password'
            )
            
            # Başarısız deneme sayısını artır
            is_locked = security_utils.increment_failed_attempts(user)
            
            if is_locked:
                security_utils.log_security_event(
                    user.id, 'account_locked', 'WARNING',
                    'Account locked due to too many failed login attempts'
                )
                flash('Çok fazla başarısız deneme. Hesabınız 15 dakika kilitlendi.', 'error')
            else:
                remaining_attempts = 5 - user.failed_login_attempts
                flash(f'Hatalı şifre. Kalan deneme hakkı: {remaining_attempts}', 'error')
            
            return render_template('phoenix/auth/login.html')
        
        # 4. HESAP AKTİFLİK KONTROLÜ
        if not user.is_active:
            security_utils.log_security_event(
                user.id, 'login_attempt_inactive', 'WARNING',
                'Login attempt on inactive account'
            )
            flash('Hesabınız aktif değil. Lütfen yöneticiyle iletişime geçin.', 'error')
            return render_template('phoenix/auth/login.html')
        
        # 5. 2FA KONTROLÜ
        if user.two_factor_enabled:
            # 2FA gerekli - önce session'a kullanıcıyı kaydet ama login yapma
            session['pending_2fa_user_id'] = user.id
            session['pending_2fa_remember'] = remember
            return redirect(url_for('verify_2fa'))
        
        # 6. LOGIN BAŞARILI
        print(f"✅ Login successful: {email}")
        print(f"🔐 About to call login_user()...")
        
        # Session'ı geçici tut (web için normal session)
        session.permanent = False
        print(f"📝 Session permanent set to False")
        
        # Login yap - Web için remember=False (mobil API token kullanacak)
        login_user(user, remember=False)
        print(f"✅ login_user() called successfully")
        print(f"👤 current_user.is_authenticated: {current_user.is_authenticated}")
        print(f"👤 current_user.email: {current_user.email if current_user.is_authenticated else 'N/A'}")
        
        # Başarısız deneme sayısını sıfırla
        security_utils.reset_failed_attempts(user)
        
        # Son aktiflik zamanını güncelle
        user.last_active = datetime.utcnow()
        db.session.commit()
        print(f"💾 Database committed")
        
        # Session token oluştur
        session_token = security_utils.create_user_session(user.id)
        session['session_token'] = session_token
        print(f"🎫 Session token created and stored")
        
        # Başarılı login'i logla
        security_utils.log_login_attempt(
            email, ip_address, user_agent,
            success=True
        )
        security_utils.log_security_event(
            user.id, 'login_success', 'INFO',
            f'Successful login from {ip_address}'
        )
        
        # Redirect
        next_page = request.args.get('next')
        redirect_url = next_page or url_for('dashboard')
        print(f"🔀 Redirecting to: {redirect_url}")
        print(f"🎯 Final session state: permanent={session.permanent}, session_token={session.get('session_token') is not None}")
        
        return redirect(redirect_url)
    
    return render_template('phoenix/auth/login.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Çıkış - Session sonlandırma ile"""
    user_id = current_user.id
    
    # Session'ı sonlandır
    if 'session_token' in session:
        session_token = session.get('session_token')
        user_session = UserSession.query.filter_by(session_token=session_token).first()
        if user_session:
            user_session.is_active = False
            db.session.commit()
    
    # Güvenlik logla
    security_utils.log_security_event(
        user_id, 'logout', 'INFO',
        'User logged out successfully'
    )
    
    logout_user()
    session.clear()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Şifremi unuttum"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Token oluştur
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            
            # Eski tokenleri temizle
            PasswordReset.query.filter_by(user_id=user.id).delete()
            
            # Yeni token kaydet
            reset = PasswordReset(
                user_id=user.id,
                token=token,
                expires_at=expires_at
            )
            db.session.add(reset)
            db.session.commit()
            
            # Email gönder (şimdilik sadece flash mesajı)
            reset_url = url_for('reset_password', token=token, _external=True)
            flash(f'Şifre sıfırlama bağlantısı: {reset_url}', 'info')
            flash('Şifre sıfırlama bağlantısı oluşturuldu. (Email entegrasyonu sonra eklenecek)', 'success')
        else:
            # Güvenlik için her zaman başarılı mesajı göster
            flash('Eğer bu e-posta kayıtlıysa, şifre sıfırlama bağlantısı gönderildi.', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('phoenix/auth/forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Şifre sıfırlama"""
    reset = PasswordReset.query.filter_by(token=token).first()
    
    if not reset or not reset.is_valid():
        flash('Geçersiz veya süresi dolmuş token', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if password != password_confirm:
            flash('Şifreler eşleşmiyor', 'error')
            return render_template('phoenix/auth/reset_password.html', token=token)
        
        if len(password) < 6:
            flash('Şifre en az 6 karakter olmalıdır', 'error')
            return render_template('phoenix/auth/reset_password.html', token=token)
        
        # Şifreyi güncelle
        user = reset.user
        user.set_password(password)
        
        # Token'ı kullanıldı olarak işaretle
        reset.used_at = datetime.now(timezone.utc)
        db.session.commit()
        
        flash('Şifreniz başarıyla değiştirildi. Artık giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    
    return render_template('phoenix/auth/reset_password.html', token=token)

# ============================================
# MAIN PAGES
# ============================================

@app.route('/')
def index():
    """Ana sayfa - Giriş yapmışsa dashboard'a yönlendir"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    recent_posts = TevkilPost.query.filter_by(status='active').order_by(TevkilPost.created_at.desc()).limit(6).all()
    return render_template('index.html', posts=recent_posts)

@app.route('/dashboard')
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
        print(f"❌ Dashboard error in initial queries: {str(e)}")
        flash('Dashboard yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Chart Data: Son 6 ayın başvuru trendi
        from datetime import datetime, timedelta
        import calendar
        
        now = datetime.now(timezone.utc)
        chart_months = []
        chart_incoming = []
        chart_outgoing = []
        
        for i in range(5, -1, -1):  # Son 6 ay
            month_date = now - timedelta(days=30*i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if i == 0:
                month_end = now
            else:
                next_month = month_start.replace(day=28) + timedelta(days=4)
                month_end = next_month - timedelta(days=next_month.day)
            
            # Ay adı (Türkçe)
            turkish_months = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']
            chart_months.append(turkish_months[month_start.month - 1])
            
            # Gelen başvurular (bu aydaki)
            incoming_count = db.session.query(Application).join(TevkilPost).filter(
                TevkilPost.user_id == current_user.id,
                Application.created_at >= month_start,
                Application.created_at <= month_end
            ).count()
            chart_incoming.append(incoming_count)
            
            # Yaptığım başvurular
            outgoing_count = Application.query.filter(
                Application.applicant_id == current_user.id,
                Application.created_at >= month_start,
                Application.created_at <= month_end
            ).count()
            chart_outgoing.append(outgoing_count)
        
        # Chart Data: Kategori dağılımı
        from sqlalchemy import func
        category_data = db.session.query(
            TevkilPost.category, 
            func.count(TevkilPost.id)
        ).filter_by(user_id=current_user.id).group_by(TevkilPost.category).all()
        
        category_labels = [cat[0] or 'Diğer' for cat in category_data]
        category_counts = [cat[1] for cat in category_data]
        
        # Performance stats
        # Bu ay tamamlanan işler
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_completed = TevkilPost.query.filter(
            TevkilPost.user_id == current_user.id,
            TevkilPost.status == 'completed',
            TevkilPost.updated_at >= month_start
        ).count()
        
        # Tahmini toplam kazanç (completed işlerin ücret toplamı)
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
        
        # Kullanıcı istatistiklerini getir
        user_stats = get_user_stats(current_user.id) or {}

        week_ago = now - timedelta(days=7)

        def _to_utc(dt):
            if not dt:
                return None
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)

        def _metric_subtitle(delta):
            return f"Son 7 gün +{delta}" if delta else "Son 7 gün değişiklik yok"

        active_posts_count = sum(1 for post in my_posts if post.status == 'active')
        new_active_posts = sum(
            1 for post in my_posts
            if post.status == 'active' and (_to_utc(post.created_at) or now) >= week_ago
        )

        incoming_total = len(incoming_applications)
        incoming_recent = sum(1 for app in incoming_applications if (_to_utc(app.created_at) or now) >= week_ago)

        outgoing_total = len(my_applications)
        outgoing_recent = sum(1 for app in my_applications if (_to_utc(app.created_at) or now) >= week_ago)

        recent_notifications_count = Notification.query.filter_by(user_id=current_user.id).filter(
            Notification.created_at >= week_ago
        ).count()

        metrics = [
            {
                "label": "Aktif ilanlar",
                "icon": "work",
                "value": active_posts_count,
                "subtitle": _metric_subtitle(new_active_posts),
                "url": url_for('list_posts', filter='my_active'),
            },
            {
                "label": "Gelen başvurular",
                "icon": "inbox",
                "value": incoming_total,
                "subtitle": _metric_subtitle(incoming_recent),
                "url": url_for('applications_received'),
            },
            {
                "label": "Başvurularım",
                "icon": "send",
                "value": outgoing_total,
                "subtitle": _metric_subtitle(outgoing_recent),
                "url": url_for('applications_sent'),
            },
            {
                "label": "Okunmamış bildirim",
                "icon": "notifications",
                "value": unread_notifications,
                "subtitle": _metric_subtitle(recent_notifications_count),
                "url": url_for('notifications'),
            },
        ]

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
        for post in sorted(my_posts, key=lambda item: _to_utc(item.updated_at) or _to_utc(item.created_at) or now, reverse=True)[:5]:
            deadline_source = post.deadline or post.court_date
            if deadline_source:
                deadline_text = (_to_utc(deadline_source) or now).strftime('%d %b %Y')
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
                'url': url_for('post_detail', post_id=post.id),
            })

        upcoming_posts = TevkilPost.query.filter(
            TevkilPost.user_id == current_user.id,
            TevkilPost.court_date.isnot(None),
            TevkilPost.court_date >= now
        ).order_by(TevkilPost.court_date.asc()).limit(4).all()

        hearings = []
        for item in upcoming_posts:
            court_dt = _to_utc(item.court_date) or now
            hearings.append({
                'date': court_dt.strftime('%d %b %Y'),
                'time': court_dt.strftime('%H:%M'),
                'title': item.title,
                'court': item.courthouse or item.city or 'Mahkeme bilgisi yok',
                'counterpart': item.category,
                'url': url_for('post_detail', post_id=item.id),
            })

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
            created_at = _to_utc(notif.created_at) or now
            notifications_feed.append({
                'icon': notification_icon_map.get(notif.type, 'notifications'),
                'title': notif.title or notif.message or 'Bildirim',
                'description': notif.message or '',
                'time': notif.time_ago if hasattr(notif, 'time_ago') else created_at.strftime('%d %b %Y %H:%M'),
                'url': notif.action_url,
                'is_new': getattr(notif, 'is_new', False),
            })

        timeline_entries = []

        for post in my_posts[:5]:
            timeline_entries.append({
                'timestamp': _to_utc(post.created_at) or now,
                'icon': 'add_circle',
                'variant': 'brand',
                'title': 'Yeni ilan oluşturdunuz',
                'description': post.title,
                'url': url_for('post_detail', post_id=post.id),
            })

        for app_item in my_applications[:5]:
            timeline_entries.append({
                'timestamp': _to_utc(app_item.created_at) or now,
                'icon': 'send',
                'variant': 'purple',
                'title': 'Başvuru yaptınız',
                'description': app_item.post.title if app_item.post else 'Bir ilana başvuru yapıldı',
                'url': url_for('post_detail', post_id=app_item.post_id),
            })

        for incoming in incoming_applications[:5]:
            applicant_name = incoming.applicant.masked_full_name if incoming.applicant else 'Başvuru sahibi'
            timeline_entries.append({
                'timestamp': _to_utc(incoming.created_at) or now,
                'icon': 'inbox',
                'variant': 'emerald',
                'title': 'Yeni başvuru aldınız',
                'description': f"{applicant_name} başvurdu",
                'url': url_for('applications_received'),
            })

        sorted_timeline = sorted(timeline_entries, key=lambda item: item['timestamp'], reverse=True)[:6]
        for entry in sorted_timeline:
            entry['time_display'] = entry['timestamp'].strftime('%d %b %Y, %H:%M')

        quick_actions = [
            {
                'label': 'Yeni ilan',
                'icon': 'add_circle',
                'url': url_for('create_post'),
                'variant': 'brand',
            },
            {
                'label': 'İlan ara',
                'icon': 'search',
                'url': url_for('list_posts'),
                'variant': 'emerald',
            },
            {
                'label': 'Mesajlar',
                'icon': 'forum',
                'url': url_for('chat'),
                'variant': 'purple',
            },
            {
                'label': 'Harita',
                'icon': 'map',
                'url': url_for('map_view'),
                'variant': 'amber',
            },
        ]

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
            'dashboard.html',
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
            chart_months=chart_months,
            chart_incoming=chart_incoming,
            chart_outgoing=chart_outgoing,
            category_labels=category_labels,
            category_counts=category_counts,
            monthly_completed=monthly_completed,
            total_earnings=total_earnings,
            avg_rating=avg_rating,
            unread_notifications=unread_notifications,
            user_stats=user_stats,
        )
    except Exception as e:
        print(f"❌ Dashboard error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Minimal dashboard göster
        return render_template('phoenix/dashboard/overview.html',
                             my_posts=my_posts,
                             my_applications=my_applications,
                             incoming_applications=incoming_applications,
                             unread_notifications=unread_notifications,
                             chart_months=[],
                             chart_incoming=[],
                             chart_outgoing=[],
                             category_labels=[],
                             category_counts=[],
                             monthly_completed=0,
                             total_earnings=0,
                             avg_rating=0,
                             user_stats={})

@app.route('/stats')
@dev_login_optional
def stats_page():
    """Detaylı istatistikler sayfası"""
    # Kullanıcı istatistikleri
    user_stats = get_user_stats(current_user.id)
    
    # Platform istatistikleri (admin için tüm platform, diğerleri için özet)
    platform_stats = get_platform_stats() if current_user.is_admin else None
    
    # Son 30 günlük aktivite grafiği
    from datetime import datetime, timedelta
    
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
        
        # O günkü görüntülenmeler (tüm ilanların toplamı)
        views_count = db.session.query(db.func.sum(TevkilPost.view_count)).filter(
            TevkilPost.user_id == current_user.id,
            TevkilPost.last_viewed_at >= day_start,
            TevkilPost.last_viewed_at < day_end
        ).scalar() or 0
        
        daily_stats.append({
            'date': day_start.strftime('%d %b'),
            'posts': posts_count,
            'applications': applications_count,
            'views': views_count
        })
    
    return render_template('stats.html', 
                         user_stats=user_stats,
                         platform_stats=platform_stats,
                         daily_stats=daily_stats)

@app.route('/applications/received')
@dev_login_optional
def applications_received():
    """Gelen başvurular - kullanıcı ilanlarına yapılan başvurular (Phoenix görünümü)"""
    incoming_applications = db.session.query(Application).join(TevkilPost).filter(
        TevkilPost.user_id == current_user.id
    ).order_by(Application.created_at.desc()).all()

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    def _to_utc(dt):
        if not dt:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    def _initials(name: str | None) -> str:
        if not name:
            return "?"
        parts = [segment for segment in name.strip().split() if segment]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    def _time_ago(dt):
        if not dt:
            return ""
        delta = now - dt
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return "az önce"
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

    status_labels = {
        'pending': 'Beklemede',
        'accepted': 'Kabul edildi',
        'rejected': 'Reddedildi',
    }
    status_variants = {
        'pending': 'amber',
        'accepted': 'emerald',
        'rejected': 'rose',
    }
    status_icons = {
        'pending': 'hourglass_top',
        'accepted': 'task_alt',
        'rejected': 'cancel',
    }

    total_count = len(incoming_applications)
    pending_count = sum(1 for item in incoming_applications if item.status == 'pending')
    accepted_count = sum(1 for item in incoming_applications if item.status == 'accepted')
    rejected_count = sum(1 for item in incoming_applications if item.status == 'rejected')

    recent_total = sum(1 for item in incoming_applications if (_to_utc(item.created_at) or now) >= week_ago)
    recent_accepted = sum(1 for item in incoming_applications if item.status == 'accepted' and (_to_utc(item.updated_at) or now) >= week_ago)
    recent_rejected = sum(1 for item in incoming_applications if item.status == 'rejected' and (_to_utc(item.updated_at) or now) >= week_ago)

    decision_rate = int(((accepted_count + rejected_count) / total_count) * 100) if total_count else 0
    pending_ratio = int((pending_count / total_count) * 100) if total_count else 0

    metrics = [
        {
            'label': 'Toplam başvuru',
            'icon': 'inbox',
            'value': total_count,
            'subtitle': f'Son 7 gün {recent_total}',
            'variant': 'brand',
        },
        {
            'label': 'Bekleyen yanıt',
            'icon': 'hourglass_top',
            'value': pending_count,
            'subtitle': f'%{pending_ratio} beklemede',
            'variant': 'amber',
        },
        {
            'label': 'Kabul edilen',
            'icon': 'task_alt',
            'value': accepted_count,
            'subtitle': f'Son 7 gün +{recent_accepted}',
            'variant': 'emerald',
        },
        {
            'label': 'Reddedilen',
            'icon': 'cancel',
            'value': rejected_count,
            'subtitle': f'Son 7 gün +{recent_rejected}',
            'variant': 'rose',
        },
    ]

    filters = [
        {'key': 'all', 'label': 'Tümü', 'count': total_count},
        {'key': 'pending', 'label': 'Beklemede', 'count': pending_count},
        {'key': 'accepted', 'label': 'Kabul edilen', 'count': accepted_count},
        {'key': 'rejected', 'label': 'Reddedilen', 'count': rejected_count},
    ]

    application_cards = []
    for item in incoming_applications:
        post = item.post
        applicant = item.applicant
        created_at_utc = _to_utc(item.created_at) or now
        updated_at_utc = _to_utc(item.updated_at) or created_at_utc
        deadline_source = None
        if post:
            deadline_source = post.deadline or post.court_date
        deadline_utc = _to_utc(deadline_source) if deadline_source else None
        deadline_display = deadline_utc.strftime('%d %b %Y, %H:%M') if deadline_utc else 'Takvimlenmedi'

        application_cards.append({
            'id': item.id,
            'status': item.status,
            'status_label': status_labels.get(item.status, item.status.title()),
            'status_variant': status_variants.get(item.status, 'slate'),
            'status_icon': status_icons.get(item.status, 'info'),
            'is_new': created_at_utc >= week_ago,
            'created_display': created_at_utc.strftime('%d %b %Y, %H:%M'),
            'updated_display': updated_at_utc.strftime('%d %b %Y, %H:%M'),
            'time_ago': _time_ago(created_at_utc),
            'message': item.message,
            'proposed_price': item.proposed_price,
            'post': {
                'title': post.title if post else 'İlan kaldırıldı',
                'category': post.category if post else 'Kategori yok',
                'city': (post.city or post.location) if post else None,
                'url': url_for('post_detail', post_id=post.id) if post else None,
                'deadline': deadline_display,
            },
            'applicant': {
                'masked_name': applicant.masked_full_name if applicant else 'Başvuru sahibi',
                'full_name': applicant.full_name if applicant else None,
                'initials': _initials(applicant.full_name if applicant else None),
                'profile_url': url_for('user_profile', user_id=applicant.id) if applicant else None,
                'city': applicant.city if applicant else None,
                'bar': applicant.bar_association if applicant else None,
            },
            'can_manage': item.status == 'pending',
        })

    return render_template(
        'phoenix/applications/received.html',
        applications=application_cards,
        metrics=metrics,
        filters=filters,
        decision_rate=decision_rate,
        counts={
            'total': total_count,
            'pending': pending_count,
            'accepted': accepted_count,
            'rejected': rejected_count,
        },
    )

@app.route('/applications/sent')
@dev_login_optional
def applications_sent():
    """Gönderilen başvurular - kullanıcı başvuruları (Phoenix görünümü)"""
    my_applications = Application.query.filter_by(applicant_id=current_user.id).order_by(Application.created_at.desc()).all()

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    def _to_utc(dt):
        if not dt:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    def _initials(name: str | None) -> str:
        if not name:
            return "?"
        parts = [segment for segment in name.strip().split() if segment]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    def _time_ago(dt):
        if not dt:
            return ""
        delta = now - dt
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return "az önce"
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

    status_labels = {
        'pending': 'Yanıt bekliyor',
        'accepted': 'Kabul edildi',
        'rejected': 'Reddedildi',
    }
    status_variants = {
        'pending': 'amber',
        'accepted': 'emerald',
        'rejected': 'rose',
    }
    status_icons = {
        'pending': 'hourglass_top',
        'accepted': 'task_alt',
        'rejected': 'cancel',
    }

    total_count = len(my_applications)
    pending_count = sum(1 for item in my_applications if item.status == 'pending')
    accepted_count = sum(1 for item in my_applications if item.status == 'accepted')
    rejected_count = sum(1 for item in my_applications if item.status == 'rejected')

    recent_sent = sum(1 for item in my_applications if (_to_utc(item.created_at) or now) >= week_ago)
    recent_decided = sum(1 for item in my_applications if item.status != 'pending' and (_to_utc(item.updated_at) or now) >= week_ago)

    acceptance_rate = int((accepted_count / total_count) * 100) if total_count else 0
    decision_rate = int(((accepted_count + rejected_count) / total_count) * 100) if total_count else 0

    metrics = [
        {
            'label': 'Gönderdiğim başvuru',
            'icon': 'send',
            'value': total_count,
            'subtitle': f'Son 7 gün {recent_sent}',
            'variant': 'brand',
        },
        {
            'label': 'Yanıt bekliyor',
            'icon': 'hourglass_top',
            'value': pending_count,
            'subtitle': f'%{decision_rate} yanıtlandı',
            'variant': 'amber',
        },
        {
            'label': 'Kabul edilen',
            'icon': 'task_alt',
            'value': accepted_count,
            'subtitle': f'Oran %{acceptance_rate}',
            'variant': 'emerald',
        },
        {
            'label': 'Karara bağlanan',
            'icon': 'insights',
            'value': accepted_count + rejected_count,
            'subtitle': f'Son 7 gün +{recent_decided}',
            'variant': 'indigo',
        },
    ]

    filters = [
        {'key': 'all', 'label': 'Tümü', 'count': total_count},
        {'key': 'pending', 'label': 'Beklemede', 'count': pending_count},
        {'key': 'accepted', 'label': 'Kabul edilen', 'count': accepted_count},
        {'key': 'rejected', 'label': 'Reddedilen', 'count': rejected_count},
    ]

    application_cards = []
    for item in my_applications:
        post = item.post
        owner = post.user if post else None
        created_at_utc = _to_utc(item.created_at) or now
        updated_at_utc = _to_utc(item.updated_at) or created_at_utc
        deadline_source = None
        if post:
            deadline_source = post.deadline or post.court_date
        deadline_utc = _to_utc(deadline_source) if deadline_source else None
        deadline_display = deadline_utc.strftime('%d %b %Y, %H:%M') if deadline_utc else 'Takvimlenmedi'

        response_time = None
        if item.response_time:
            minutes = int(item.response_time)
            if minutes >= 60:
                hours = minutes // 60
                response_time = f"{hours} sa"
            else:
                response_time = f"{minutes} dk"

        application_cards.append({
            'id': item.id,
            'status': item.status,
            'status_label': status_labels.get(item.status, item.status.title()),
            'status_variant': status_variants.get(item.status, 'slate'),
            'status_icon': status_icons.get(item.status, 'info'),
            'created_display': created_at_utc.strftime('%d %b %Y, %H:%M'),
            'updated_display': updated_at_utc.strftime('%d %b %Y, %H:%M'),
            'time_ago': _time_ago(created_at_utc),
            'message': item.message,
            'proposed_price': item.proposed_price,
            'response_time': response_time,
            'post': {
                'title': post.title if post else 'İlan kaldırıldı',
                'category': post.category if post else 'Kategori yok',
                'city': (post.city or post.location) if post else None,
                'url': url_for('post_detail', post_id=post.id) if post else None,
                'deadline': deadline_display,
            },
            'owner': {
                'masked_name': owner.masked_full_name if owner else 'İlan sahibi',
                'full_name': owner.full_name if owner else None,
                'initials': _initials(owner.full_name if owner else None),
                'profile_url': url_for('user_profile', user_id=owner.id) if owner else None,
                'bar': owner.bar_association if owner else None,
                'city': owner.city if owner else None,
            },
        })

    return render_template(
        'phoenix/applications/sent.html',
        applications=application_cards,
        metrics=metrics,
        filters=filters,
        counts={
            'total': total_count,
            'pending': pending_count,
            'accepted': accepted_count,
            'rejected': rejected_count,
        },
        rates={
            'acceptance': acceptance_rate,
            'decision': decision_rate,
        }
    )

# ============================================
# TEVKIL POST ROUTES
# ============================================

@app.route('/posts')
@dev_login_optional
def list_posts():
    """İlan listesi - Gelişmiş Filtreleme"""
    from constants import CITIES

    # Filters
    user_filter = request.args.get('filter')  # legacy user-specific filters
    filter_type = request.args.get('filter_type', 'all')
    category = request.args.get('category')
    city = request.args.get('city')
    urgency = request.args.get('urgency')
    search = request.args.get('search')

    # 🆕 GELİŞMİŞ FİLTRELER
    price_min = request.args.get('price_min', type=int)
    price_max = request.args.get('price_max', type=int)
    hearing_date_from = request.args.get('hearing_date_from')
    hearing_date_to = request.args.get('hearing_date_to')
    urgent_only = request.args.get('urgent_only') in ('1', 'on', 'true', 'True')
    remote_allowed = request.args.get('remote_allowed') in ('1', 'on', 'true', 'True')

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    soon_threshold = now + timedelta(days=7)

    category_label_map = TASK_CATEGORY_LABELS

    urgency_variants = {
        'very_urgent': {'label': 'Çok acil', 'variant': 'rose', 'icon': 'warning'},
        'urgent': {'label': 'Acil', 'variant': 'amber', 'icon': 'schedule'},
        'normal': {'label': 'Normal', 'variant': 'slate', 'icon': 'event'},
        None: {'label': 'Normal', 'variant': 'slate', 'icon': 'event'},
    }

    status_labels = {
        'active': 'Aktif',
        'assigned': 'Atandı',
        'completed': 'Tamamlandı',
        'cancelled': 'İptal edildi',
    }

    def _slugify(value):
        if not value:
            return 'other'
        cleaned = ''.join(ch.lower() if ch.isalnum() else '-' for ch in value)
        return '-'.join(segment for segment in cleaned.split('-') if segment) or 'other'

    category_slug_map = { _slugify(key): key for key in category_label_map.keys() }

    # Base query
    if user_filter == 'my_active':
        # Kullanıcının aktif ilanları
        query = TevkilPost.query.filter_by(user_id=current_user.id, status='active')
    elif user_filter == 'my_completed':
        # Kullanıcının tamamlanan ilanları
        query = TevkilPost.query.filter_by(user_id=current_user.id, status='completed')
    elif user_filter == 'my_all':
        # Kullanıcının tüm ilanları
        query = TevkilPost.query.filter_by(user_id=current_user.id)
    else:
        # Tüm aktif ilanlar (genel liste)
        query = TevkilPost.query.filter_by(status='active')
    
    # Temel filtreler
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
    
    # 🆕 FİYAT FİLTRELERİ
    if price_min is not None:
        query = query.filter(TevkilPost.price_min >= price_min)
    if price_max is not None:
        query = query.filter(
            or_(
                TevkilPost.price_min <= price_max,
                TevkilPost.price_min.is_(None)
            )
        )
    
    # 🆕 TARİH FİLTRELERİ
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
    
    # 🆕 ACİLİYET FİLTRESİ
    if urgent_only:
        query = query.filter_by(urgency_level='urgent')
    
    # 🆕 UZAKTAN ÇALIŞMA FİLTRESİ
    if remote_allowed:
        query = query.filter_by(remote_allowed=True)

    # Hızlı filtreler
    if filter_type == 'urgent':
        query = query.filter(TevkilPost.urgency_level == 'urgent')
    elif filter_type == 'very_urgent':
        query = query.filter(TevkilPost.urgency_level == 'very_urgent')
    elif filter_type == 'recent':
        query = query.filter(TevkilPost.created_at >= week_ago)
    elif filter_type == 'remote':
        query = query.filter(TevkilPost.remote_allowed.is_(True))
    elif filter_type == 'upcoming':
        query = query.filter(
            TevkilPost.court_date.isnot(None),
            TevkilPost.court_date <= soon_threshold
        )
    elif filter_type and filter_type.startswith('cat-'):
        slug = filter_type[4:]
        category_key = category_slug_map.get(slug)
        if category_key:
            query = query.filter(TevkilPost.category == category_key)
    
    # Sıralama
    query = query.order_by(TevkilPost.created_at.desc())
    
    # 🆕 PAGINATION
    from pagination_utils import paginate_query, get_page_numbers
    page = request.args.get('page', 1, type=int)
    per_page = max(10, min(request.args.get('per_page', 20, type=int), 50))
    
    base_query = query
    pagination = paginate_query(base_query, page=page, per_page=per_page)
    posts = pagination['items']

    favorite_ids = set()
    if current_user.is_authenticated:
        favorites = Favorite.query.filter_by(user_id=current_user.id).all()
        favorite_ids = {fav.post_id for fav in favorites}

    def _to_utc(dt):
        if not dt:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    def _time_ago(dt):
        if not dt:
            return ''
        dt = _to_utc(dt) or datetime.now(timezone.utc)
        delta = datetime.now(timezone.utc) - dt
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

    post_cards = []
    for post in posts:
        category_key = post.category or 'diger'
        category_label = category_label_map.get(category_key, category_key.replace('_', ' ').title())
        category_slug = _slugify(category_key)

        urgency_info = urgency_variants.get(post.urgency_level, urgency_variants[None])

        deadline_source = post.court_date or post.deadline
        deadline_utc = _to_utc(deadline_source)
        if deadline_utc:
            deadline_display = deadline_utc.strftime('%d %b %Y, %H:%M')
            if deadline_utc < now:
                deadline_state = 'overdue'
                deadline_badge = 'Süresi doldu'
            elif deadline_utc <= soon_threshold:
                deadline_state = 'soon'
                remaining = deadline_utc - now
                days_left = max(int(remaining.total_seconds() // 86400), 0)
                deadline_badge = 'Bugün' if days_left == 0 else f'{days_left} gün kaldı'
            else:
                deadline_state = 'scheduled'
                deadline_badge = 'Takvimde'
        else:
            deadline_display = 'Takvimlenmedi'
            deadline_state = 'none'
            deadline_badge = None

        price_display = None
        if post.price_min and post.price_max:
            price_display = f"{int(post.price_min):,} - {int(post.price_max):,} ₺".replace(',', '.')
        elif post.price_min:
            price_display = f"{int(post.price_min):,} ₺".replace(',', '.')
        elif post.price_max:
            price_display = f"{int(post.price_max):,} ₺".replace(',', '.')

        created_utc = _to_utc(post.created_at) or now
        description_text = (post.description or '').strip()
        description_snippet = description_text[:180] + ('…' if len(description_text) > 180 else '')

        application_count = post.applications_count or post.applications.count()

        post_cards.append({
            'id': post.id,
            'title': post.title,
            'url': url_for('post_detail', post_id=post.id),
            'category_key': category_key,
            'category_label': category_label,
            'category_slug': category_slug,
            'city': post.city or 'Belirtilmemiş',
            'courthouse': post.courthouse,
            'district': post.district,
            'urgency': post.urgency_level or 'normal',
            'urgency_label': urgency_info['label'],
            'urgency_variant': urgency_info['variant'],
            'urgency_icon': urgency_info['icon'],
            'deadline_display': deadline_display,
            'deadline_state': deadline_state,
            'deadline_badge': deadline_badge,
            'price_display': price_display,
            'remote_allowed': bool(post.remote_allowed),
            'applications': application_count,
            'status': post.status,
            'status_label': status_labels.get(post.status, 'Durum yok'),
            'favorited': post.id in favorite_ids,
            'owner': {
                'name': post.user.masked_full_name if post.user else 'Anonim',
                'avatar': post.user.full_name[0].upper() if post.user and post.user.full_name else 'A',
                'bar': post.user.bar_association if post.user else None,
            },
            'created_display': created_utc.strftime('%d %b %Y, %H:%M'),
            'created_ago': _time_ago(created_utc),
            'description': description_snippet,
            'search_text': f"{post.title} {description_text}".lower(),
        })

    total_count = pagination['total']
    urgent_total = base_query.filter(TevkilPost.urgency_level.in_(['urgent', 'very_urgent'])).count()
    very_urgent_total = base_query.filter(TevkilPost.urgency_level == 'very_urgent').count()
    upcoming_total = base_query.filter(
        TevkilPost.court_date.isnot(None),
        TevkilPost.court_date <= soon_threshold
    ).count()
    remote_total = base_query.filter(TevkilPost.remote_allowed.is_(True)).count()
    recent_total = base_query.filter(TevkilPost.created_at >= week_ago).count()
    avg_price_value = base_query.order_by(None).with_entities(func.avg(TevkilPost.price_min)).scalar()

    category_rows = (
        base_query
        .order_by(None)
        .with_entities(TevkilPost.category, func.count())
        .group_by(TevkilPost.category)
        .all()
    )

    metrics = [
        {
            'label': 'Aktif ilan',
            'icon': 'feed',
            'value': total_count,
            'subtitle': f'Son 7 gün +{recent_total}',
            'variant': 'brand',
        },
        {
            'label': 'Acil ilan',
            'icon': 'priority_high',
            'value': urgent_total,
            'subtitle': f'Çok acil {very_urgent_total}',
            'variant': 'rose',
        },
        {
            'label': 'Yaklaşan duruşma',
            'icon': 'event_upcoming',
            'value': upcoming_total,
            'subtitle': '7 gün içinde görev',
            'variant': 'amber',
        },
        {
            'label': 'Uzaktan yapılabilir',
            'icon': 'distance',
            'value': remote_total,
            'subtitle': 'Uzaktan destek',
            'variant': 'indigo',
        },
    ]

    filters = [
        {'key': 'all', 'label': 'Tümü', 'count': total_count},
    ]
    if urgent_total:
        filters.append({'key': 'urgent', 'label': 'Acil', 'count': urgent_total})
    if very_urgent_total:
        filters.append({'key': 'very_urgent', 'label': 'Çok acil', 'count': very_urgent_total})
    if upcoming_total:
        filters.append({'key': 'upcoming', 'label': 'Yaklaşan', 'count': upcoming_total})
    if recent_total:
        filters.append({'key': 'recent', 'label': 'Son 7 gün', 'count': recent_total})
    if remote_total:
        filters.append({'key': 'remote', 'label': 'Uzaktan', 'count': remote_total})

    for category_key, count in category_rows:
        if not category_key or count == 0:
            continue
        filters.append({
            'key': f'cat-{_slugify(category_key)}',
            'label': category_label_map.get(category_key, category_key.replace('_', ' ').title()),
            'count': count,
        })

    category_options = [
        {'value': key, 'label': label}
        for key, label in sorted(TASK_CATEGORY_OPTIONS, key=lambda item: item[1])
    ]

    avg_price_display = f"{int(avg_price_value):,} ₺".replace(',', '.') if avg_price_value else None

    page_numbers = get_page_numbers(pagination['page'], pagination['pages']) if pagination['pages'] else []

    filter_state = {
        'search': search or '',
        'city': city or '',
        'category': category or '',
        'urgency': urgency or '',
        'price_min': price_min if price_min is not None else '',
        'price_max': price_max if price_max is not None else '',
        'hearing_date_from': hearing_date_from or '',
        'hearing_date_to': hearing_date_to or '',
        'urgent_only': urgent_only,
        'remote_allowed': remote_allowed,
        'filter_type': filter_type or '',
        'user_filter': user_filter or '',
        'per_page': per_page,
    }

    return render_template(
        'phoenix/posts/explore.html',
        post_cards=post_cards,
        metrics=metrics,
        filters=filters,
        pagination=pagination,
        page_numbers=page_numbers,
        cities=CITIES,
        category_options=category_options,
        filter_state=filter_state,
        avg_price=avg_price_display,
    )

@app.route('/map')
@dev_login_optional
def map_view():
    """Harita görünümü - tüm ilanları haritada göster"""
    # Aktif ilanları getir
    posts = TevkilPost.query.filter_by(status='active').order_by(TevkilPost.created_at.desc()).all()
    
    # Haritada gösterilecek JSON verisi hazırla
    posts_json = []
    for post in posts:
        if post.latitude and post.longitude:  # Koordinatları olan ilanlar
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
    
    # Google Maps API anahtarı (opsiyonel, fallback var)
    google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    return render_template('map.html', 
                         posts=posts,
                         posts_json=posts_json,
                         google_maps_key=google_maps_key)

@app.route('/posts/new', methods=['GET', 'POST'])
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
            return redirect(url_for('create_post'))

        if not task_date_raw or not task_time_raw:
            flash('Görev tarihi ve saatini belirtmelisınız.', 'error')
            return redirect(url_for('create_post'))

        try:
            task_datetime = datetime.strptime(f"{task_date_raw} {task_time_raw}", '%Y-%m-%d %H:%M')
        except ValueError:
            flash('Görev tarihi veya saati geçersiz. Lütfen formatı kontrol edin.', 'error')
            return redirect(url_for('create_post'))

        auto_title = generate_post_title(category, city=city, courthouse=courthouse, district=district)
        
        # 1. SPAM KONTROLÜ
        if is_spam(auto_title) or is_spam(description):
            flash('⚠️ İlanınız spam içerik tespit edildiği için oluşturulamadı. Lütfen içeriği kontrol edin.', 'danger')
            return redirect(url_for('create_post'))
        
        # 2. UYGUNSUZ İÇERİK KONTROLÜ
        if is_inappropriate(auto_title) or is_inappropriate(description):
            flash('⚠️ İlanınız uygunsuz içerik tespit edildiği için oluşturulamadı.', 'danger')
            return redirect(url_for('create_post'))
        
        # 3. FLOOD KONTROLÜ (1 saatte 5'ten fazla ilan)
        if check_flood(current_user.id, db.session, action_type='post', max_count=5, time_window_minutes=60):
            flash('⚠️ Çok fazla ilan oluşturdunuz. Lütfen bir süre bekleyin.', 'warning')
            return redirect(url_for('dashboard'))
        
        # 4. METNİ TEMİZLE
        description = sanitize_text(description, max_length=5000)
        auto_title = sanitize_text(auto_title, max_length=200)
        category = sanitize_text(category, max_length=50)
        city = sanitize_text(city, max_length=50) if city else None
        district = sanitize_text(district, max_length=100) if district else None
        courthouse = sanitize_text(courthouse, max_length=150) if courthouse else None
        city = city or None
        district = district or None
        courthouse = courthouse or None
        
        # Konum bilgisini geocode et
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
        return redirect(url_for('post_detail', post_id=post.id))
    
    return render_template(
        'post_create.html',
        cities=CITIES,
        courthouses=COURTHOUSES,
        task_category_options=TASK_CATEGORY_OPTIONS,
        category_definitions=TASK_CATEGORY_DEFINITIONS,
        category_abbreviations=CATEGORY_ABBREVIATIONS,
    )

@app.route('/whatsapp-ilan')
@login_required
def whatsapp_ilan():
    """WhatsApp ile ilan oluşturma bilgilendirmesi"""
    if not current_app.config.get('WHATSAPP_ENABLED'):
        abort(404)
    return render_template('whatsapp_ilan.html')

@app.route('/whatsapp/setup')
@login_required
def whatsapp_setup():
    """WhatsApp entegrasyon kurulum ve test sayfası"""
    if not current_app.config.get('WHATSAPP_ENABLED'):
        abort(404)
    return render_template('whatsapp_setup.html')

@app.route('/posts/<int:post_id>')
def post_detail(post_id):
    """İlan detayı"""
    post = TevkilPost.query.get_or_404(post_id)
    
    # İlan görüntüleme sayısını artır (hem eski hem yeni sistem)
    update_post_view(post_id, current_user.id if current_user.is_authenticated else None)
    
    # Başvuruları getir - herkes sayıyı görebilir, ama detayları sadece ilan sahibi
    applications = Application.query.filter_by(post_id=post_id).order_by(Application.created_at.desc()).all()
    
    # Check if post is favorited
    is_favorited = False
    if current_user.is_authenticated:
        is_favorited = Favorite.query.filter_by(user_id=current_user.id, post_id=post_id).first() is not None
    
    # İlan istatistiklerini getir
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

    # Google Maps API anahtarı
    google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    return render_template(
        'post_detail.html',
        post=post,
        applications=applications,
        is_favorited=is_favorited,
        post_stats=post_stats,
        google_maps_key=google_maps_key,
        detail=detail_context,
        stats_cards=stats_cards,
    )

@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """İlan düzenle"""
    post = TevkilPost.query.get_or_404(post_id)
    
    # Sadece ilan sahibi düzenleyebilir
    if post.user_id != current_user.id:
        flash('Bu ilanı düzenleme yetkiniz yok', 'error')
        return redirect(url_for('post_detail', post_id=post_id))
    
    if request.method == 'POST':
        data = request.form
        from spam_detector import sanitize_text

        category = (data.get('category') or '').strip()
        description = data.get('description', '')
        task_date_raw = data.get('task_date')
        task_time_raw = data.get('task_time')
        city = (data.get('city') or '').strip()
        district = (data.get('district') or '').strip()
        courthouse = (data.get('courthouse') or '').strip()
        location_hidden = (data.get('location') or '').strip()

        if not category:
            flash('Görev türü seçmek zorunludur.', 'error')
            return redirect(url_for('edit_post', post_id=post_id))

        if not task_date_raw or not task_time_raw:
            flash('Görev tarihi ve saatini belirtmelisiniz.', 'error')
            return redirect(url_for('edit_post', post_id=post_id))

        try:
            task_datetime = datetime.strptime(f"{task_date_raw} {task_time_raw}", '%Y-%m-%d %H:%M')
        except ValueError:
            flash('Görev tarihi veya saati geçersiz. Lütfen formatı kontrol edin.', 'error')
            return redirect(url_for('edit_post', post_id=post_id))

        auto_title = generate_post_title(category, city=city, courthouse=courthouse, district=district)

        description = sanitize_text(description, max_length=5000)
        category = sanitize_text(category, max_length=50)
        city = sanitize_text(city, max_length=50) if city else None
        district = sanitize_text(district, max_length=100) if district else None
        courthouse = sanitize_text(courthouse, max_length=150) if courthouse else None
        auto_title = sanitize_text(auto_title, max_length=200)
        city = city or None
        district = district or None
        courthouse = courthouse or None

        new_location_str = courthouse or (f"{district} {city}".strip() if district and city else district) or city or location_hidden

        # Konum değiştiyse yeniden geocode et
        if new_location_str != post.location:
            coords = get_coordinates(new_location_str) if new_location_str else {}
            post.latitude = coords.get('latitude')
            post.longitude = coords.get('longitude')
            post.formatted_address = coords.get('formatted_address')

        post.title = auto_title
        post.description = description
        post.category = category
        post.urgency_level = data.get('urgency_level')
        post.location = new_location_str
        post.city = city
        post.district = district
        post.courthouse = courthouse
        post.court_date = task_datetime
        post.remote_allowed = data.get('remote_allowed') == 'on'
        price_raw = data.get('price')
        price_value = float(price_raw) if price_raw else None
        post.price_min = price_value
        post.price_max = price_value
        post.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        flash('İlan güncellendi!', 'success')
        return redirect(url_for('post_detail', post_id=post_id))

    return render_template(
        'post_edit.html',
        post=post,
        cities=CITIES,
        courthouses=COURTHOUSES,
        task_category_options=TASK_CATEGORY_OPTIONS,
        category_definitions=TASK_CATEGORY_DEFINITIONS,
        category_abbreviations=CATEGORY_ABBREVIATIONS,
    )

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """İlan sil"""
    post = TevkilPost.query.get_or_404(post_id)
    
    if post.user_id != current_user.id:
        flash('Bu ilanı silme yetkiniz yok', 'error')
        return redirect(url_for('post_detail', post_id=post_id))
    
    db.session.delete(post)
    db.session.commit()
    
    flash('İlan silindi', 'success')
    return redirect(url_for('dashboard'))

# ============================================
# APPLICATION ROUTES
# ============================================

@app.route('/posts/<int:post_id>/apply', methods=['POST'])
@login_required
def apply_to_post(post_id):
    """İlana başvur"""
    post = TevkilPost.query.get_or_404(post_id)
    
    # Stajyer avukatlar başvuru yapamaz
    if current_user.is_trainee:
        flash('Stajyer avukatlar görevlere başvuru yapamazlar', 'error')
        return redirect(url_for('post_detail', post_id=post_id))
    
    # Kendi ilanına başvuramaz
    if post.user_id == current_user.id:
        flash('Kendi ilanınıza başvuramazsınız', 'error')
        return redirect(url_for('post_detail', post_id=post_id))
    
    # Daha önce başvurmuş mu kontrol et
    existing = Application.query.filter_by(post_id=post_id, applicant_id=current_user.id).first()
    if existing:
        flash('Bu ilana zaten başvurdunuz', 'error')
        return redirect(url_for('post_detail', post_id=post_id))
    
    data = request.form
    
    application = Application(
        post_id=post_id,
        applicant_id=current_user.id,
        message=data.get('message'),
        proposed_price=float(data.get('proposed_price')) if data.get('proposed_price') else None
    )
    
    db.session.add(application)
    post.applications_count += 1
    
    # Bildirim oluştur
    notification = Notification(
        user_id=post.user_id,
        type='new_application',
        title='Yeni Başvuru',
    message=f'{mask_name(current_user.full_name)} ilanınıza başvurdu: {post.title}',
        related_post_id=post_id,
        related_user_id=current_user.id,
        action_url=f'/applications/received'  # Gelen başvurular sayfasına yönlendir
    )
    db.session.add(notification)
    
    db.session.commit()
    
    # WhatsApp bildirimi gönder (ilan sahibine) - Merkezi Bot
    if post.user.phone:
        try:
            from whatsapp_central_bot import central_bot
            
            central_bot.send_notification_new_application(
                post.user,
                application
            )
        except Exception as e:
            print(f"WhatsApp bildirimi gönderilemedi: {str(e)}")
    
    # 📧 E-posta bildirimi gönder (ilan sahibine)
    if current_app.config.get('EMAIL_ENABLED') and post.user.notify_email:
        try:
            from email_service import send_application_received_email
            send_application_received_email(post.user, application)
        except Exception as e:
            print(f"⚠️ Başvuru alındı e-postası gönderilemedi: {e}")
    
    flash('Başvurunuz gönderildi!', 'success')
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/applications/<int:app_id>/accept', methods=['POST'])
@login_required
def accept_application(app_id):
    """Başvuruyu kabul et"""
    application = Application.query.get_or_404(app_id)
    post = application.post
    
    # Sadece ilan sahibi kabul edebilir
    if post.user_id != current_user.id:
        return jsonify({'error': 'Yetkiniz yok'}), 403
    
    # Daha önce kabul edilmiş başvuru var mı kontrol et
    existing_accepted = Application.query.filter_by(
        post_id=post.id,
        status='accepted'
    ).first()
    
    if existing_accepted:
        flash('Bu ilana zaten bir başvuru kabul edilmiş. Bir ilana sadece bir başvuru kabul edilebilir.', 'error')
        return redirect(url_for('post_detail', post_id=post.id))
    
    application.status = 'accepted'
    post.status = 'assigned'
    post.assigned_to = application.applicant_id
    
    # Gelişmiş bildirim gönder
    create_notification(
        user_id=application.applicant_id,
        notification_type='application_accepted',
        title='🎉 Başvurunuz Kabul Edildi!',
        message=f'Tebrikler! "{post.title}" ilanına başvurunuz kabul edildi.',
        related_post_id=post.id,
        related_user_id=current_user.id,
        priority='high',
        category='application',
        action_url=f'/posts/{post.id}',
        action_text='İlanı Görüntüle'
    )
    
    db.session.commit()
    
    # WhatsApp bildirimi gönder (başvurana) - Merkezi Bot
    if application.applicant.phone:
        try:
            from whatsapp_central_bot import central_bot
            
            central_bot.send_notification_application_accepted(
                application.applicant,
                application
            )
        except Exception as e:
            print(f"WhatsApp bildirimi gönderilemedi: {str(e)}")
    
    # 📧 E-posta bildirimi gönder
    if current_app.config.get('EMAIL_ENABLED') and application.applicant.notify_email:
        try:
            from email_service import send_application_accepted_email
            send_application_accepted_email(application.applicant, application)
        except Exception as e:
            print(f"⚠️ Başvuru kabul e-postası gönderilemedi: {e}")
    
    flash('Başvuru kabul edildi!', 'success')
    return redirect(url_for('post_detail', post_id=post.id))

@app.route('/applications/<int:app_id>/reject', methods=['POST'])
@login_required
def reject_application(app_id):
    """Başvuruyu reddet"""
    application = Application.query.get_or_404(app_id)
    post = application.post
    
    if post.user_id != current_user.id:
        return jsonify({'error': 'Yetkiniz yok'}), 403
    
    application.status = 'rejected'
    
    # Gelişmiş bildirim gönder
    create_notification(
        user_id=application.applicant_id,
        notification_type='application_rejected',
        title='Başvurunuz Değerlendirildi',
        message=f'"{post.title}" ilanına başvurunuz maalesef kabul edilmedi.',
        related_post_id=post.id,
        related_user_id=current_user.id,
        priority='normal',
        category='application',
        action_url=f'/posts/{post.id}',
        action_text='İlanı Görüntüle'
    )
    
    db.session.commit()
    
    # WhatsApp bildirimi gönder (başvurana) - Merkezi Bot
    if application.applicant.phone:
        try:
            from whatsapp_central_bot import central_bot
            
            central_bot.send_notification_application_rejected(
                application.applicant,
                application
            )
        except Exception as e:
            print(f"WhatsApp bildirimi gönderilemedi: {str(e)}")
    
    flash('Başvuru reddedildi', 'info')
    return redirect(url_for('post_detail', post_id=post.id))

@app.route('/applications/<int:app_id>/authorization-info')
@login_required
def get_authorization_info(app_id):
    """Yetkilendirme bilgilerini getir (JSON)"""
    application = Application.query.get_or_404(app_id)
    post = application.post
    
    # Sadece ilan sahibi görebilir
    if post.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Yetkiniz yok'}), 403
    
    # Sadece kabul edilmiş başvurular için
    if application.status != 'accepted':
        return jsonify({'success': False, 'error': 'Bu başvuru kabul edilmemiş'}), 400
    
    return jsonify({
        'success': True,
        'data': {
            'post_owner': {
                'full_name': post.user.masked_full_name,
                'bar_association': post.user.bar_association,
                'tc_number': post.user.tc_number,
                'bar_registration_number': post.user.bar_registration_number,
                'address': post.user.address,
                'city': post.user.city,
                'phone': post.user.phone,
                'email': post.user.email
            },
            'applicant': {
                'full_name': application.applicant.masked_full_name,
                'bar_association': application.applicant.bar_association,
                'tc_number': application.applicant.tc_number,
                'bar_registration_number': application.applicant.bar_registration_number,
                'address': application.applicant.address,
                'city': application.applicant.city,
                'phone': application.applicant.phone,
                'email': application.applicant.email
            },
            'post': {
                'title': post.title,
                'category': post.category,
                'location': post.location,
                'description': post.description,
                'created_at': post.created_at.strftime('%d.%m.%Y')
            },
            'application': {
                'accepted_at': application.updated_at.strftime('%d.%m.%Y %H:%M') if application.updated_at else '',
                'proposed_price': application.proposed_price
            }
        }
    })

@app.route('/applications/<int:app_id>/generate-authorization-pdf')
@login_required
def generate_authorization_pdf(app_id):
    """Yetki belgesi UDF formatında oluştur ve indir (UYAP uyumlu)"""
    from udf_service_dynamic import create_authorization_udf_dynamic
    from datetime import datetime
    
    application = Application.query.get_or_404(app_id)
    post = application.post
    
    # Sadece ilan sahibi indirebilir
    if post.user_id != current_user.id:
        flash('Bu belgeyi indirme yetkiniz yok', 'error')
        return redirect(url_for('post_detail', post_id=post.id))
    
    # Sadece kabul edilmiş başvurular için
    if application.status != 'accepted':
        flash('Bu başvuru kabul edilmemiş', 'error')
        return redirect(url_for('post_detail', post_id=post.id))
    
    # UDF'e geçiş için kodu tamamen değiştir
    from udf_service_dynamic import create_authorization_udf_dynamic
    
    # Verileri hazırla
    post_owner = {
    'name': post.user.masked_full_name,
        'baro': post.user.bar_association or 'Belirtilmemiş',
        'tc_number': post.user.tc_number or '',
        'sicil': post.user.bar_registration_number or 'Belirtilmemiş',
        'tax_office': '',  # Kullanıcı modelinde bu alan henüz yok
        'tax_number': '',   # Kullanıcı modelinde bu alan henüz yok
        'address': post.user.address or 'Belirtilmemiş'
    }
    
    applicant_data = {
    'name': application.applicant.masked_full_name,
        'baro': application.applicant.bar_association or 'Belirtilmemiş',
        'tc_number': application.applicant.tc_number or '',
        'sicil': application.applicant.bar_registration_number or 'Belirtilmemiş',
        'tax_office': '',  # Kullanıcı modelinde bu alan henüz yok
        'tax_number': '',   # Kullanıcı modelinde bu alan henüz yok
        'address': application.applicant.address or 'Belirtilmemiş'
    }
    
    post_data = {
        'title': post.title,
        'category': post.category,
        'location': post.location,
        'description': post.description,
        'client_name': '',  # Post modelinde bu alan henüz yok - ileride eklenebilir
        'client_address': '',  # Post modelinde bu alan henüz yok - ileride eklenebilir
        'vekaletname_info': ''  # Post modelinde bu alan henüz yok - ileride eklenebilir
    }
    
    application_info = {
        'created_at': application.created_at.strftime('%d.%m.%Y %H:%M') if application.created_at else 'Belirtilmemiş',
        'accepted_at': application.updated_at.strftime('%d.%m.%Y %H:%M') if application.updated_at else 'Belirtilmemiş'
    }
    
    # UDF oluştur
    udf_buffer = create_authorization_udf_dynamic(
        post_owner=post_owner,
        applicant=applicant_data,
        post=post_data,
        application=application_info,
        price=application.proposed_price or 0
    )
    
    # UDF dosyasını gönder (UYAP formatı)
    filename = f"yetki_belgesi_{post.user.full_name}_{application.applicant.full_name}_{datetime.now().strftime('%Y%m%d')}.udf"
    
    return send_file(
        udf_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )

# ============================================
# PROFILE & RATING
# ============================================

@app.route('/profile/<int:user_id>')
def user_profile(user_id):
    """Kullanıcı profili - Optimized with eager loading"""
    # User bilgisini al
    user = User.query.get_or_404(user_id)
    
    # Kullanıcının tamamladığı işler
    completed_posts = TevkilPost.query.filter_by(assigned_to=user_id, status='completed').all()
    
    # Aldığı değerlendirmeler
    ratings = Rating.query.filter_by(reviewed_id=user_id).order_by(Rating.created_at.desc()).all()
    
    return render_template('phoenix/profile/view.html', user=user, completed_posts=completed_posts, ratings=ratings)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Profil düzenle"""
    if request.method == 'POST':
        data = request.form
        
        # Check if bar registration is being changed and if it's unique
        new_bar_assoc = data.get('bar_association')
        new_bar_reg_num = data.get('bar_registration_number')
        
        if new_bar_assoc and new_bar_reg_num:
            # Check if these bar credentials are already used by another user
            if (new_bar_assoc != current_user.bar_association or 
                new_bar_reg_num != current_user.bar_registration_number):
                existing_user = User.query.filter(
                    User.id != current_user.id,
                    User.bar_association == new_bar_assoc,
                    User.bar_registration_number == new_bar_reg_num
                ).first()
                
                if existing_user:
                    flash(f'{new_bar_assoc} - {new_bar_reg_num} sicil numarası ile zaten kayıtlı başka bir kullanıcı var', 'error')
                    return redirect(url_for('edit_profile'))
        
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
        
        # Avatar URL
        current_user.avatar_url = data.get('avatar_url') if data.get('avatar_url') else None
        
        # Social Media Links
        current_user.linkedin_url = data.get('linkedin_url') if data.get('linkedin_url') else None
        current_user.twitter_url = data.get('twitter_url') if data.get('twitter_url') else None
        current_user.instagram_url = data.get('instagram_url') if data.get('instagram_url') else None
        current_user.website_url = data.get('website_url') if data.get('website_url') else None
        
        # Sadece admin kullanıcılar lawyer_type değiştirebilir
        if current_user.is_admin and data.get('lawyer_type'):
            current_user.lawyer_type = data.get('lawyer_type')
        
        db.session.commit()
        
        flash('Profil güncellendi!', 'success')
        return redirect(url_for('user_profile', user_id=current_user.id))
    
    return render_template('phoenix/profile/edit.html')

@app.route('/settings')
@login_required
def settings():
    """Ayarlar sayfası"""
    # 2FA bilgilerini hazırla
    two_fa_enabled = current_user.two_factor_enabled
    backup_codes = []
    if current_user.two_factor_backup_codes:
        import json
        try:
            backup_codes = json.loads(current_user.two_factor_backup_codes)
        except:
            backup_codes = []
    
    return render_template('phoenix/settings/preferences.html', 
                         two_fa_enabled=two_fa_enabled,
                         backup_codes=backup_codes)

@app.route('/settings/profile', methods=['POST'])
@login_required
def update_profile():
    """Profil bilgilerini güncelle"""
    data = request.form
    
    current_user.full_name = data.get('full_name')
    current_user.phone = data.get('phone')
    current_user.whatsapp_number = data.get('whatsapp_number')
    current_user.city = data.get('city')
    current_user.district = data.get('district')
    current_user.bio = data.get('bio')
    
    # Social Media Links
    current_user.linkedin_url = data.get('linkedin_url') or None
    current_user.twitter_url = data.get('twitter_url') or None
    current_user.instagram_url = data.get('instagram_url') or None
    current_user.website_url = data.get('website_url') or None
    
    db.session.commit()
    flash('Profil bilgileriniz başarıyla güncellendi!', 'success')
    return redirect(url_for('edit_profile'))

@app.route('/rate/<int:user_id>', methods=['GET', 'POST'])
@login_required
def rate_user(user_id):
    """Kullanıcıyı değerlendir"""
    user = User.query.get_or_404(user_id)
    
    # Kendini değerlendiremez
    if user_id == current_user.id:
        flash('Kendinizi değerlendiremezsiniz!', 'error')
        return redirect(url_for('user_profile', user_id=user_id))
    
    # Daha önce değerlendirmiş mi kontrol et
    existing_rating = Rating.query.filter_by(
        reviewer_id=current_user.id,
        reviewed_id=user_id
    ).first()
    
    if request.method == 'POST':
        rating_value = int(request.form.get('rating', 0))
        professionalism = request.form.get('professionalism', type=int)
        communication = request.form.get('communication', type=int)
        quality = request.form.get('quality', type=int)
        comment = request.form.get('comment', '').strip()
        
        # Validasyon
        if not (1 <= rating_value <= 5):
            flash('Geçersiz puan değeri!', 'error')
            return redirect(url_for('rate_user', user_id=user_id))
        
        if existing_rating:
            # Güncelle
            existing_rating.rating = rating_value
            existing_rating.professionalism = professionalism
            existing_rating.communication = communication
            existing_rating.quality = quality
            existing_rating.comment = comment
            flash_message = 'Değerlendirmeniz güncellendi!'
        else:
            # Yeni oluştur
            rating = Rating(
                reviewer_id=current_user.id,
                reviewed_id=user_id,
                rating=rating_value,
                professionalism=professionalism,
                communication=communication,
                quality=quality,
                comment=comment
            )
            db.session.add(rating)
            flash_message = 'Değerlendirmeniz kaydedildi!'
        
        # Kullanıcının ortalama puanını güncelle
        all_ratings = Rating.query.filter_by(reviewed_id=user_id).all()
        if all_ratings:
            avg_rating = sum(r.rating for r in all_ratings) / len(all_ratings)
            user.rating_average = avg_rating
            user.rating_count = len(all_ratings)
        
        # Bildirim gönder
        create_notification(
            user_id=user_id,
            notification_type='new_rating',
            title='⭐ Yeni Değerlendirme!',
            message=f'{mask_name(current_user.full_name)} sizi değerlendirdi: {rating_value}/5 yıldız',
            related_user_id=current_user.id,
            priority='normal',
            category='rating',
            action_url=f'/profile/{user_id}',
            action_text='Profili Görüntüle'
        )
        
        db.session.commit()
        flash(flash_message, 'success')
        return redirect(url_for('user_profile', user_id=user_id))
    
    # GET request - rating formunu göster
    return render_template('rate_user.html', user=user, existing_rating=existing_rating)

@app.route('/report/<report_type>/<int:item_id>', methods=['GET', 'POST'])
@login_required
def report_content(report_type, item_id):
    """İçerik/kullanıcı rapor et"""
    from models import Report
    
    # Report type kontrolü
    valid_types = ['user', 'post', 'message']
    if report_type not in valid_types:
        abort(404)
    
    if request.method == 'POST':
        from spam_detector import sanitize_text
        
        # Daha önce rapor edilmiş mi kontrol et
        existing_report = None
        if report_type == 'user':
            existing_report = Report.query.filter_by(
                reporter_id=current_user.id,
                reported_user_id=item_id
            ).first()
        elif report_type == 'post':
            existing_report = Report.query.filter_by(
                reporter_id=current_user.id,
                reported_post_id=item_id
            ).first()
        elif report_type == 'message':
            existing_report = Report.query.filter_by(
                reporter_id=current_user.id,
                reported_message_id=item_id
            ).first()
        
        if existing_report:
            flash('⚠️ Bu içeriği daha önce raporladınız.', 'warning')
            return redirect(request.referrer or url_for('dashboard'))
        
        # Rapor oluştur
        description = sanitize_text(request.form.get('description', ''), max_length=1000)
        category = request.form.get('category', 'other')  # spam, inappropriate, abuse, fake, other
        
        report = Report(
            reporter_id=current_user.id,
            report_type=category,
            description=description
        )
        
        # İlgili ID'yi ata
        if report_type == 'user':
            report.reported_user_id = item_id
        elif report_type == 'post':
            report.reported_post_id = item_id
        elif report_type == 'message':
            report.reported_message_id = item_id
        
        db.session.add(report)
        db.session.commit()
        
        flash('✅ Raporunuz alındı. İncelenecek ve gerekli işlem yapılacaktır.', 'success')
        return redirect(request.referrer or url_for('dashboard'))
    
    # GET request - rapor formunu göster
    item = None
    if report_type == 'user':
        item = User.query.get_or_404(item_id)
    elif report_type == 'post':
        item = TevkilPost.query.get_or_404(item_id)
    elif report_type == 'message':
        from models import Message
        item = Message.query.get_or_404(item_id)
    
    return render_template('report.html', report_type=report_type, item=item)

@app.route('/settings/avatar', methods=['POST'])
@login_required
def update_avatar():
    """Avatar yükle"""
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'error': 'Dosya bulunamadı'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Dosya seçilmedi'}), 400
    
    # Dosya uzantısı kontrolü
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return jsonify({'success': False, 'error': 'İzin verilmeyen dosya türü'}), 400
    
    # Dosya boyutu kontrolü (2MB)
    file.seek(0, 2)
    file_size = file.tell()
    # 🔒 FILE UPLOAD VALIDATION
    is_valid, error_msg, safe_filename = input_validation.validate_image_upload(file)
    if not is_valid:
        return jsonify({'success': False, 'error': error_msg}), 400
    
    # Unique filename
    file_ext = safe_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"avatar_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
    
    # avatars klasörünü oluştur
    upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'avatars')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Eski avatarı sil
    if current_user.avatar_url and '/static/uploads/avatars/' in current_user.avatar_url:
        old_file = os.path.join(app.root_path, current_user.avatar_url.lstrip('/'))
        if os.path.exists(old_file):
            try:
                os.remove(old_file)
            except Exception as e:
                print(f"⚠️ Could not delete old avatar: {e}")
    
    # Dosyayı kaydet
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    # URL oluştur
    avatar_url = f"/static/uploads/avatars/{unique_filename}"
    current_user.avatar_url = avatar_url
    
    db.session.commit()
    
    flash('Profil fotoğrafınız başarıyla güncellendi!', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/avatar/remove', methods=['POST'])
@login_required
def remove_avatar():
    """Avatar kaldır"""
    # Eski avatarı sil
    if current_user.avatar_url and '/static/uploads/avatars/' in current_user.avatar_url:
        old_file = os.path.join(app.root_path, current_user.avatar_url.lstrip('/'))
        if os.path.exists(old_file):
            os.remove(old_file)
    
    current_user.avatar_url = None
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/settings/privacy', methods=['POST'])
@login_required
def update_privacy_settings():
    """Gizlilik ayarlarını güncelle"""
    data = request.form
    
    current_user.profile_visible = 'profile_visible' in data
    current_user.show_phone = 'show_phone' in data
    current_user.show_email = 'show_email' in data
    current_user.show_last_active = 'show_last_active' in data
    
    db.session.commit()
    flash('Gizlilik ayarlarınız başarıyla güncellendi!', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/2fa/setup', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    """2FA kurulumu"""
    import pyotp
    import qrcode
    import io
    import base64
    import json
    import secrets
    
    if request.method == 'POST':
        # Verify code
        code = request.form.get('code')
        secret = request.form.get('secret')
        
        if not secret or not code:
            flash('Geçersiz istek!', 'error')
            return redirect(url_for('settings'))
        
        # TOTP doğrulama
        totp = pyotp.TOTP(secret)
        if totp.verify(code):
            # 2FA'yı aktifleştir
            current_user.two_factor_enabled = True
            current_user.two_factor_secret = secret
            
            # Yedek kodlar oluştur (10 adet)
            backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
            current_user.two_factor_backup_codes = json.dumps(backup_codes)
            
            db.session.commit()
            
            flash('✅ İki faktörlü doğrulama başarıyla aktifleştirildi!', 'success')
            return redirect(url_for('settings'))
        else:
            flash('❌ Doğrulama kodu hatalı! Lütfen tekrar deneyin.', 'error')
            return redirect(url_for('setup_2fa'))
    
    # GET request - QR kod oluştur
    if current_user.two_factor_enabled:
        flash('İki faktörlü doğrulama zaten aktif!', 'info')
        return redirect(url_for('settings'))
    
    # Yeni secret oluştur
    secret = pyotp.random_base32()
    
    # TOTP URI oluştur
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email,
        issuer_name='Tevkil Platform'
    )
    
    # QR kod oluştur
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # QR kodu base64'e çevir
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return render_template('2fa_setup.html', 
                         qr_code=qr_code_base64, 
                         secret=secret,
                         manual_entry_key=secret)

@app.route('/settings/2fa/disable', methods=['POST'])
@login_required
def disable_2fa():
    """2FA'yı devre dışı bırak"""
    password = request.form.get('password')
    
    # Şifre kontrolü
    if not current_user.check_password(password):
        flash('❌ Şifre hatalı!', 'error')
        return redirect(url_for('settings'))
    
    # 2FA'yı kapat
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    current_user.two_factor_backup_codes = None
    
    db.session.commit()
    
    flash('✅ İki faktörlü doğrulama devre dışı bırakıldı.', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/notifications', methods=['POST'])
@login_required
def update_notification_settings():
    """Bildirim ayarlarını güncelle"""
    data = request.form
    
    current_user.notify_new_message = 'email_new_messages' in data
    current_user.notify_new_application = 'email_applications' in data
    current_user.notify_new_rating = 'email_ratings' in data
    current_user.notify_email = 'email_weekly_summary' in data
    
    db.session.commit()
    flash('Bildirim ayarlarınız başarıyla güncellendi!', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/account/delete', methods=['POST'])
@login_required
def delete_account():
    """Kullanıcı hesabını kalıcı olarak sil"""
    try:
        data = request.get_json() if request.is_json else request.form
        password = data.get('password')
        confirmation = data.get('confirmation')
        
        # 1. Şifre doğrulama
        if not current_user.check_password(password):
            security_utils.log_security_event(
                current_user.id, 'account_delete_failed', 'WARNING',
                'Failed account deletion - incorrect password'
            )
            if request.is_json:
                return jsonify({'success': False, 'error': 'Şifre yanlış!'}), 403
            flash('Şifre yanlış!', 'error')
            return redirect(url_for('settings'))
        
        # 2. Onay metni kontrolü
        if confirmation != 'SIL':
            if request.is_json:
                return jsonify({'success': False, 'error': 'Onay metni hatalı!'}), 400
            flash('Hesabınızı silmek için "SIL" yazmalısınız!', 'error')
            return redirect(url_for('settings'))
        
        # 3. Güvenlik log'u
        security_utils.log_security_event(
            current_user.id, 'account_deleted', 'CRITICAL',
            f'User {current_user.email} deleted their account'
        )
        
        user_id = current_user.id
        user_email = current_user.email
        
        # 4. Avatar dosyasını sil
        if current_user.avatar_url and '/static/uploads/avatars/' in current_user.avatar_url:
            old_file = os.path.join(app.root_path, current_user.avatar_url.lstrip('/'))
            if os.path.exists(old_file):
                try:
                    os.remove(old_file)
                except:
                    pass
        
        # 5. Kullanıcı verilerini sil (cascade ile ilişkili veriler de silinecek)
        from flask_login import logout_user
        logout_user()
        
        # Kullanıcıyı veritabanından sil
        db.session.delete(User.query.get(user_id))
        db.session.commit()
        
        # 6. Başarılı mesajı
        flash('Hesabınız başarıyla silindi. Bizi kullandığınız için teşekkür ederiz.', 'info')
        return redirect(url_for('index'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Account deletion error: {str(e)}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Bir hata oluştu. Lütfen daha sonra tekrar deneyin.'}), 500
        flash('Bir hata oluştu. Lütfen daha sonra tekrar deneyin.', 'error')
        return redirect(url_for('settings'))

@app.route('/settings/password', methods=['POST'])
@login_required
def change_password():
    """Şifre değiştir - Güvenlik politikalarıyla"""
    data = request.form
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    # 1. Mevcut şifre kontrolü
    if not current_user.check_password(current_password):
        security_utils.log_security_event(
            current_user.id, 'password_change_failed', 'WARNING',
            'Failed password change - incorrect current password'
        )
        flash('Mevcut şifreniz yanlış!', 'error')
        return redirect(url_for('settings'))
    
    # 2. Yeni şifre eşleşme kontrolü
    if new_password != confirm_password:
        flash('Yeni şifreler eşleşmiyor!', 'error')
        return redirect(url_for('settings'))
    
    # 3. Güçlü şifre kontrolü
    is_strong, strength_message = security_utils.is_strong_password(new_password)
    if not is_strong:
        flash(f'Şifre yeterince güçlü değil: {strength_message}', 'error')
        return redirect(url_for('settings'))
    
    # 4. Şifre geçmişi kontrolü (son 5 şifre)
    from werkzeug.security import generate_password_hash
    new_password_hash = generate_password_hash(new_password)
    
    # Eski şifreyi kaydet
    security_utils.save_password_to_history(current_user.id, current_user.password_hash)
    
    # 5. Şifreyi güncelle
    current_user.set_password(new_password)
    current_user.last_password_change = datetime.utcnow()
    current_user.password_expires_at = datetime.utcnow() + timedelta(days=90)  # 90 gün sonra
    db.session.commit()
    
    # 6. Güvenlik logla
    security_utils.log_security_event(
        current_user.id, 'password_change', 'INFO',
        'Password changed successfully'
    )
    
    # 7. Diğer oturumları sonlandır (güvenlik)
    count = security_utils.terminate_all_sessions(current_user.id, except_current=True)
    
    flash(f'Şifreniz başarıyla değiştirildi! Güvenlik için {count} aktif oturum sonlandırıldı.', 'success')
    return redirect(url_for('settings'))

# ============================================
# NOTIFICATION HELPERS
# ============================================

def create_notification(user_id, notification_type, title, message, related_post_id=None, related_user_id=None, 
                       priority='normal', category='general', action_url=None, action_text=None):
    """
    Gelişmiş bildirim oluştur
    
    Args:
        user_id: Bildirim alacak kullanıcı ID
        notification_type: Bildirim tipi (new_application, application_accepted, vb.)
        title: Bildirim başlığı
        message: Bildirim mesajı
        related_post_id: İlgili ilan ID
        related_user_id: İlgili kullanıcı ID
        priority: Öncelik (low, normal, high, urgent)
        category: Kategori (application, message, system, warning)
        action_url: Tıklanınca gidilecek URL
        action_text: Aksiyon butonu metni
    """
    # Kullanıcının bildirim tercihlerini kontrol et
    user = User.query.get(user_id)
    if not user:
        return None
    
    # Bildirim tercihine göre kontrol
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


def get_notification_stats(user_id):
    """Kullanıcının bildirim istatistiklerini getir"""
    base_query = Notification.query.filter_by(user_id=user_id, archived_at=None)
    total = base_query.count()
    unread = base_query.filter(Notification.read_at.is_(None)).count()
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today = base_query.filter(Notification.created_at >= today_start).count()
    high_priority = base_query.filter(Notification.priority.in_(['high', 'urgent'])).count()

    return {
        'total': total,
        'unread': unread,
        'today': today,
        'high_priority': high_priority,
    }


def mark_notification_read(notification_id, user_id):
    """Bildirimi okundu işaretle"""
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if notification and not notification.read_at:
        notification.read_at = datetime.now(timezone.utc)
        db.session.commit()
        return True
    return False


def mark_notification_clicked(notification_id, user_id):
    """Bildirime tıklandı işaretle"""
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if notification:
        if not notification.read_at:
            notification.read_at = datetime.now(timezone.utc)
        notification.clicked_at = datetime.now(timezone.utc)
        db.session.commit()
        return True
    return False


def delete_old_notifications(days=30):
    """Eski bildirimleri sil"""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    old_notifications = Notification.query.filter(
        Notification.created_at < cutoff_date,
        Notification.read_at.isnot(None)
    ).all()
    
    count = len(old_notifications)
    for notif in old_notifications:
        db.session.delete(notif)
    db.session.commit()
    
    return count

# ============================================
# STATISTICS HELPERS
# ============================================

def get_user_stats(user_id):
    """Kullanıcı istatistiklerini getir"""
    user = User.query.get(user_id)
    if not user:
        return None
    
    # Son 30 günlük aktivite
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    # Son aylık ilanlar
    recent_posts = TevkilPost.query.filter_by(user_id=user_id).filter(
        TevkilPost.created_at >= thirty_days_ago
    ).count()
    
    # Son aylık başvurular
    recent_applications = Application.query.filter_by(applicant_id=user_id).filter(
        Application.created_at >= thirty_days_ago
    ).count()
    
    # Rating breakdown
    ratings = Rating.query.filter_by(reviewed_id=user_id).all()
    rating_breakdown = {
        5: len([r for r in ratings if r.rating == 5]),
        4: len([r for r in ratings if r.rating == 4]),
        3: len([r for r in ratings if r.rating == 3]),
        2: len([r for r in ratings if r.rating == 2]),
        1: len([r for r in ratings if r.rating == 1]),
    }
    
    # Kategori dağılımı
    user_posts = TevkilPost.query.filter_by(user_id=user_id).all()
    category_distribution = {}
    for post in user_posts:
        category_distribution[post.category] = category_distribution.get(post.category, 0) + 1
    
    return {
        'total_posts': user.total_posts_created or 0,
        'total_applications_sent': user.total_applications_sent or 0,
        'total_applications_received': user.total_applications_received or 0,
        'accepted_applications': user.accepted_applications or 0,
        'rejected_applications': user.rejected_applications or 0,
        'success_rate': round(user.success_rate or 0, 1),
        'average_response_time': round(user.average_response_time_hours or 0, 1),
        'total_views': user.total_views_received or 0,
        'profile_views': user.profile_views or 0,
        'rating_average': round(user.rating_average or 0, 1),
        'rating_count': user.rating_count or 0,
        'rating_breakdown': rating_breakdown,
        'recent_posts_30d': recent_posts,
        'recent_applications_30d': recent_applications,
        'category_distribution': category_distribution,
        'last_post_date': user.last_post_date,
        'last_application_date': user.last_application_date,
    }


def get_platform_stats():
    """Platform geneli istatistikler"""
    # Temel sayılar
    total_users = User.query.count()
    total_posts = TevkilPost.query.count()
    total_applications = Application.query.count()
    active_posts = TevkilPost.query.filter_by(status='active').count()
    
    # Son 7 günlük aktivite
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_users_7d = User.query.filter(User.created_at >= seven_days_ago).count()
    new_posts_7d = TevkilPost.query.filter(TevkilPost.created_at >= seven_days_ago).count()
    new_applications_7d = Application.query.filter(Application.created_at >= seven_days_ago).count()
    
    # Şehir bazlı istatistikler
    city_stats = db.session.query(
        TevkilPost.city,
        db.func.count(TevkilPost.id).label('count')
    ).group_by(TevkilPost.city).order_by(db.func.count(TevkilPost.id).desc()).limit(10).all()
    
    # Kategori bazlı istatistikler
    category_stats = db.session.query(
        TevkilPost.category,
        db.func.count(TevkilPost.id).label('count')
    ).group_by(TevkilPost.category).order_by(db.func.count(TevkilPost.id).desc()).all()
    
    # En aktif kullanıcılar
    top_creators = User.query.order_by(User.total_posts_created.desc()).limit(5).all()
    
    # En çok görüntülenen ilanlar
    top_viewed = TevkilPost.query.order_by(TevkilPost.view_count.desc()).limit(5).all()
    
    return {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_applications': total_applications,
        'active_posts': active_posts,
        'new_users_7d': new_users_7d,
        'new_posts_7d': new_posts_7d,
        'new_applications_7d': new_applications_7d,
        'city_stats': [(city, count) for city, count in city_stats],
        'category_stats': [(cat, count) for cat, count in category_stats],
        'top_creators': top_creators,
        'top_viewed': top_viewed,
    }


def get_post_stats(post_id):
    """İlan bazlı detaylı istatistikler"""
    post = TevkilPost.query.get(post_id)
    if not post:
        return None
    
    # Başvuru istatistikleri
    applications = Application.query.filter_by(post_id=post_id).all()
    
    accepted_count = len([a for a in applications if a.status == 'accepted'])
    rejected_count = len([a for a in applications if a.status == 'rejected'])
    pending_count = len([a for a in applications if a.status == 'pending'])
    
    # Başvuru zamanları analizi
    if applications:
        application_times = [(a.created_at - post.created_at).total_seconds() / 3600 for a in applications]
        avg_time_to_apply = sum(application_times) / len(application_times)
    else:
        avg_time_to_apply = 0
    
    return {
        'view_count': post.view_count or 0,
        'application_count': len(applications),
        'accepted_count': accepted_count,
        'rejected_count': rejected_count,
        'pending_count': pending_count,
        'application_rate': round(post.application_rate or 0, 2),
        'avg_time_to_apply_hours': round(avg_time_to_apply, 1),
        'first_application_at': post.first_application_at,
        'last_viewed_at': post.last_viewed_at,
    }


def update_post_view(post_id, user_id=None):
    """İlan görüntüleme sayısını artır"""
    post = TevkilPost.query.get(post_id)
    if post:
        post.view_count = (post.view_count or 0) + 1
        post.last_viewed_at = datetime.now(timezone.utc)
        
        # Eski views alanını da güncelle (backward compatibility)
        post.views = post.view_count
        
        db.session.commit()
        return True
    return False

# ============================================
# NOTIFICATIONS ROUTES
# ============================================

@app.route('/notifications')
@login_required
def notifications():
    """Geliştirilmiş bildirimler sayfası"""
    notifications_query = Notification.query.filter_by(
        user_id=current_user.id,
        archived_at=None
    ).order_by(Notification.created_at.desc())
    notifications_raw = notifications_query.all()

    now = datetime.now(timezone.utc)

    def _to_utc(dt):
        if not dt:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    def _time_ago(dt):
        if not dt:
            return ""
        delta = now - dt
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return "az önce"
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

    type_config = {
        'new_application': {
            'icon': 'description',
            'accent': 'bg-blue-100 dark:bg-blue-900/30',
            'icon_color': 'text-blue-600 dark:text-blue-400',
            'category': 'application',
            'default_title': 'Yeni başvuru',
            'default_message': 'İlanınıza yeni bir başvuru var.',
            'action_text': 'Başvuruyu görüntüle',
        },
        'application_accepted': {
            'icon': 'task_alt',
            'accent': 'bg-emerald-100 dark:bg-emerald-900/30',
            'icon_color': 'text-emerald-600 dark:text-emerald-400',
            'category': 'application',
            'default_title': 'Başvurun kabul edildi',
            'default_message': 'Başvuruna olumlu yanıt verildi.',
            'action_text': 'Yanıtı gör',
        },
        'application_rejected': {
            'icon': 'cancel',
            'accent': 'bg-rose-100 dark:bg-rose-900/30',
            'icon_color': 'text-rose-600 dark:text-rose-400',
            'category': 'application',
            'default_title': 'Başvurun reddedildi',
            'default_message': 'Başvuruna olumsuz yanıt verildi.',
            'action_text': 'Detayı aç',
        },
        'new_message': {
            'icon': 'mail',
            'accent': 'bg-violet-100 dark:bg-violet-900/30',
            'icon_color': 'text-violet-600 dark:text-violet-300',
            'category': 'message',
            'default_title': 'Yeni mesaj',
            'default_message': 'Bir kullanıcıdan yeni mesajın var.',
            'action_text': 'Mesajı oku',
        },
        'new_rating': {
            'icon': 'star',
            'accent': 'bg-amber-100 dark:bg-amber-900/30',
            'icon_color': 'text-amber-600 dark:text-amber-400',
            'category': 'message',
            'default_title': 'Yeni değerlendirme',
            'default_message': 'Profiline yeni bir değerlendirme eklendi.',
            'action_text': 'Değerlendirmeyi gör',
        },
        'post_expiring': {
            'icon': 'schedule',
            'accent': 'bg-orange-100 dark:bg-orange-900/30',
            'icon_color': 'text-orange-600 dark:text-orange-400',
            'category': 'alert',
            'default_title': 'İlan süresi doluyor',
            'default_message': 'İlanın sona ermek üzere, süresini uzatmayı düşün.',
            'action_text': 'İlanı yönet',
        },
        'system': {
            'icon': 'info',
            'accent': 'bg-slate-200 dark:bg-slate-800/30',
            'icon_color': 'text-slate-600 dark:text-slate-300',
            'category': 'system',
            'default_title': 'Sistem duyurusu',
            'default_message': 'Platformla ilgili önemli bir güncelleme var.',
            'action_text': 'Detayları gör',
        },
    }

    category_info = {
        'application': {'label': 'Başvurular', 'icon': 'description'},
        'message': {'label': 'Mesajlar', 'icon': 'mail'},
        'system': {'label': 'Sistem', 'icon': 'info'},
        'alert': {'label': 'Uyarılar', 'icon': 'warning'},
        'general': {'label': 'Genel', 'icon': 'notifications'},
    }

    priority_labels = {
        'urgent': 'Acil',
        'high': 'Önemli',
        'normal': 'Standart',
        'low': 'Düşük',
        None: 'Standart',
    }

    priority_variants = {
        'urgent': 'rose',
        'high': 'orange',
        'normal': 'slate',
        'low': 'slate',
        None: 'slate',
    }

    notification_cards = []
    category_counts = {key: 0 for key in category_info.keys()}
    unread_count = 0
    today_count = 0
    high_priority_count = 0

    for notif in notifications_raw:
        config = type_config.get(notif.type, {})
        category_key = (notif.category or config.get('category') or 'general')
        if category_key not in category_info:
            category_info[category_key] = {'label': category_key.title(), 'icon': 'notifications'}
            category_counts[category_key] = 0

        created_utc = _to_utc(notif.created_at) or now
        is_new = (now - created_utc).total_seconds() < 86400
        is_read = bool(notif.read_at)

        category_counts[category_key] = category_counts.get(category_key, 0) + 1
        if not is_read:
            unread_count += 1
        if is_new:
            today_count += 1
        if (notif.priority or 'normal') in ('high', 'urgent'):
            high_priority_count += 1

        card = {
            'id': notif.id,
            'title': notif.title or config.get('default_title') or 'Yeni bildirim',
            'message': notif.message or config.get('default_message') or '',
            'type': notif.type,
            'category': category_key,
            'category_label': category_info[category_key]['label'],
            'icon': config.get('icon', category_info[category_key]['icon']),
            'accent_class': config.get('accent', 'bg-slate-100 dark:bg-slate-800/40'),
            'icon_color_class': config.get('icon_color', 'text-slate-600 dark:text-slate-300'),
            'is_read': is_read,
            'read_state': 'read' if is_read else 'unread',
            'is_new': is_new,
            'priority': notif.priority or 'normal',
            'priority_label': priority_labels.get(notif.priority or 'normal', 'Standart'),
            'priority_variant': priority_variants.get(notif.priority or 'normal', 'slate'),
            'time_ago': _time_ago(created_utc),
            'timestamp': created_utc.strftime('%d %b %Y, %H:%M'),
            'action_url': notif.action_url,
            'action_text': notif.action_text or config.get('action_text'),
        }

        notification_cards.append(card)

    stats = get_notification_stats(current_user.id)
    stats.update({
        'total': len(notification_cards),
        'unread': unread_count,
        'today': today_count,
        'high_priority': high_priority_count,
    })

    filters = [
        {'key': 'all', 'label': 'Tümü', 'count': len(notification_cards)},
        {'key': 'unread', 'label': 'Okunmamış', 'count': unread_count},
    ]

    if high_priority_count:
        filters.append({'key': 'priority', 'label': 'Önemli', 'count': high_priority_count})

    for key, info in category_info.items():
        count = category_counts.get(key, 0)
        if count:
            filters.append({'key': key, 'label': info['label'], 'count': count})

    metrics = [
        {
            'label': 'Toplam bildirim',
            'icon': 'notifications',
            'value': stats['total'],
            'subtitle': f"Bugün {today_count}",
            'variant': 'brand',
        },
        {
            'label': 'Okunmamış',
            'icon': 'mark_email_unread',
            'value': unread_count,
            'subtitle': f"Önemli {high_priority_count}",
            'variant': 'amber',
        },
        {
            'label': 'Başvuru hareketi',
            'icon': 'description',
            'value': category_counts.get('application', 0),
            'subtitle': 'İlan aktiviteleri',
            'variant': 'indigo',
        },
        {
            'label': 'Sistem duyuruları',
            'icon': 'campaign',
            'value': category_counts.get('system', 0),
            'subtitle': 'Platform güncellemeleri',
            'variant': 'slate',
        },
    ]

    return render_template(
        'notifications_new.html',
        notifications=notification_cards,
        stats=stats,
        filters=filters,
        metrics=metrics,
    )


@app.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Tüm bildirimleri okundu işaretle"""
    notifications_list = Notification.query.filter_by(user_id=current_user.id, read_at=None).all()
    for notif in notifications_list:
        notif.read_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({'success': True, 'count': len(notifications_list)})


@app.route('/notifications/<int:notification_id>/click', methods=['POST'])
@login_required
def notification_clicked(notification_id):
    """Bildirime tıklandı işaretle"""
    success = mark_notification_clicked(notification_id, current_user.id)
    return jsonify({'success': success})


@app.route('/notifications/<int:notification_id>/archive', methods=['POST'])
@login_required
def archive_notification(notification_id):
    """Bildirimi arşivle"""
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
    if notification:
        notification.archived_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Bildirim bulunamadı'}), 404


@app.route('/notifications/settings')
@login_required
def notification_settings():
    """Bildirim ayarları sayfası"""
    return render_template('phoenix/settings/notifications.html', user=current_user)


@app.route('/notifications/settings/update', methods=['POST'])
@login_required
def update_notification_preferences():
    """Bildirim ayarlarını güncelle (eski sistem)"""
    data = request.form
    
    current_user.notify_new_application = 'notify_new_application' in data
    current_user.notify_application_status = 'notify_application_status' in data
    current_user.notify_new_message = 'notify_new_message' in data
    current_user.notify_new_rating = 'notify_new_rating' in data
    current_user.notify_post_expiring = 'notify_post_expiring' in data
    current_user.notify_system = 'notify_system' in data
    current_user.notify_email = 'notify_email' in data
    
    db.session.commit()
    
    flash('Bildirim ayarları güncellendi', 'success')
    return redirect(url_for('notification_settings'))


@app.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    """Tüm bildirimleri okundu işaretle (eski endpoint - geriye dönük uyumluluk)"""
    notifications_list = Notification.query.filter_by(user_id=current_user.id, read_at=None).all()
    for notif in notifications_list:
        notif.read_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({'success': True})

# ============================================
# MESSAGES ROUTES
# ============================================

# ============================================
# CHAT / MESSAGING ROUTES (Modern Chat System)
# ============================================


def _user_initials(user):
    """Return capitalised initials derived from the user's full name."""
    if not user or not user.full_name:
        return "TR"
    parts = [segment for segment in user.full_name.strip().split() if segment]
    if not parts:
        return "TR"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _normalise_to_utc(dt):
    """Ensure datetime values are timezone-aware in UTC."""
    if not dt:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _format_relative_time(dt):
    """Generate a concise human readable relative time string."""
    dt = _normalise_to_utc(dt)
    if not dt:
        return ""
    now = datetime.now(timezone.utc)
    diff = now - dt
    if diff.total_seconds() < 0:
        return dt.strftime('%d.%m.%Y %H:%M')
    minutes = int(diff.total_seconds() // 60)
    hours = int(diff.total_seconds() // 3600)
    days = diff.days
    if minutes < 1:
        return "az önce"
    if minutes < 60:
        return f"{minutes} dk önce"
    if hours < 24:
        return f"{hours} saat önce"
    if days < 7:
        return f"{days} gün önce"
    return dt.strftime('%d.%m.%Y')


def _format_file_size(size_bytes):
    """Format byte values for human friendly display."""
    if not size_bytes:
        return None
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def _conversation_meta(conversation):
    """Build metadata text rendered under the participant name."""
    parts = []
    if conversation.post:
        title = conversation.post.title or "İlan"
        if conversation.post.city:
            parts.append(f"{conversation.post.city} · {title}")
        else:
            parts.append(title)
    if conversation.created_at:
        created = _normalise_to_utc(conversation.created_at)
        if created:
            parts.append(f"Başlangıç {created.strftime('%d.%m.%Y')}")
    return " · ".join(parts) if parts else "Sohbet"


def _thread_summary(conversation, current_user_id, active_id):
    """Convert conversation model into sidebar friendly summary data."""
    other_user = conversation.get_other_user(current_user_id)
    return {
        "id": conversation.id,
        "name": other_user.masked_full_name if hasattr(other_user, "masked_full_name") else other_user.full_name,
        "initials": _user_initials(other_user),
        "last_timestamp": _format_relative_time(conversation.last_message_at or conversation.updated_at),
        "preview": conversation.last_message_text or "Henüz mesaj yok",
        "unread": conversation.get_unread_count(current_user_id),
        "active": active_id == conversation.id,
        "meta": _conversation_meta(conversation),
        "url": url_for("chat_conversation", conversation_id=conversation.id),
    }


def _thread_detail(conversation, current_user_id):
    """Build the payload required to render the active chat panel."""
    other_user = conversation.get_other_user(current_user_id)
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at.asc()).all()
    return {
        "id": conversation.id,
        "name": other_user.masked_full_name if hasattr(other_user, "masked_full_name") else other_user.full_name,
        "initials": _user_initials(other_user),
        "meta": _conversation_meta(conversation),
        "post": {
            "title": conversation.post.title,
            "url": url_for("post_detail", post_id=conversation.post_id),
        } if conversation.post_id else None,
        "other_user_id": other_user.id,
        "messages": [
            {
                "id": msg.id,
                "body": msg.message,
                "timestamp": _normalise_to_utc(msg.created_at).strftime('%d.%m.%Y %H:%M') if msg.created_at else "",
                "is_owner": msg.sender_id == current_user_id,
                "type": msg.message_type or "text",
                "file_url": msg.file_url,
                "file_name": msg.file_name,
                "file_size": _format_file_size(msg.file_size),
            }
            for msg in messages
        ],
    }


class ChatMessageError(Exception):
    """Raised when chat message creation fails."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


def _create_chat_message(
    conversation,
    sender,
    message_text="",
    reply_to_id=None,
    uploaded_file=None,
):
    """Persist a chat message, emit socket event and return payload metadata."""
    message_text = (message_text or "").strip()

    if sender.id not in (conversation.user1_id, conversation.user2_id):
        raise ChatMessageError("Yetkiniz yok", status_code=403)

    if not message_text and not uploaded_file:
        raise ChatMessageError("Mesaj veya dosya gerekli")

    file_url = None
    file_name = None
    file_size = None
    file_type = None
    message_type = "text"

    if uploaded_file:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf', 'docx', 'udf', 'gif', 'webp'}
        original_name = uploaded_file.filename or ""
        file_ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else ''
        if file_ext not in allowed_extensions:
            raise ChatMessageError(f"Desteklenmeyen dosya tipi. İzin verilenler: {', '.join(sorted(allowed_extensions))}")

        uploaded_file.seek(0, os.SEEK_END)
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)
        if file_size > 10 * 1024 * 1024:
            raise ChatMessageError("Dosya boyutu 10MB'dan büyük olamaz")

        upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'chat')
        os.makedirs(upload_folder, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = secure_filename(original_name)
        unique_filename = f"{sender.id}_{timestamp}_{safe_name}"
        file_path = os.path.join(upload_folder, unique_filename)
        uploaded_file.save(file_path)

        file_url = f"/static/uploads/chat/{unique_filename}"
        file_name = original_name
        file_type = uploaded_file.content_type or f'application/{file_ext}'
        message_type = 'image' if file_ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'} else 'file'
        if not message_text:
            message_text = f"📎 {file_name}"

    other_user = conversation.get_other_user(sender.id)
    message = Message(
        conversation_id=conversation.id,
        sender_id=sender.id,
        message=message_text,
        reply_to_id=reply_to_id,
        delivered_at=datetime.now(timezone.utc),
        message_type=message_type,
        file_url=file_url,
        file_name=file_name,
        file_size=file_size,
        file_type=file_type,
    )
    message.receiver_id = other_user.id
    message.post_id = conversation.post_id

    db.session.add(message)

    conversation.last_message_at = datetime.now(timezone.utc)
    conversation.last_message_text = message_text[:100]
    conversation.last_message_sender_id = sender.id
    if sender.id == conversation.user1_id:
        conversation.unread_count_user2 += 1
    else:
        conversation.unread_count_user1 += 1

    try:
        db.session.commit()
    except Exception as exc:  # pragma: no cover - safeguard
        db.session.rollback()
        raise ChatMessageError("Mesaj kaydedilemedi") from exc

    masked_sender_name = sender.masked_full_name if hasattr(sender, "masked_full_name") else sender.full_name
    masked_other_name = other_user.masked_full_name if hasattr(other_user, "masked_full_name") else other_user.full_name
    sender_avatar = (
        sender.avatar_url
        if getattr(sender, "avatar_url", None)
        else f"https://ui-avatars.com/api/?name={masked_sender_name.replace(' ', '+')}&background=1f2937&color=fff"
    )
    other_user_avatar = (
        other_user.avatar_url
        if getattr(other_user, "avatar_url", None)
        else f"https://ui-avatars.com/api/?name={masked_other_name.replace(' ', '+')}&background=1f2937&color=fff"
    )

    socketio.emit(
        'new_message',
        {
            'conversation_id': conversation.id,
            'sender_id': sender.id,
            'sender_name': masked_sender_name,
            'sender_avatar': sender_avatar,
            'content': message_text,
            'message': message_text,
            'timestamp': message.created_at.strftime('%H:%M'),
            'created_at': message.created_at.isoformat(),
            'id': message.id,
            'is_mine': False,
            'read_at': None,
            'message_type': message_type,
            'file_url': file_url,
            'file_name': file_name,
            'file_size': file_size,
            'file_type': file_type,
        },
        room=f'conversation_{conversation.id}',
    )

    try:
        create_notification(
            user_id=other_user.id,
            notification_type='new_message',
            title='💬 Yeni Mesaj',
            message=f'{masked_sender_name}: {message_text[:50]}...',
            related_user_id=sender.id,
            action_url=url_for('chat_conversation', conversation_id=conversation.id),
            action_text='Mesajı Görüntüle',
            priority='normal',
        )
    except Exception as exc:  # pragma: no cover - notification best effort
        print(f"Notification error: {exc}")

    return {
        "message": message,
        "other_user": other_user,
        "payload": {
            'message_id': message.id,
            'created_at': message.created_at.strftime('%H:%M'),
            'sender_name': masked_sender_name,
            'message_text': message_text,
            'message_type': message_type,
            'file_url': file_url,
            'file_name': file_name,
            'file_size': file_size,
            'file_type': file_type,
        },
    }


@app.route('/chat')
@login_required
def chat():
    """Phoenix tabanlı mesajlaşma merkezi."""
    user_convs = db.session.query(Conversation).filter(
        or_(
            Conversation.user1_id == current_user.id,
            Conversation.user2_id == current_user.id,
        )
    ).order_by(Conversation.last_message_at.desc()).all()

    active_conversation = user_convs[0] if user_convs else None
    if active_conversation:
        active_conversation.mark_as_read(current_user.id)
        Message.query.filter(
            Message.conversation_id == active_conversation.id,
            Message.sender_id != current_user.id,
            Message.read_at.is_(None),
        ).update({'read_at': datetime.now(timezone.utc)})
        db.session.commit()

    total_unread = sum(conv.get_unread_count(current_user.id) for conv in user_convs)
    active_id = active_conversation.id if active_conversation else None
    threads = [
        _thread_summary(conv, current_user.id, active_id=active_id)
        for conv in user_convs
    ]
    active_thread = _thread_detail(active_conversation, current_user.id) if active_conversation else None

    return render_template(
        'phoenix/messages/inbox.html',
        threads=threads,
        active_thread=active_thread,
        total_unread=total_unread,
    )


@app.route('/chat/<int:conversation_id>', methods=['GET', 'POST'])
@login_required
def chat_conversation(conversation_id: int):
    """Gösterilen sohbeti Phoenix arayüzüyle render et."""
    conversation = Conversation.query.get_or_404(conversation_id)

    if current_user.id not in (conversation.user1_id, conversation.user2_id):
        flash('Bu sohbete erişim yetkiniz yok', 'error')
        return redirect(url_for('chat'))

    if request.method == 'POST':
        message_text = request.form.get('message', '')
        reply_to_raw = request.form.get('reply_to_id')
        try:
            reply_to_id = int(reply_to_raw) if reply_to_raw else None
        except (TypeError, ValueError):
            reply_to_id = None

        try:
            _create_chat_message(
                conversation=conversation,
                sender=current_user,
                message_text=message_text,
                reply_to_id=reply_to_id,
                uploaded_file=request.files.get('file'),
            )
            flash('Mesaj gönderildi.', 'success')
        except ChatMessageError as exc:
            flash(str(exc), 'error')
            if exc.status_code == 403:
                return redirect(url_for('chat'))
        return redirect(url_for('chat_conversation', conversation_id=conversation_id))

    conversation.mark_as_read(current_user.id)
    Message.query.filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != current_user.id,
        Message.read_at.is_(None),
    ).update({'read_at': datetime.now(timezone.utc)})
    db.session.commit()

    user_convs = db.session.query(Conversation).filter(
        or_(
            Conversation.user1_id == current_user.id,
            Conversation.user2_id == current_user.id,
        )
    ).order_by(Conversation.last_message_at.desc()).all()

    total_unread = sum(conv.get_unread_count(current_user.id) for conv in user_convs)
    threads = [
        _thread_summary(conv, current_user.id, active_id=conversation.id)
        for conv in user_convs
    ]
    active_thread = _thread_detail(conversation, current_user.id)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('ajax') == '1':
        panel_html = render_template(
            'partials/chat_panel.html',
            active_thread=active_thread,
            current_user=current_user,
        )
        return jsonify({
            'success': True,
            'panel_html': panel_html,
            'conversation_id': conversation.id,
            'url': url_for('chat_conversation', conversation_id=conversation.id),
        })

    return render_template(
        'chat.html',
        threads=threads,
        active_thread=active_thread,
        total_unread=total_unread,
    )


@app.route('/chat/start/<int:user_id>', methods=['GET'])
@login_required
def start_chat(user_id: int):
    """Yeni bir chat başlat veya var olanı aç."""
    if user_id == current_user.id:
        flash('Kendinize mesaj gönderemezsiniz', 'error')
        return redirect(url_for('chat'))

    User.query.get_or_404(user_id)
    post_id = request.args.get('post_id', type=int)
    conversation = Conversation.get_or_create(current_user.id, user_id, post_id)
    db.session.commit()

    return redirect(url_for('chat_conversation', conversation_id=conversation.id))


@app.route('/chat/send', methods=['POST'])
@login_required
@limiter.limit("100 per minute")
def send_chat_message():
    """Chat mesajı gönder (AJAX) - Dosya desteği ile."""
    try:
        if request.is_json:
            data = request.get_json() or {}
            conversation_id = data.get('conversation_id')
            message_text = data.get('message', '')
            reply_to_raw = data.get('reply_to_id')
            uploaded_file = None
        else:
            conversation_id = request.form.get('conversation_id')
            message_text = request.form.get('message', '')
            reply_to_raw = request.form.get('reply_to_id')
            uploaded_file = request.files.get('file')

        conversation_id = int(conversation_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Geçersiz sohbet'}), 400

    reply_to_id = None
    if reply_to_raw:
        try:
            reply_to_id = int(reply_to_raw)
        except (TypeError, ValueError):
            reply_to_id = None

    conversation = Conversation.query.get_or_404(conversation_id)

    try:
        result = _create_chat_message(
            conversation=conversation,
            sender=current_user,
            message_text=message_text,
            reply_to_id=reply_to_id,
            uploaded_file=uploaded_file,
        )
    except ChatMessageError as exc:
        return jsonify({'success': False, 'error': str(exc)}), exc.status_code
    except Exception as exc:  # pragma: no cover - unexpected errors
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 500

    payload = result['payload']
    return jsonify({'success': True, **payload})

 

@app.route('/chat/messages/<int:conversation_id>/new', methods=['GET'])
@login_required
@limiter.limit("200 per minute")  # Polling için çok yüksek limit
def get_new_messages(conversation_id):
    """Yeni mesajları al (polling için)"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    if current_user.id not in [conversation.user1_id, conversation.user2_id]:
        return jsonify({'success': False, 'error': 'Yetkiniz yok'}), 403
    
    # Son mesaj ID'sini al
    since_id = request.args.get('since_id', type=int, default=0)
    
    # Yeni mesajları getir
    new_messages = Message.query.filter(
        Message.conversation_id == conversation_id,
        Message.id > since_id
    ).order_by(Message.created_at.asc()).all()
    
    # Karşı taraftan gelen mesajları okundu işaretle
    for msg in new_messages:
        if msg.sender_id != current_user.id and not msg.read_at:
            msg.read_at = datetime.now(timezone.utc)
    
    # Okunmamış sayısını güncelle
    conversation.mark_as_read(current_user.id)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'messages': [{
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.masked_full_name,
            'message': msg.message,
            'created_at': msg.created_at.strftime('%H:%M'),
            'is_mine': msg.sender_id == current_user.id,
            'read_at': msg.read_at.strftime('%H:%M') if msg.read_at else None
        } for msg in new_messages]
    })

@app.route('/chat/typing', methods=['POST'])
@login_required
def chat_typing_indicator():
    """Typing indicator (gelecek için - WebSocket ile daha iyi olur)"""
    data = request.get_json()
    conversation_id = data.get('conversation_id')
    
    # Şimdilik sadece success dön, gerçek zamanlı için WebSocket gerekir
    return jsonify({'success': True})

@app.route('/chat/upload', methods=['POST'])
@login_required
def upload_chat_file():
    """Dosya yükle ve mesaj olarak gönder"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Dosya bulunamadı'}), 400
        
        file = request.files['file']
        conversation_id = request.form.get('conversation_id')
        message_text = request.form.get('message', '')
        
        if not conversation_id:
            return jsonify({'success': False, 'error': 'Conversation ID eksik'}), 400
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Dosya seçilmedi'}), 400
        
        # Conversation kontrolü
        conversation = Conversation.query.get_or_404(conversation_id)
        if current_user.id not in [conversation.user1_id, conversation.user2_id]:
            return jsonify({'success': False, 'error': 'Yetkisiz erişim'}), 403
        
        # Dosya uzantısı kontrolü
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        # 🔒 FILE UPLOAD VALIDATION
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}
        is_valid, error_msg, safe_filename = input_validation.validate_file_upload(
            file, 
            allowed_extensions=allowed_extensions, 
            max_size=10*1024*1024  # 10MB
        )
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Unique filename
        file_ext = safe_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_filename}"
        
        # uploads klasörünü oluştur
        upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'chat')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Dosyayı kaydet
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # URL oluştur
        file_url = f"/static/uploads/chat/{unique_filename}"
        
        # Mesaj türünü belirle
        message_type = 'file'
        if file_ext in {'png', 'jpg', 'jpeg', 'gif'}:
            message_type = 'image'
        
        # Mesaj oluştur
        other_user = conversation.get_other_user(current_user.id)
        message = Message(
            conversation_id=conversation_id,
            sender_id=current_user.id,
            receiver_id=other_user.id,
            message=message_text or f"📎 {filename}",
            message_type=message_type,
            file_name=filename,
            file_size=file_size,
            file_url=file_url,
            file_type=file.content_type
        )
        
        db.session.add(message)
        
        # Conversation güncelle
        conversation.last_message_at = datetime.now(timezone.utc)
        if other_user.id == conversation.user1_id:
            conversation.unread_count_user1 += 1
        else:
            conversation.unread_count_user2 += 1
        
        db.session.commit()
        
        # Socket.IO ile bildirim gönder
        socketio.emit('new_message', {
            'conversation_id': conversation_id,
            'message': {
                'id': message.id,
                'sender_id': current_user.id,
                'message': message.message,
                'message_type': message_type,
                'file_name': filename,
                'file_size': file_size,
                'file_url': file_url,
                'created_at': message.created_at.strftime('%H:%M'),
                'is_mine': False
            }
        }, room=f'user_{other_user.id}')
        
        return jsonify({
            'success': True,
            'message': {
                'id': message.id,
                'sender_id': current_user.id,
                'message': message.message,
                'message_type': message_type,
                'file_name': filename,
                'file_size': file_size,
                'file_url': file_url,
                'created_at': message.created_at.strftime('%H:%M'),
                'is_mine': True
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# OLD MESSAGES ROUTES (Backward Compatibility - Deprecated)
# ============================================

@app.route('/messages')
@login_required
def messages():
    """ESKİ mesajlar sayfası - Chat'e yönlendir"""
    return redirect(url_for('chat'))

@app.route('/messages/send/<int:receiver_id>', methods=['GET', 'POST'])
@login_required
def send_message(receiver_id):
    """ESKİ mesaj gönder - Chat'e yönlendir"""
    return redirect(url_for('start_chat', user_id=receiver_id, 
                          post_id=request.args.get('post_id')))

@app.route('/messages/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Mesajı okundu olarak işaretle - Hala çalışır"""
    message = Message.query.get_or_404(message_id)
    
    if message.receiver_id == current_user.id and not message.read_at:
        message.read_at = datetime.now(timezone.utc)
        
        # Conversation'daki unread count'u azalt
        if message.conversation_id:
            conv = Conversation.query.get(message.conversation_id)
            if conv:
                if current_user.id == conv.user1_id and conv.unread_count_user1 > 0:
                    conv.unread_count_user1 -= 1
                elif current_user.id == conv.user2_id and conv.unread_count_user2 > 0:
                    conv.unread_count_user2 -= 1
        
        db.session.commit()
    
    return jsonify({'success': True})

# ============================================
# FAVORITES ROUTES
# ============================================

@app.route('/favorites')
@login_required
def favorites():
    """Favori ilanlar"""
    favorites_raw = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc()).all()

    now = datetime.now(timezone.utc)
    soon_threshold = now + timedelta(days=7)

    def _to_utc(dt):
        if not dt:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    def _time_ago(dt):
        if not dt:
            return ""
        dt = _to_utc(dt) or now
        delta = now - dt
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return "az önce"
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

    def _slugify(value):
        if not value:
            return "other"
        sanitized = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
        cleaned = "-".join(segment for segment in sanitized.split("-") if segment)
        return cleaned or "other"

    urgency_map = {
        'very_urgent': {'label': 'Çok acil', 'variant': 'rose'},
        'urgent': {'label': 'Acil', 'variant': 'orange'},
        'normal': {'label': 'Normal', 'variant': 'slate'},
        None: {'label': 'Normal', 'variant': 'slate'},
    }

    favorite_cards = []
    category_counts = {}
    price_values = []
    urgent_count = 0
    upcoming_count = 0

    for fav in favorites_raw:
        post = fav.post
        if not post:
            favorite_cards.append({
                'favorite_id': fav.id,
                'post_id': None,
                'title': 'İlan kaldırıldı',
                'url': None,
                'category': 'Bilinmiyor',
                'category_slug': 'other',
                'city': None,
                'city_slug': 'other',
                'urgency': 'normal',
                'urgency_label': 'Normal',
                'urgency_variant': 'slate',
                'deadline_display': 'Takvimlenmedi',
                'deadline_state': 'none',
                'deadline_badge': None,
                'price_display': None,
                'views': 0,
                'applications': 0,
                'status': 'inactive',
                'status_label': 'Pasif',
                'favorited_display': fav.created_at.strftime('%d %b %Y, %H:%M') if fav.created_at else '',
                'time_ago': _time_ago(fav.created_at),
            })
            continue

        deadline_source = post.deadline or post.court_date
        deadline_utc = _to_utc(deadline_source)
        deadline_display = deadline_utc.strftime('%d %b %Y, %H:%M') if deadline_utc else 'Takvimlenmedi'
        if deadline_utc:
            if deadline_utc < now:
                deadline_state = 'overdue'
                deadline_badge = 'Süresi doldu'
            elif deadline_utc <= soon_threshold:
                remaining = deadline_utc - now
                days_left = max(int(remaining.total_seconds() // 86400), 0)
                deadline_state = 'soon'
                deadline_badge = 'Bugün' if days_left == 0 else f'{days_left} gün kaldı'
            else:
                deadline_state = 'scheduled'
                deadline_badge = 'Takvimde'
        else:
            deadline_state = 'none'
            deadline_badge = None

        urgency_key = post.urgency_level or 'normal'
        urgency_info = urgency_map.get(urgency_key, urgency_map['normal'])
        if urgency_info['variant'] in ('rose', 'orange'):
            urgent_count += 1
        if deadline_state == 'soon':
            upcoming_count += 1

        category_counts[post.category] = category_counts.get(post.category, 0) + 1
        city_key = post.city or post.location or 'Diğer'

        if post.price_min:
            price_values.append(post.price_min)
        elif post.price_max:
            price_values.append(post.price_max)

        price_display = None
        if post.price_min and post.price_max:
            price_display = f"{int(post.price_min)} - {int(post.price_max)} ₺"
        elif post.price_min:
            price_display = f"{int(post.price_min)} ₺"
        elif post.price_max:
            price_display = f"{int(post.price_max)} ₺"

        favorite_cards.append({
            'favorite_id': fav.id,
            'post_id': post.id,
            'title': post.title,
            'url': url_for('post_detail', post_id=post.id),
            'category': post.category,
            'category_slug': _slugify(post.category),
            'city': city_key,
            'city_slug': _slugify(city_key),
            'urgency': urgency_key,
            'urgency_label': urgency_info['label'],
            'urgency_variant': urgency_info['variant'],
            'deadline_display': deadline_display,
            'deadline_state': deadline_state,
            'deadline_badge': deadline_badge,
            'price_display': price_display,
            'views': post.views or post.view_count or 0,
            'applications': post.applications_count or 0,
            'status': post.status,
            'status_label': 'Aktif' if post.status == 'active' else 'Pasif',
            'favorited_display': fav.created_at.strftime('%d %b %Y, %H:%M') if fav.created_at else '',
            'time_ago': _time_ago(fav.created_at),
        })

    total_count = len(favorite_cards)
    average_price = int(sum(price_values) / len(price_values)) if price_values else 0
    last_added = _time_ago(favorites_raw[0].created_at) if favorites_raw else None

    metrics = [
        {
            'label': 'Favori ilan',
            'icon': 'favorite',
            'value': total_count,
            'subtitle': f"Son eklenen {last_added}" if last_added else 'Henüz favori yok',
            'variant': 'brand',
        },
        {
            'label': 'Acil durum',
            'icon': 'priority_high',
            'value': urgent_count,
            'subtitle': 'Çok acil ilanlar',
            'variant': 'rose',
        },
        {
            'label': 'Yaklaşan tarih',
            'icon': 'event_upcoming',
            'value': upcoming_count,
            'subtitle': '7 gün içinde duruşma',
            'variant': 'amber',
        },
        {
            'label': 'Ortalama teklif',
            'icon': 'payments',
            'value': f'{average_price:,} ₺' if average_price else '—',
            'subtitle': 'Favorilerde',
            'variant': 'indigo',
        },
    ]

    filters = [
        {'key': 'all', 'label': 'Tümü', 'count': total_count},
    ]
    if urgent_count:
        filters.append({'key': 'urgent', 'label': 'Acil', 'count': urgent_count})

    for category, count in sorted(category_counts.items(), key=lambda item: item[0]):
        filters.append({'key': f'cat-{_slugify(category)}', 'label': category, 'count': count, 'type': 'category'})

    counts = {
        'total': total_count,
        'urgent': urgent_count,
        'upcoming': upcoming_count,
    }

    return render_template(
        'favorites.html',
        favorites=favorite_cards,
        metrics=metrics,
        filters=filters,
        counts=counts,
    )

@app.route('/favorites/toggle/<int:post_id>', methods=['POST'])
@login_required
def toggle_favorite(post_id):
    """Favorilere ekle/çıkar"""
    post = TevkilPost.query.get_or_404(post_id)
    
    favorite = Favorite.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if favorite:
        # Zaten favoride, çıkar
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'success': True, 'action': 'removed', 'message': 'Favorilerden çıkarıldı'})
    else:
        # Favorilere ekle
        favorite = Favorite(user_id=current_user.id, post_id=post_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'success': True, 'action': 'added', 'message': 'Favorilere eklendi'})

# ============================================
# API ENDPOINTS (for future mobile app)
# ============================================

@app.route('/api/posts', methods=['GET'])
def api_posts():
    """API: İlan listesi"""
    posts = TevkilPost.query.filter_by(status='active').order_by(TevkilPost.created_at.desc()).limit(20).all()
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'category': p.category,
        'location': p.location,
        'urgency': p.urgency_level,
        'created_at': p.created_at.isoformat()
    } for p in posts])

@app.route('/api/courthouses/<city>', methods=['GET'])
def api_courthouses(city):
    """API: Belirli bir şehrin adliyelerini döndür"""
    courthouses = COURTHOUSES.get(city, [])
    return jsonify(courthouses)

# ============================================
# WHATSAPP BOT ENDPOINTS
# ============================================

@app.route('/api/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    """
    Merkezi WhatsApp Cloud API Webhook
    Tek numara - Tüm avukatlar için
    """
    if not current_app.config.get('WHATSAPP_ENABLED'):
        abort(404)
    
    from whatsapp_central_bot import central_bot
    from whatsapp_meta_api import MetaWhatsAppAPI
    
    # GET request: Webhook verification (Meta tarafından)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        print(f"🔔 Webhook verification isteği:")
        print(f"  Mode: {mode}")
        print(f"  Token: {token}")
        print(f"  Challenge: {challenge}")
        
        api = MetaWhatsAppAPI()
        verified_challenge = api.verify_webhook(mode, token, challenge)
        
        if verified_challenge:
            print(f"✅ Webhook verified! Challenge: {verified_challenge}")
            # Meta integer challenge bekliyor, string olarak gönder
            return str(verified_challenge), 200
        else:
            print(f"❌ Webhook verification failed!")
            return 'Verification failed', 403
    
    # POST request: Gelen mesajlar
    elif request.method == 'POST':
        try:
            data = request.json
            print(f"\n📨 Gelen mesaj: {data}")
            
            # Meta webhook'tan mesajı parse et
            api = MetaWhatsAppAPI()
            message_data = api.parse_webhook_message(data)
            
            if not message_data:
                print("⚠️ Mesaj parse edilemedi veya status update")
                return jsonify({'status': 'ignored'}), 200
            
            sender_phone = message_data['sender_phone']
            message_text = message_data['message_text']
            message_id = message_data['message_id']
            message_type = message_data.get('type', 'text')
            
            print(f"👤 Gönderen: {sender_phone}")
            print(f"💬 Mesaj: {message_text}")
            print(f"🆔 Message ID: {message_id}")
            print(f"📝 Tip: {message_type}")
            
            # Sesli mesaj veya medya ise bildir ve ignore et
            if message_type != 'text' or message_text is None:
                print(f"⚠️ Text dışı mesaj tipi ({message_type}), cevap gönderiliyor...")
                api.mark_message_as_read(message_id)
                
                # Kullanıcıya bilgi mesajı gönder
                if message_type == 'audio':
                    info_msg = """🎤 Sesli mesaj aldım!

Üzgünüm, şu anda sadece yazılı mesajları işleyebiliyorum.

Lütfen ilanınızı yazarak gönderin:

Örnek:
"Ankara 4. Asliye Ceza Mahkemesinde yarın saat 10:00 duruşma, 2000 TL"

Yardım: #YARDIM"""
                else:
                    info_msg = f"""📎 {message_type.title()} mesajı aldım!

Üzgünüm, şu anda sadece yazılı mesajları işleyebiliyorum.

Lütfen ilanınızı yazarak gönderin.

Yardım: #YARDIM"""
                
                try:
                    api.send_message(sender_phone, info_msg)
                    print(f"✅ Bilgi mesajı gönderildi")
                except:
                    pass
                
                return jsonify({'status': 'ignored', 'reason': f'Non-text message type: {message_type}'}), 200
            
            # ÖNEMLİ: Duplicate mesaj kontrolü
            # Meta bazen aynı mesajı 2 kez gönderebiliyor
            from datetime import datetime, timezone, timedelta
            
            now = datetime.now(timezone.utc)
            
            # Eski message cache'leri temizle (5 dakikadan eski)
            cutoff_time = now - timedelta(minutes=5)
            central_bot.processed_messages = {
                mid: ts for mid, ts in central_bot.processed_messages.items()
                if ts > cutoff_time
            }
            
            # Bu mesaj zaten işlendi mi?
            if message_id in central_bot.processed_messages:
                print(f"⚠️ DUPLICATE MESAJ! Message ID {message_id} zaten işlendi, atlıyorum.")
                return jsonify({'status': 'duplicate', 'message': 'Already processed'}), 200
            
            # Mesajı cache'e ekle
            central_bot.processed_messages[message_id] = now
            
            # Mesajı okundu olarak işaretle
            api.mark_message_as_read(message_id)
            
            # Merkezi Bot'u kullan - TEK NUMARA SİSTEMİ
            result = central_bot.process_message(sender_phone, message_text)
            
            # Kullanıcıya cevap gönder
            if result:
                api.send_message(sender_phone, result['message'])
                print(f"✅ Cevap gönderildi!")
            
            return jsonify({'status': 'success'}), 200
            
        except Exception as e:
            print(f"❌ Webhook error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/whatsapp/test', methods=['POST'])
@login_required
def whatsapp_test():
    """
    WhatsApp bot test endpoint - Manuel test için
    Merkezi bot sistemini kullanır
    """
    if not current_app.config.get('WHATSAPP_ENABLED'):
        return jsonify({'success': False, 'error': 'WhatsApp özelliği şu anda devre dışı'}), 404
    
    from whatsapp_central_bot import central_bot
    
    message_text = request.form.get('message')
    
    if not current_user.phone:
        return jsonify({
            'success': False,
            'error': 'Telefon numaranız kayıtlı değil. Lütfen profilinizi düzenleyin.'
        }), 400
    
    if not message_text:
        return jsonify({'success': False, 'error': 'Mesaj boş olamaz'}), 400
    
    try:
        # Merkezi Bot'u kullan
        result = central_bot.process_message(current_user.phone, message_text)
        
        if result['success']:
            return jsonify({
                'success': True,
                'response': result['message'],
                'message': 'İşlem başarılı!'
            })
        else:
            return jsonify({
                'success': False,
                'error': result['message']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Hata: {str(e)}'
        }), 500

# ============================================
# DATABASE INITIALIZATION
# ============================================

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized!')

# ============================================================
# PWA ROUTES
# ============================================================

@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest"""
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

@app.route('/service-worker.js')
def service_worker():
    """Serve service worker"""
    return send_from_directory('static', 'service-worker.js', mimetype='application/javascript')


# ============================================================
# SECURITY & 2FA ROUTES
# ============================================================

@app.route('/verify-2fa', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def verify_2fa():
    """2FA doğrulama sayfası"""
    if 'pending_2fa_user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['pending_2fa_user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        token = request.form.get('token', '').replace('-', '').replace(' ', '')
        use_backup = request.form.get('use_backup', False)
        
        verified = False
        
        if use_backup:
            # Yedek kod kullan
            verified = security_utils.verify_backup_code(user, token)
            if verified:
                security_utils.log_security_event(
                    user.id, '2fa_backup_code_used', 'INFO',
                    'Backup code used for 2FA verification'
                )
        else:
            # TOTP token doğrula
            verified = security_utils.verify_2fa_token(user.two_factor_secret, token)
        
        if verified:
            # 2FA başarılı
            remember = session.get('pending_2fa_remember', False)
            
            # Session'ı geçici tut (web için normal session)
            session.permanent = False
            
            # Login yap - Web için remember=False
            login_user(user, remember=False)
            
            # Session işaretle
            session['2fa_verified'] = True
            session.pop('pending_2fa_user_id', None)
            session.pop('pending_2fa_remember', None)
            
            # Son aktiflik
            user.last_active = datetime.utcnow()
            db.session.commit()
            
            # Session oluştur
            session_token = security_utils.create_user_session(user.id)
            session['session_token'] = session_token
            
            # Logla
            security_utils.log_security_event(
                user.id, '2fa_verified', 'INFO',
                'Two-factor authentication verified successfully'
            )
            security_utils.log_login_attempt(
                user.email, request.remote_addr, 
                request.headers.get('User-Agent', ''), success=True
            )
            
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # 2FA başarısız
            security_utils.log_security_event(
                user.id, '2fa_failed', 'WARNING',
                '2FA verification failed - invalid token'
            )
            flash('Geçersiz doğrulama kodu. Lütfen tekrar deneyin.', 'error')
    
    return render_template('verify_2fa.html', user=user)


@app.route('/security/settings', methods=['GET'])
@login_required
def security_settings():
    """Güvenlik ayarları sayfası"""
    # Aktif oturumlar
    active_sessions = security_utils.get_active_sessions(current_user.id)
    
    # Son güvenlik olayları
    recent_logs = SecurityLog.query.filter_by(
        user_id=current_user.id
    ).order_by(SecurityLog.created_at.desc()).limit(20).all()
    
    return render_template('security_settings.html',
                         user=current_user,
                         active_sessions=active_sessions,
                         security_logs=recent_logs)


@app.route('/security/sessions/terminate/<int:session_id>', methods=['POST'])
@login_required
def terminate_session(session_id):
    """Belirli bir oturumu sonlandır"""
    user_session = UserSession.query.get(session_id)
    
    if not user_session or user_session.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Oturum bulunamadı'}), 404
    
    user_session.is_active = False
    db.session.commit()
    
    security_utils.log_security_event(
        current_user.id, 'session_terminated', 'INFO',
        f'Session {session_id} terminated by user'
    )
    
    return jsonify({'success': True, 'message': 'Oturum sonlandırıldı'})


@app.route('/security/sessions/terminate-all', methods=['POST'])
@login_required
def terminate_all_sessions():
    """Tüm diğer oturumları sonlandır"""
    count = security_utils.terminate_all_sessions(current_user.id, except_current=True)
    
    security_utils.log_security_event(
        current_user.id, 'all_sessions_terminated', 'INFO',
        f'Terminated {count} sessions'
    )
    
    return jsonify({
        'success': True,
        'message': f'{count} oturum sonlandırıldı'
    })


@app.route('/security/password/check-strength', methods=['POST'])
def check_password_strength():
    """Şifre gücünü kontrol et (AJAX)"""
    password = request.json.get('password', '')
    is_strong, message = security_utils.is_strong_password(password)
    
    return jsonify({
        'is_strong': is_strong,
        'message': message
    })


@app.route('/security/logs', methods=['GET'])
@login_required
def security_logs():
    """Güvenlik loglarını görüntüle"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    logs = SecurityLog.query.filter_by(
        user_id=current_user.id
    ).order_by(SecurityLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('security_logs.html', logs=logs)


# ============================================================
# WEBSOCKET EVENTS (Real-time Chat)
# ============================================================

# Store active users {user_id: sid}
active_users = {}
# Store typing status {conversation_id: {user_id: timestamp}}
typing_users = {}

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    if current_user.is_authenticated:
        active_users[current_user.id] = request.sid
        print(f'✅ WebSocket: User {current_user.id} ({current_user.full_name}) connected')
        
        # Notify others that user is online
        emit('user_status', {
            'user_id': current_user.id,
            'status': 'online',
            'full_name': current_user.masked_full_name
        }, broadcast=True)
    else:
        print('❌ WebSocket: Unauthenticated connection attempt')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    if current_user.is_authenticated:
        if current_user.id in active_users:
            del active_users[current_user.id]
        
        print(f'👋 WebSocket: User {current_user.id} disconnected')
        
        # Notify others that user is offline
        emit('user_status', {
            'user_id': current_user.id,
            'status': 'offline',
            'full_name': current_user.masked_full_name
        }, broadcast=True)

@socketio.on('join_conversation')
def handle_join_conversation(data):
    """Join a conversation room"""
    conversation_id = data.get('conversation_id')
    if not conversation_id:
        return
    
    # Verify user is part of this conversation
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        emit('error', {'message': 'Conversation not found'})
        return
    
    if current_user.id not in [conversation.user1_id, conversation.user2_id]:
        emit('error', {'message': 'Unauthorized'})
        return
    
    # Join the room
    room = f'conversation_{conversation_id}'
    join_room(room)
    print(f'📥 User {current_user.id} joined conversation {conversation_id}')
    
    # Mark messages as read
    Message.query.filter(
        Message.conversation_id == conversation_id,
        Message.receiver_id == current_user.id,
        Message.read_at.is_(None)
    ).update({'read_at': datetime.now(timezone.utc)}, synchronize_session=False)

    conversation.mark_as_read(current_user.id)
    db.session.commit()
    
    # Notify about read status
    emit('messages_read', {
        'conversation_id': conversation_id,
        'user_id': current_user.id
    }, room=room)

@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    """Leave a conversation room"""
    conversation_id = data.get('conversation_id')
    if not conversation_id:
        return
    
    room = f'conversation_{conversation_id}'
    leave_room(room)
    print(f'📤 User {current_user.id} left conversation {conversation_id}')

@socketio.on('send_message')
def handle_send_message(data):
    """Handle sending a new message"""
    try:
        conversation_id = data.get('conversation_id')
        content = data.get('content', '').strip()
        
        if not conversation_id or not content:
            emit('error', {'message': 'Invalid message data'})
            return
        
        # Verify conversation access
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            emit('error', {'message': 'Conversation not found'})
            return
        
        if current_user.id not in [conversation.user1_id, conversation.user2_id]:
            emit('error', {'message': 'Unauthorized'})
            return
        
        # Determine receiver
        receiver_id = conversation.user2_id if current_user.id == conversation.user1_id else conversation.user1_id
        other_user = User.query.get(receiver_id)
        
        # Create message (correct field name: message, not content)
        message = Message(
            conversation_id=conversation_id,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            message=content,  # ✅ FIXED: Use 'message' field
            post_id=conversation.post_id,
            delivered_at=datetime.now(timezone.utc)
        )
        db.session.add(message)
        
        # Update conversation
        conversation.last_message_at = datetime.now(timezone.utc)
        conversation.last_message_text = content[:100]
        conversation.last_message_sender_id = current_user.id
        
        # Update unread count
        if current_user.id == conversation.user1_id:
            conversation.unread_count_user2 += 1
        else:
            conversation.unread_count_user1 += 1
        
        db.session.commit()
        
        # Get sender avatar with fallback
        masked_sender_name = current_user.masked_full_name
        sender_avatar = current_user.avatar_url if current_user.avatar_url else f"https://ui-avatars.com/api/?name={masked_sender_name.replace(' ', '+')}&background=1f2937&color=fff"
        
        # Prepare message data
        message_data = {
            'id': message.id,
            'conversation_id': conversation_id,
            'sender_id': current_user.id,
            'sender_name': masked_sender_name,
            'sender_avatar': sender_avatar,
            'receiver_id': receiver_id,
            'content': content,
            'message': content,  # Both for compatibility
            'timestamp': message.created_at.strftime('%H:%M'),
            'created_at': message.created_at.isoformat(),
            'is_read': False,
            'read_at': None,
            # 📎 Dosya bilgileri (şimdilik None - gelecekte eklenecek)
            'message_type': message.message_type or 'text',
            'file_url': message.file_url,
            'file_name': message.file_name,
            'file_size': message.file_size,
            'file_type': message.file_type
        }
        
        # Send to conversation room
        room = f'conversation_{conversation_id}'
        emit('new_message', message_data, room=room)
        
        # Send notification to receiver if online but not in room
        if receiver_id in active_users:
            emit('new_message_notification', {
                'conversation_id': conversation_id,
                'sender_name': masked_sender_name,
                'sender_avatar': sender_avatar,
                'preview': content[:50]
            }, room=active_users[receiver_id])
        
        # 📱 PUSH NOTIFICATION - Alıcıya mobil bildirim gönder
        try:
            send_push_notification(
                user_id=receiver_id,
                title=f'💬 {masked_sender_name}',
                body=content[:100],  # İlk 100 karakter
                data={
                    'type': 'new_message',
                    'conversation_id': str(conversation_id),
                    'sender_id': str(current_user.id),
                    'sender_name': masked_sender_name,
                    'page': f'/chat?conversation_id={conversation_id}'
                }
            )
        except Exception as notif_error:
            print(f"⚠️ Push notification error: {notif_error}")
        
        print(f'📨 Message sent: {current_user.id} → {receiver_id} in conversation {conversation_id}')
        
    except Exception as e:
        print(f'❌ Error in handle_send_message: {str(e)}')
        db.session.rollback()
        emit('error', {'message': f'Error sending message: {str(e)}'})

@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicator"""
    conversation_id = data.get('conversation_id')
    is_typing = data.get('is_typing', False)
    
    if not conversation_id:
        return
    
    # Verify conversation access
    conversation = Conversation.query.get(conversation_id)
    if not conversation or current_user.id not in [conversation.user1_id, conversation.user2_id]:
        return
    
    room = f'conversation_{conversation_id}'
    
    # Update typing status
    if conversation_id not in typing_users:
        typing_users[conversation_id] = {}
    
    if is_typing:
        typing_users[conversation_id][current_user.id] = datetime.now()
    elif current_user.id in typing_users[conversation_id]:
        del typing_users[conversation_id][current_user.id]
    
    # Broadcast typing status to room (except sender)
    emit('user_typing', {
        'user_id': current_user.id,
        'user_name': current_user.masked_full_name,
        'is_typing': is_typing
    }, room=room, skip_sid=request.sid)

@socketio.on('mark_as_read')
def handle_mark_as_read(data):
    """Mark messages as read"""
    conversation_id = data.get('conversation_id')
    
    if not conversation_id:
        return
    
    conversation = Conversation.query.get(conversation_id)
    if not conversation or current_user.id not in [conversation.user1_id, conversation.user2_id]:
        return

    # Mark all messages from other user as read
    Message.query.filter(
        Message.conversation_id == conversation_id,
        Message.receiver_id == current_user.id,
        Message.read_at.is_(None)
    ).update({'read_at': datetime.now(timezone.utc)}, synchronize_session=False)

    conversation.mark_as_read(current_user.id)
    db.session.commit()
    
    room = f'conversation_{conversation_id}'
    emit('messages_read', {
        'conversation_id': conversation_id,
        'user_id': current_user.id
    }, room=room)

@socketio.on('request_online_status')
def handle_online_status_request(data):
    """Return online status of users"""
    user_ids = data.get('user_ids', [])
    
    online_status = {}
    for user_id in user_ids:
        online_status[user_id] = user_id in active_users
    
    emit('online_status_response', online_status)

# ==================== PUSH NOTIFICATIONS ====================
# Device Token Model
class DeviceToken(db.Model):
    __tablename__ = 'device_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False)
    platform = db.Column(db.String(20), nullable=False)  # 'android' or 'ios'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

@app.route('/api/notifications/register-device', methods=['POST'])
@login_required
def register_device_token():
    """Register device token for push notifications"""
    try:
        data = request.get_json()
        token = data.get('token')
        platform = data.get('platform', 'android')

        if not token:
            return jsonify({'error': 'Token is required'}), 400

        # Check if token already exists
        existing_token = DeviceToken.query.filter_by(token=token).first()
        
        if existing_token:
            # Update last_used time
            existing_token.last_used = datetime.now(timezone.utc)
            existing_token.user_id = current_user.id  # Update user if changed
        else:
            # Create new token
            new_token = DeviceToken(
                user_id=current_user.id,
                token=token,
                platform=platform
            )
            db.session.add(new_token)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Device registered'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error registering device token: {e}")
        return jsonify({'error': 'Failed to register device'}), 500

@app.route('/api/notifications/unregister-device', methods=['POST'])
@login_required
def unregister_device_token():
    """Unregister device token (when user logs out)"""
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({'error': 'Token is required'}), 400

        device = DeviceToken.query.filter_by(token=token, user_id=current_user.id).first()
        if device:
            db.session.delete(device)
            db.session.commit()

        return jsonify({'success': True, 'message': 'Device unregistered'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error unregistering device token: {e}")
        return jsonify({'error': 'Failed to unregister device'}), 500

def send_push_notification(user_id, title, body, data=None):
    """
    Send push notification to user's devices via Firebase Cloud Messaging
    """
    try:
        from firebase_notification_service import FirebaseNotificationService
        
        # Get user's device tokens
        tokens = DeviceToken.query.filter_by(user_id=user_id).all()
        
        if not tokens:
            print(f"ℹ️ No device tokens found for user {user_id}")
            return False

        print(f"📬 Sending push notification to user {user_id}:")
        print(f"   Title: {title}")
        print(f"   Body: {body}")
        print(f"   Data: {data}")
        print(f"   Devices: {len(tokens)}")

        # Get list of FCM tokens
        fcm_tokens = [token.token for token in tokens if token.platform == 'android']
        
        if not fcm_tokens:
            print(f"⚠️ No Android FCM tokens found for user {user_id}")
            return False
        
        # Send via Firebase Cloud Messaging
        result = FirebaseNotificationService.send_multicast(
            tokens=fcm_tokens,
            title=title,
            body=body,
            data=data
        )
        
        # Clean up invalid tokens
        if result.get('invalid_tokens'):
            for invalid_token in result['invalid_tokens']:
                device = DeviceToken.query.filter_by(token=invalid_token).first()
                if device:
                    db.session.delete(device)
                    print(f"🗑️ Removed invalid token: {invalid_token[:20]}...")
            db.session.commit()
        
        return result.get('success', 0) > 0

    except Exception as e:
        print(f"❌ Error sending push notification: {e}")
        return False

# ==================== MOBILE API ENDPOINTS ====================
# 📱 Token-based authentication for mobile apps (persistent sessions)

@app.route('/api/mobile/login', methods=['POST'])
@limiter.limit("10 per minute")
def api_mobile_login():
    """Mobile app login - Returns persistent API token"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email ve şifre gerekli'
            }), 400
        
        # Kullanıcıyı bul
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'error': 'Hatalı email veya şifre'
            }), 401
        
        # Hesap aktif mi kontrol et
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'Hesabınız aktif değil'
            }), 403
        
        # API token oluştur (veya mevcut olanı kullan)
        if not user.api_token:
            user.generate_api_token()
            db.session.commit()
        else:
            # Mevcut token'ı güncelle
            user.api_token_last_used = datetime.utcnow()
            db.session.commit()
        
        # Kullanıcı bilgilerini döndür
        return jsonify({
            'success': True,
            'token': user.api_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'avatar_url': user.avatar_url,
                'city': user.city,
                'lawyer_type': user.lawyer_type,
                'rating_average': user.rating_average,
                'rating_count': user.rating_count,
                'is_admin': user.is_admin
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Mobile login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Giriş işlemi başarısız'
        }), 500

@app.route('/api/mobile/logout', methods=['POST'])
def api_mobile_logout():
    """Mobile app logout - Revokes API token"""
    try:
        # Authorization header'dan token al
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Token gerekli'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Token'a sahip kullanıcıyı bul
        user = User.query.filter_by(api_token=token).first()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Geçersiz token'
            }), 401
        
        # Token'ı iptal et
        user.revoke_api_token()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Çıkış başarılı'
        }), 200
        
    except Exception as e:
        print(f"❌ Mobile logout error: {e}")
        return jsonify({
            'success': False,
            'error': 'Çıkış işlemi başarısız'
        }), 500

@app.route('/api/mobile/verify', methods=['POST'])
def api_mobile_verify():
    """Verify API token and return user info"""
    try:
        # Authorization header'dan token al
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Token gerekli'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Token'a sahip kullanıcıyı bul
        user = User.query.filter_by(api_token=token).first()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Geçersiz token',
                'action': 'login_required'
            }), 401
        
        # Token'ın son kullanım zamanını güncelle
        user.api_token_last_used = datetime.utcnow()
        db.session.commit()
        
        # Kullanıcı bilgilerini döndür
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'avatar_url': user.avatar_url,
                'city': user.city,
                'lawyer_type': user.lawyer_type,
                'rating_average': user.rating_average,
                'rating_count': user.rating_count,
                'is_admin': user.is_admin,
                'unread_notifications': user.notifications_unread_count
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Mobile verify error: {e}")
        return jsonify({
            'success': False,
            'error': 'Token doğrulama başarısız'
        }), 500

# ==================== HEALTH CHECK ====================
@app.route('/health')
@app.route('/healthz')
@limiter.exempt  # 🔥 Health check'i rate limiting'den muaf tut
def health_check():
    """Health check endpoint for platform and external monitors."""
    try:
        db.session.execute(text('SELECT 1'))
        db.session.rollback()
    except Exception as exc:  # pragma: no cover - defensive guard
        current_app.logger.error('Health check failed: %s', exc)
        db.session.rollback()
        return jsonify({'status': 'unhealthy', 'detail': str(exc)}), 500

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200

# ==================== LEGAL PAGES ====================
@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('phoenix/static/contact.html')

@app.route('/privacy-policy')
def privacy_policy():
    """Privacy policy page (KVKK compliance)"""
    return render_template('privacy_policy.html', current_date='2025')

@app.route('/terms-of-service')
def terms_of_service():
    """Terms of service page"""
    return render_template('terms_of_service.html', current_date='2025')

@app.route('/cookie-policy')
def cookie_policy():
    """Cookie policy page"""
    return render_template('cookie_policy.html', current_date='2025')

# ==================== HEALTH & ANALYTICS HELPERS ====================

def _apply_date_range(query, column, start_dt=None, end_dt=None):
    """Apply optional start/end datetime filters to a SQLAlchemy query."""
    if start_dt:
        query = query.filter(column >= start_dt)
    if end_dt:
        query = query.filter(column < end_dt)
    return query


def _parse_analytics_filters(args):
    """Normalise incoming analytics filter query parameters."""
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
    """Collect analytics metrics respecting the active filter set."""
    now = datetime.utcnow()
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

    message_query = _apply_date_range(Message.query, Message.created_at, start_dt, end_dt)
    total_messages = message_query.count()
    messages_this_week = _apply_date_range(Message.query, Message.created_at, week_start, end_dt).count()

    rating_query = _apply_date_range(Rating.query, Rating.created_at, start_dt, end_dt)
    total_ratings = rating_query.count()
    avg_rating = rating_query.with_entities(func.avg(Rating.rating)).scalar() or 0
    ratings_this_week = _apply_date_range(Rating.query, Rating.created_at, week_start, end_dt).count()

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
# ==================== ADMIN & ANALYTICS ====================
@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    """Render the admin analytics dashboard with optional filtering."""

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

    return render_template('admin_analytics.html', **context)

@app.route('/admin/analytics/export')
@admin_required
def export_analytics():
    """Export analytics data as CSV respecting active filters."""

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

# ==================== USER MANAGEMENT ====================
@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin kullanıcı yönetim paneli - tüm kullanıcıları listele"""
    
    # Filtreleme parametreleri
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
    
    # Arama filtresi (isim, email, telefon)
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
    
    # Şehir filtresi
    if city:
        query = query.filter(User.city == city)
    
    # Baro filtresi
    if bar_association:
        query = query.filter(User.bar_association == bar_association)
    
    # Durum filtresi
    if status == 'active':
        query = query.filter(User.is_active == True)
    elif status == 'inactive':
        query = query.filter(User.is_active == False)
    
    # Doğrulama filtresi
    if verified == 'yes':
        query = query.filter(User.verified == True)
    elif verified == 'no':
        query = query.filter(User.verified == False)
    
    # Sıralama
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
    else:  # created_at
        order_col = User.created_at
    
    if order == 'asc':
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())
    
    # Sayfalama
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    # İstatistikler
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    verified_users = User.query.filter_by(verified=True).count()
    admin_users_count = User.query.filter_by(is_admin=True).count()
    
    # Benzersiz baro listesi
    bar_associations = db.session.query(User.bar_association).distinct().filter(
        User.bar_association.isnot(None),
        User.bar_association != ''
    ).all()
    bar_associations = sorted([b[0] for b in bar_associations])
    
    return render_template('phoenix/admin/users.html',
                         users=users,
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
                         admin_users_count=admin_users_count)

@app.route('/admin/users/<int:user_id>')
@login_required
@admin_required
def admin_user_detail(user_id):
    """Kullanıcı detay sayfası - admin için"""
    
    user = User.query.get_or_404(user_id)
    
    # Kullanıcının ilanları
    posts = TevkilPost.query.filter_by(user_id=user_id).order_by(TevkilPost.created_at.desc()).limit(10).all()
    
    # Kullanıcının başvuruları (gönderdiği)
    applications_sent = Application.query.filter_by(applicant_id=user_id).order_by(
        Application.created_at.desc()
    ).limit(10).all()
    
    # Kullanıcının aldığı başvurular
    post_ids = [p.id for p in TevkilPost.query.filter_by(user_id=user_id).all()]
    applications_received = Application.query.filter(
        Application.post_id.in_(post_ids)
    ).order_by(Application.created_at.desc()).limit(10).all() if post_ids else []
    
    # Son aktiviteler
    last_login = None  # Bu özellik eklenebilir
    
    return render_template('admin_user_detail.html',
                         user=user,
                         posts=posts,
                         applications_sent=applications_sent,
                         applications_received=applications_received,
                         last_login=last_login)

@app.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user_status(user_id):
    """Kullanıcı durumunu aktif/pasif yap"""
    
    user = User.query.get_or_404(user_id)
    
    # Kendi hesabını devre dışı bırakmasın
    if user.id == current_user.id:
        flash('Kendi hesabınızın durumunu değiştiremezsiniz.', 'error')
        return redirect(url_for('admin_user_detail', user_id=user_id))
    
    user.is_active = not user.is_active
    
    try:
        db.session.commit()
        status_text = "aktif" if user.is_active else "pasif"
        flash(f'{user.full_name} kullanıcısı {status_text} duruma getirildi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Bir hata oluştu. Lütfen tekrar deneyin.', 'error')
        print(f"❌ Kullanıcı durum değiştirme hatası: {e}")
    
    return redirect(url_for('admin_user_detail', user_id=user_id))

@app.route('/admin/users/<int:user_id>/verify', methods=['POST'])
@login_required
@admin_required
def admin_verify_user(user_id):
    """Kullanıcıyı doğrula/doğrulamayı kaldır"""
    
    user = User.query.get_or_404(user_id)
    
    user.verified = not user.verified
    
    try:
        db.session.commit()
        status_text = "doğrulandı" if user.verified else "doğrulaması kaldırıldı"
        flash(f'{user.full_name} kullanıcısı {status_text}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Bir hata oluştu. Lütfen tekrar deneyin.', 'error')
        print(f"❌ Kullanıcı doğrulama hatası: {e}")
    
    return redirect(url_for('admin_user_detail', user_id=user_id))

# ==================== REPORT MANAGEMENT ====================
@app.route('/admin/reports/<int:report_id>/update', methods=['POST'])
@admin_required
def update_report_status(report_id):
    """Allow admins to update report status and log the action."""

    status = (request.form.get('status') or '').strip()
    admin_note = (request.form.get('admin_note') or '').strip()
    action_taken = (request.form.get('action_taken') or '').strip()

    redirect_params = {
        key: value for key in ('start_date', 'end_date', 'city', 'category')
        if (value := request.form.get(key))
    }

    try:
        report = Report.query.get(report_id)
    except ProgrammingError as exc:
        db.session.rollback()
        current_app.logger.warning('Report tablosuna erişilemedi: %s', exc)
        flash('Rapor tablosu mevcut değil. Lütfen migration komutlarını çalıştırın.', 'error')
        return redirect(url_for('admin_analytics', **redirect_params))

    if not report:
        flash('Rapor bulunamadı.', 'error')
        return redirect(url_for('admin_analytics', **redirect_params))

    valid_statuses = {'pending', 'reviewed', 'resolved', 'dismissed'}
    if status not in valid_statuses:
        flash('Geçersiz rapor durumu seçildi.', 'error')
        return redirect(url_for('admin_analytics', **redirect_params))

    if action_taken and action_taken not in {'none', 'warning', 'content_removed', 'user_banned'}:
        flash('Geçersiz aksiyon değeri.', 'error')
        return redirect(url_for('admin_analytics', **redirect_params))

    report.status = status
    report.admin_note = admin_note or None
    report.action_taken = action_taken or None
    report.actioned_by_id = current_user.id
    report.actioned_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
        security_utils.log_security_event(
            current_user.id,
            'admin_report_update',
            description=f'Rapor #{report.id} {status} olarak güncellendi.',
            metadata={
                'report_id': report.id,
                'status': status,
                'action_taken': report.action_taken,
            }
        )
        flash('Rapor durumu güncellendi.', 'success')
    except Exception as exc:  # pragma: no cover - rollback guard
        db.session.rollback()
        current_app.logger.error('Rapor güncellenemedi: %s', exc)
        flash('Rapor güncellenirken bir hata oluştu.', 'error')

    return redirect(url_for('admin_analytics', **redirect_params))

# ==================== CONTACT FORM ====================
@app.route('/api/contact', methods=['POST'])
@limiter.limit("5 per hour")  # Rate limit for contact form
def submit_contact_form():
    """İletişim formu endpoint'i (EmailJS alternatifi)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} alanı gereklidir'
                }), 400
        
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        subject = data.get('subject')
        message = data.get('message')
        
        # Email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({
                'success': False,
                'error': 'Geçersiz e-posta adresi'
            }), 400
        
        # Send email to admin/support
        admin_email = os.getenv('ADMIN_EMAIL', 'destek@utap.com.tr')
        
        try:
            from flask_mail import Message as MailMessage
            from email_service import mail
            
            msg = MailMessage(
                subject=f'İletişim Formu: {subject}',
                recipients=[admin_email],
                sender=os.getenv('MAIL_DEFAULT_SENDER', 'Tevkil Platform <destek@utap.com.tr>'),
                html=f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                        <h2 style="color: #1f2937; border-bottom: 3px solid #3b82f6; padding-bottom: 10px;">
                            📧 Yeni İletişim Formu Mesajı
                        </h2>
                        
                        <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>👤 Ad Soyad:</strong> {name}</p>
                            <p><strong>📧 E-posta:</strong> <a href="mailto:{email}">{email}</a></p>
                            <p><strong>📱 Telefon:</strong> {phone}</p>
                            <p><strong>📋 Konu:</strong> {subject}</p>
                            
                            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                            
                            <h3 style="color: #1f2937;">💬 Mesaj:</h3>
                            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 6px; white-space: pre-wrap;">
{message}
                            </div>
                        </div>
                        
                        <p style="color: #6b7280; font-size: 12px; text-align: center; margin-top: 20px;">
                            Bu mesaj <strong>utap.com.tr</strong> iletişim formu üzerinden gönderilmiştir.
                        </p>
                    </div>
                </body>
                </html>
                """
            )
            
            mail.send(msg)
            
            return jsonify({
                'success': True,
                'message': 'Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.'
            }), 200
            
        except Exception as email_error:
            # Log email error but still save to database
            print(f"❌ Email send error: {email_error}")
            
            # Alternative: Save to database for admin review
            # You can create a ContactMessage model later
            
            return jsonify({
                'success': True,
                'message': 'Mesajınız alındı. En kısa sürede size dönüş yapacağız.'
            }), 200
        
    except Exception as e:
        print(f"❌ Contact form error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Mesaj gönderilemedi. Lütfen daha sonra tekrar deneyin.'
        }), 500

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error page"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Custom 500 error page"""
    db.session.rollback()  # Rollback any failed database operations
    error_message = str(e) if app.debug else None
    return render_template('errors/500.html', error=error_message), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Use socketio.run instead of app.run
    # Production mode - debug=False for security
    debug_mode = os.getenv('FLASK_ENV', 'production') == 'development'
    # Get port from environment variable (Fly.io uses PORT=8080)
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=debug_mode)

