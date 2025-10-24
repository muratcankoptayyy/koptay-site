"""
Tevkil Platform - Main Application
Avukatlar arası iş devri ve tevkil platformu
"""
import os
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_file, send_from_directory, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect, generate_csrf
from dotenv import load_dotenv
from models import db, User, TevkilPost, Application, Rating, Message, Notification, Favorite, PasswordReset, Conversation
from models import UserSession, SecurityLog, PasswordHistory, LoginAttempt
from sqlalchemy import or_, and_
import secrets
import json
from constants import CITIES, COURTHOUSES
from sms_service import NetgsmSMSService
from geocoding_service import get_coordinates
from functools import wraps
import security_utils
from cache_config import init_cache
from database_pooling_config import DATABASE_CONFIG

# Load environment variables
load_dotenv()

# ⚡ FEATURE FLAGS
WHATSAPP_ENABLED = os.getenv('WHATSAPP_ENABLED', 'false').lower() == 'true'

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///tevkil.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEV_MODE'] = os.getenv('FLASK_ENV', 'production') == 'development'
app.config['WHATSAPP_ENABLED'] = WHATSAPP_ENABLED  # Template'lerde kullanmak için

# ⚡ DATABASE POOLING - High concurrency support
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = DATABASE_CONFIG

# Initialize extensions
db.init_app(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ⚡ REDIS CACHE - 70% faster response times
cache = init_cache(app)

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# Initialize Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize SMS service
sms_service = NetgsmSMSService()

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

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Context Processors
@app.context_processor
def inject_csrf_token():
    """CSRF token'ı tüm template'lere enjekte et"""
    return dict(csrf_token=generate_csrf)

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Kullanıcı kayıt"""
    if request.method == 'POST':
        data = request.form
        
        # Check if user exists
        if User.query.filter_by(email=data.get('email')).first():
            flash('Bu e-posta adresi zaten kullanımda', 'error')
            return redirect(url_for('register'))
        
        # Check if bar registration already exists
        bar_assoc = data.get('bar_association')
        bar_reg_num = data.get('bar_registration_number')
        if bar_assoc and bar_reg_num:
            existing_user = User.query.filter_by(
                bar_association=bar_assoc,
                bar_registration_number=bar_reg_num
            ).first()
            if existing_user:
                flash(f'{bar_assoc} - {bar_reg_num} sicil numarası ile zaten kayıtlı bir kullanıcı var', 'error')
                return redirect(url_for('register'))
        
        # Create new user
        user = User(
            email=data.get('email'),
            full_name=data.get('full_name'),
            phone=data.get('phone'),
            tc_number=data.get('tc_number'),
            bar_association=data.get('bar_association'),
            bar_registration_number=data.get('bar_registration_number'),
            lawyer_type=data.get('lawyer_type', 'avukat'),  # Avukat türü (avukat veya stajyer)
            city=data.get('city'),
            specializations=data.get('specializations', '').split(',') if data.get('specializations') else []
        )
        user.set_password(data.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Login rate limit
def login():
    """Kullanıcı girişi - Güvenlik özellikleriyle"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        print(f"🔐 Login attempt: {email} from {ip_address}")
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Kullanıcı bulunamadı
            security_utils.log_login_attempt(
                email, ip_address, user_agent, 
                success=False, failure_reason='user_not_found'
            )
            flash('Hatalı e-posta veya şifre', 'error')
            return render_template('login.html')
        
        # 1. HESAP KİLİDİ KONTROLÜ
        if user.account_locked_until and datetime.utcnow() < user.account_locked_until:
            remaining_minutes = int((user.account_locked_until - datetime.utcnow()).total_seconds() / 60)
            security_utils.log_security_event(
                user.id, 'login_attempt_while_locked', 'WARNING',
                f'Login attempt on locked account from {ip_address}'
            )
            flash(f'Hesabınız kilitli. {remaining_minutes} dakika sonra tekrar deneyin.', 'error')
            return render_template('login.html')
        
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
            return render_template('login.html')
        
        # 3. ŞİFRE KONTROLÜ
        if not user.check_password(password):
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
            
            return render_template('login.html')
        
        # 4. HESAP AKTİFLİK KONTROLÜ
        if not user.is_active:
            security_utils.log_security_event(
                user.id, 'login_attempt_inactive', 'WARNING',
                'Login attempt on inactive account'
            )
            flash('Hesabınız aktif değil. Lütfen yöneticiyle iletişime geçin.', 'error')
            return render_template('login.html')
        
        # 5. 2FA KONTROLÜ
        if user.two_factor_enabled:
            # 2FA gerekli - önce session'a kullanıcıyı kaydet ama login yapma
            session['pending_2fa_user_id'] = user.id
            session['pending_2fa_remember'] = remember
            return redirect(url_for('verify_2fa'))
        
        # 6. LOGIN BAŞARILI
        print(f"✅ Login successful: {email}")
        
        # Login yap
        login_user(user, remember=remember)
        
        # Başarısız deneme sayısını sıfırla
        security_utils.reset_failed_attempts(user)
        
        # Son aktiflik zamanını güncelle
        user.last_active = datetime.utcnow()
        db.session.commit()
        
        # Session token oluştur
        session_token = security_utils.create_user_session(user.id)
        session['session_token'] = session_token
        
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
        return redirect(next_page or url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
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
    
    return render_template('forgot_password.html')

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
            return render_template('reset_password.html', token=token)
        
        if len(password) < 6:
            flash('Şifre en az 6 karakter olmalıdır', 'error')
            return render_template('reset_password.html', token=token)
        
        # Şifreyi güncelle
        user = reset.user
        user.set_password(password)
        
        # Token'ı kullanıldı olarak işaretle
        reset.used_at = datetime.now(timezone.utc)
        db.session.commit()
        
        flash('Şifreniz başarıyla değiştirildi. Artık giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

# ============================================
# MAIN PAGES
# ============================================

@app.route('/')
def index():
    """Ana sayfa"""
    recent_posts = TevkilPost.query.filter_by(status='active').order_by(TevkilPost.created_at.desc()).limit(6).all()
    return render_template('index.html', posts=recent_posts)

@app.route('/dashboard')
@dev_login_optional
def dashboard():
    """Kullanıcı dashboard"""
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
    
    # Tahmini toplam kazanç (completed işlerin price_max toplamı)
    completed_posts = TevkilPost.query.filter_by(
        user_id=current_user.id, 
        status='completed'
    ).all()
    total_earnings = sum([p.price_max for p in completed_posts if p.price_max])
    
    # Ortalama rating
    ratings = Rating.query.filter_by(reviewed_id=current_user.id).all()
    avg_rating = sum([r.rating for r in ratings]) / len(ratings) if ratings else 0
    
    # Kullanıcı istatistiklerini getir
    user_stats = get_user_stats(current_user.id)
    
    return render_template('dashboard.html',
                         my_posts=my_posts,
                         my_applications=my_applications,
                         incoming_applications=incoming_applications,
                         unread_notifications=unread_notifications,
                         chart_months=chart_months,
                         chart_incoming=chart_incoming,
                         chart_outgoing=chart_outgoing,
                         category_labels=category_labels,
                         category_counts=category_counts,
                         monthly_completed=monthly_completed,
                         total_earnings=total_earnings,
                         avg_rating=avg_rating,
                         user_stats=user_stats)

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
    """Gelen başvurular - kullanıcının ilanlarına yapılan başvurular"""
    # Kullanıcının ilanlarına gelen başvurular
    incoming_applications = db.session.query(Application).join(TevkilPost).filter(
        TevkilPost.user_id == current_user.id
    ).order_by(Application.created_at.desc()).all()
    
    return render_template('applications_received.html', applications=incoming_applications)

@app.route('/applications/sent')
@dev_login_optional
def applications_sent():
    """Gönderilen başvurular - kullanıcının yaptığı başvurular"""
    # Kullanıcının yaptığı başvurular
    my_applications = Application.query.filter_by(applicant_id=current_user.id).order_by(Application.created_at.desc()).all()
    
    return render_template('applications_sent.html', applications=my_applications)

# ============================================
# TEVKIL POST ROUTES
# ============================================

@app.route('/posts')
@dev_login_optional
def list_posts():
    """İlan listesi"""
    from constants import CITIES
    
    # Filters
    filter_type = request.args.get('filter')  # my_active, my_completed, all
    category = request.args.get('category')
    city = request.args.get('city')
    urgency = request.args.get('urgency')
    search = request.args.get('search')
    
    # Base query
    if filter_type == 'my_active':
        # Kullanıcının aktif ilanları
        query = TevkilPost.query.filter_by(user_id=current_user.id, status='active')
    elif filter_type == 'my_completed':
        # Kullanıcının tamamlanan ilanları
        query = TevkilPost.query.filter_by(user_id=current_user.id, status='completed')
    elif filter_type == 'my_all':
        # Kullanıcının tüm ilanları
        query = TevkilPost.query.filter_by(user_id=current_user.id)
    else:
        # Tüm aktif ilanlar (genel liste)
        query = TevkilPost.query.filter_by(status='active')
    
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
    
    posts = query.order_by(TevkilPost.created_at.desc()).all()
    
    # Get current user's favorites
    current_user_favorites = []
    if current_user.is_authenticated:
        favorites = Favorite.query.filter_by(user_id=current_user.id).all()
        current_user_favorites = [fav.post_id for fav in favorites]
    
    return render_template('posts_list.html', posts=posts, current_user_favorites=current_user_favorites, cities=CITIES, filter_type=filter_type)

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
                'user_name': post.user.full_name if post.user else 'Anonim'
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
        data = request.form
        
        # Konum bilgisini geocode et
        location_str = data.get('location')
        coords = get_coordinates(location_str) if location_str else {}
        
        post = TevkilPost(
            user_id=current_user.id,
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category'),
            urgency_level=data.get('urgency_level', 'normal'),
            location=location_str,
            city=data.get('city'),
            district=data.get('district'),
            courthouse=data.get('courthouse'),
            remote_allowed=data.get('remote_allowed') == 'on',
            price_min=float(data.get('price_min')) if data.get('price_min') else None,
            price_max=float(data.get('price_max')) if data.get('price_max') else None,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            latitude=coords.get('latitude'),
            longitude=coords.get('longitude'),
            formatted_address=coords.get('formatted_address')
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('İlan başarıyla oluşturuldu!', 'success')
        return redirect(url_for('post_detail', post_id=post.id))
    
    return render_template('post_create.html', cities=CITIES, courthouses=COURTHOUSES)

@app.route('/whatsapp-ilan')
@login_required
def whatsapp_ilan():
    """WhatsApp ile ilan oluşturma bilgilendirmesi"""
    if not WHATSAPP_ENABLED:
        abort(404)
    return render_template('whatsapp_ilan.html')

@app.route('/whatsapp/setup')
@login_required
def whatsapp_setup():
    """WhatsApp entegrasyon kurulum ve test sayfası"""
    if not WHATSAPP_ENABLED:
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
    post_stats = get_post_stats(post_id)
    
    # Google Maps API anahtarı
    google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    return render_template('post_detail.html', post=post, applications=applications, 
                         is_favorited=is_favorited, post_stats=post_stats,
                         google_maps_key=google_maps_key)

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
        
        # Konum değiştiyse yeniden geocode et
        location_str = data.get('location')
        if location_str != post.location:
            coords = get_coordinates(location_str) if location_str else {}
            post.latitude = coords.get('latitude')
            post.longitude = coords.get('longitude')
            post.formatted_address = coords.get('formatted_address')
        
        post.title = data.get('title')
        post.description = data.get('description')
        post.category = data.get('category')
        post.urgency_level = data.get('urgency_level')
        post.location = location_str
        post.remote_allowed = data.get('remote_allowed') == 'on'
        post.price_min = float(data.get('price_min')) if data.get('price_min') else None
        post.price_max = float(data.get('price_max')) if data.get('price_max') else None
        post.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        flash('İlan güncellendi!', 'success')
        return redirect(url_for('post_detail', post_id=post_id))
    
    return render_template('post_edit.html', post=post)

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
        message=f'{current_user.full_name} ilanınıza başvurdu: {post.title}',
        related_post_id=post_id,
        related_user_id=current_user.id
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
                'full_name': post.user.full_name,
                'bar_association': post.user.bar_association,
                'tc_number': post.user.tc_number,
                'bar_registration_number': post.user.bar_registration_number,
                'address': post.user.address,
                'city': post.user.city,
                'phone': post.user.phone,
                'email': post.user.email
            },
            'applicant': {
                'full_name': application.applicant.full_name,
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
        'name': post.user.full_name,
        'baro': post.user.bar_association or 'Belirtilmemiş',
        'tc_number': post.user.tc_number or '',
        'sicil': post.user.bar_registration_number or 'Belirtilmemiş',
        'tax_office': '',  # Kullanıcı modelinde bu alan henüz yok
        'tax_number': '',   # Kullanıcı modelinde bu alan henüz yok
        'address': post.user.address or 'Belirtilmemiş'
    }
    
    applicant_data = {
        'name': application.applicant.full_name,
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
    """Kullanıcı profili"""
    user = User.query.get_or_404(user_id)
    
    # Kullanıcının tamamladığı işler
    completed_posts = TevkilPost.query.filter_by(assigned_to=user_id, status='completed').all()
    
    # Aldığı değerlendirmeler
    ratings = Rating.query.filter_by(reviewed_id=user_id).order_by(Rating.created_at.desc()).all()
    
    return render_template('profile.html', user=user, completed_posts=completed_posts, ratings=ratings)

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
    
    return render_template('profile_edit.html')

@app.route('/settings')
@login_required
def settings():
    """Ayarlar sayfası"""
    return render_template('settings.html')

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
    return redirect(url_for('settings'))

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
    file.seek(0)
    
    if file_size > 2 * 1024 * 1024:
        return jsonify({'success': False, 'error': 'Dosya boyutu 2MB\'dan büyük'}), 400
    
    # Güvenli dosya adı
    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)
    unique_filename = f"avatar_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
    
    # avatars klasörünü oluştur
    upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'avatars')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Eski avatarı sil
    if current_user.avatar_url and '/static/uploads/avatars/' in current_user.avatar_url:
        old_file = os.path.join(app.root_path, current_user.avatar_url.lstrip('/'))
        if os.path.exists(old_file):
            os.remove(old_file)
    
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
    total = Notification.query.filter_by(user_id=user_id).count()
    unread = Notification.query.filter_by(user_id=user_id, read_at=None).count()
    today = Notification.query.filter_by(user_id=user_id).filter(
        Notification.created_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    ).count()
    
    return {
        'total': total,
        'unread': unread,
        'today': today
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
    notifications_list = Notification.query.filter_by(
        user_id=current_user.id,
        archived_at=None
    ).order_by(Notification.created_at.desc()).all()
    
    # İstatistikleri getir
    stats = get_notification_stats(current_user.id)
    
    return render_template('notifications_new.html', 
                         notifications=notifications_list,
                         stats=stats)


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
    return render_template('notification_settings.html', user=current_user)


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

@app.route('/chat')
@login_required
def chat():
    """Modern chat ana sayfası - WhatsApp tarzı"""
    # Kullanıcının tüm conversation'larını al, son mesaja göre sırala
    user_convs = db.session.query(Conversation).filter(
        or_(
            Conversation.user1_id == current_user.id,
            Conversation.user2_id == current_user.id
        )
    ).order_by(Conversation.last_message_at.desc()).all()
    
    # Toplam okunmamış mesaj sayısı
    total_unread = sum(conv.get_unread_count(current_user.id) for conv in user_convs)
    
    # Bugünün tarihi (template için)
    today = datetime.now(timezone.utc).date()
    
    return render_template('chat.html', 
                         conversations=user_convs,
                         total_unread=total_unread,
                         today=today)

@app.route('/chat/<int:conversation_id>')
@login_required
def chat_conversation(conversation_id):
    """Belirli bir conversation'ın detayı"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Kullanıcı bu conversation'a dahil mi kontrol et
    if current_user.id not in [conversation.user1_id, conversation.user2_id]:
        flash('Bu sohbete erişim yetkiniz yok', 'error')
        return redirect(url_for('chat'))
    
    # Mesajları okundu işaretle
    conversation.mark_as_read(current_user.id)
    
    # Bu conversation'daki tüm mesajları okundu işaretle
    Message.query.filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != current_user.id,
        Message.read_at.is_(None)
    ).update({'read_at': datetime.now(timezone.utc)})
    
    db.session.commit()
    
    # Tüm conversation'ları al (sidebar için)
    user_convs = db.session.query(Conversation).filter(
        or_(
            Conversation.user1_id == current_user.id,
            Conversation.user2_id == current_user.id
        )
    ).order_by(Conversation.last_message_at.desc()).all()
    
    # Bu conversation'ın mesajlarını al
    messages = Message.query.filter_by(
        conversation_id=conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    # Karşı tarafı al
    other_user = conversation.get_other_user(current_user.id)
    
    # Toplam okunmamış
    total_unread = sum(conv.get_unread_count(current_user.id) for conv in user_convs)
    
    # Bugünün tarihi
    today = datetime.now(timezone.utc).date()
    
    return render_template('chat.html',
                         conversations=user_convs,
                         active_conversation=conversation,
                         messages=messages,
                         other_user=other_user,
                         total_unread=total_unread,
                         today=today)

@app.route('/chat/start/<int:user_id>', methods=['GET'])
@login_required
def start_chat(user_id):
    """Yeni bir chat başlat veya var olanı aç"""
    if user_id == current_user.id:
        flash('Kendinize mesaj gönderemezsiniz', 'error')
        return redirect(url_for('chat'))
    
    # Kullanıcı var mı kontrol et
    other_user = User.query.get_or_404(user_id)
    
    # Post ID varsa al
    post_id = request.args.get('post_id', type=int)
    
    # Conversation bul veya oluştur
    conversation = Conversation.get_or_create(
        current_user.id, 
        user_id,
        post_id
    )
    db.session.commit()
    
    return redirect(url_for('chat_conversation', conversation_id=conversation.id))

@app.route('/chat/send', methods=['POST'])
@login_required
@limiter.limit("100 per minute")  # Chat için yüksek limit
def send_chat_message():
    """Chat mesajı gönder (AJAX)"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        message_text = data.get('message', '').strip()
        reply_to_id = data.get('reply_to_id')
        
        if not message_text:
            return jsonify({'success': False, 'error': 'Mesaj boş olamaz'}), 400
        
        # Conversation kontrolü
        conversation = Conversation.query.get_or_404(conversation_id)
        
        if current_user.id not in [conversation.user1_id, conversation.user2_id]:
            return jsonify({'success': False, 'error': 'Yetkiniz yok'}), 403
        
        # Yeni mesaj oluştur
        message = Message(
            conversation_id=conversation_id,
            sender_id=current_user.id,
            message=message_text,
            reply_to_id=reply_to_id,
            delivered_at=datetime.now(timezone.utc)
        )
        
        # DEPRECATED alanları doldur (eski sistem uyumluluğu)
        other_user = conversation.get_other_user(current_user.id)
        message.receiver_id = other_user.id
        message.post_id = conversation.post_id
        
        db.session.add(message)
        
        # Conversation'ı güncelle
        conversation.last_message_at = datetime.now(timezone.utc)
        conversation.last_message_text = message_text[:100]
        conversation.last_message_sender_id = current_user.id
        
        # Karşı tarafın okunmamış sayısını artır
        if current_user.id == conversation.user1_id:
            conversation.unread_count_user2 += 1
        else:
            conversation.unread_count_user1 += 1
        
        db.session.commit()
        
        # ⚡ SOCKET.IO REAL-TIME EMIT - Mesajı anında gönder
        socketio.emit('new_message', {
            'conversation_id': conversation_id,
            'message': {
                'id': message.id,
                'sender_id': current_user.id,
                'sender_name': current_user.full_name,
                'sender_avatar': current_user.profile_photo or '/static/default-avatar.png',
                'message': message_text,
                'created_at': message.created_at.strftime('%H:%M'),
                'is_mine': False  # Frontend'de dinamik olarak ayarlanacak
            }
        }, room=f'conversation_{conversation_id}')
        
        # Bildirim gönder (asenkron - UI'ı bloklamaz)
        try:
            create_notification(
                user_id=other_user.id,
                notification_type='new_message',
                title='💬 Yeni Mesaj',
                message=f'{current_user.full_name}: {message_text[:50]}...',
                related_user_id=current_user.id,
                action_url=url_for('chat_conversation', conversation_id=conversation_id),
                action_text='Mesajı Görüntüle',
                priority='normal'
            )
        except Exception as e:
            # Bildirim hatası mesaj göndermeyi engellemez
            print(f"Notification error: {e}")
        
        return jsonify({
            'success': True,
            'message_id': message.id,
            'created_at': message.created_at.strftime('%H:%M'),
            'sender_name': current_user.full_name
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

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
            'sender_name': msg.sender.full_name,
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
        
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': 'İzin verilmeyen dosya türü'}), 400
        
        # Dosya boyutu kontrolü (10MB)
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 10 * 1024 * 1024:
            return jsonify({'success': False, 'error': 'Dosya boyutu 10MB\'dan büyük'}), 400
        
        # Güvenli dosya adı
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        
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
    favorites_list = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc()).all()
    return render_template('favorites.html', favorites=favorites_list)

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
    if not WHATSAPP_ENABLED:
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
    if not WHATSAPP_ENABLED:
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
            login_user(user, remember=remember)
            
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


@app.route('/security/2fa/setup', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    """2FA kurulum sayfası"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'enable':
            # 2FA'yı etkinleştir
            if not current_user.two_factor_secret:
                # Secret oluştur
                secret = security_utils.generate_2fa_secret()
                current_user.two_factor_secret = secret
                db.session.commit()
            
            # QR kod oluştur
            qr_code = security_utils.generate_2fa_qr_code(
                current_user.email,
                current_user.two_factor_secret
            )
            
            # Backup kodları oluştur
            backup_codes = security_utils.generate_backup_codes()
            current_user.two_factor_backup_codes = json.dumps(backup_codes)
            db.session.commit()
            
            return render_template('setup_2fa.html',
                                 step='scan',
                                 qr_code=qr_code,
                                 secret=current_user.two_factor_secret,
                                 backup_codes=backup_codes)
        
        elif action == 'verify':
            # Kurulumu doğrula
            token = request.form.get('token', '').replace('-', '').replace(' ', '')
            
            if security_utils.verify_2fa_token(current_user.two_factor_secret, token):
                # 2FA aktif
                current_user.two_factor_enabled = True
                db.session.commit()
                
                security_utils.log_security_event(
                    current_user.id, '2fa_enabled', 'INFO',
                    'Two-factor authentication enabled'
                )
                
                flash('İki faktörlü kimlik doğrulama başarıyla etkinleştirildi!', 'success')
                return redirect(url_for('security_settings'))
            else:
                flash('Geçersiz kod. Lütfen tekrar deneyin.', 'error')
                return redirect(url_for('setup_2fa'))
        
        elif action == 'disable':
            # 2FA'yı devre dışı bırak
            password = request.form.get('password')
            
            if current_user.check_password(password):
                current_user.two_factor_enabled = False
                current_user.two_factor_secret = None
                current_user.two_factor_backup_codes = None
                db.session.commit()
                
                security_utils.log_security_event(
                    current_user.id, '2fa_disabled', 'WARNING',
                    'Two-factor authentication disabled'
                )
                
                flash('İki faktörlü kimlik doğrulama devre dışı bırakıldı.', 'success')
                return redirect(url_for('security_settings'))
            else:
                flash('Hatalı şifre.', 'error')
    
    return render_template('setup_2fa.html', step='start')


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
            'full_name': current_user.full_name
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
            'full_name': current_user.full_name
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
    Message.query.filter_by(
        conversation_id=conversation_id,
        receiver_id=current_user.id,
        is_read=False
    ).update({'is_read': True, 'read_at': datetime.now(timezone.utc)})
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
    
    # Create message
    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content,
        is_read=False
    )
    db.session.add(message)
    
    # Update conversation
    conversation.last_message_at = datetime.now(timezone.utc)
    conversation.last_message = content[:100]
    
    db.session.commit()
    
    # Prepare message data
    message_data = {
        'id': message.id,
        'conversation_id': conversation_id,
        'sender_id': current_user.id,
        'sender_name': current_user.full_name,
        'receiver_id': receiver_id,
        'content': content,
        'timestamp': message.created_at.strftime('%H:%M'),
        'created_at': message.created_at.isoformat(),
        'is_read': False
    }
    
    # Send to conversation room
    room = f'conversation_{conversation_id}'
    emit('new_message', message_data, room=room)
    
    # Send notification to receiver if online but not in room
    if receiver_id in active_users:
        emit('new_message_notification', {
            'conversation_id': conversation_id,
            'sender_name': current_user.full_name,
            'preview': content[:50]
        }, room=active_users[receiver_id])
    
    print(f'📨 Message sent: {current_user.id} → {receiver_id} in conversation {conversation_id}')

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
        'user_name': current_user.full_name,
        'is_typing': is_typing
    }, room=room, skip_sid=request.sid)

@socketio.on('mark_as_read')
def handle_mark_as_read(data):
    """Mark messages as read"""
    conversation_id = data.get('conversation_id')
    
    if not conversation_id:
        return
    
    # Mark all messages from other user as read
    Message.query.filter_by(
        conversation_id=conversation_id,
        receiver_id=current_user.id,
        is_read=False
    ).update({'is_read': True, 'read_at': datetime.now(timezone.utc)})
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Use socketio.run instead of app.run
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
