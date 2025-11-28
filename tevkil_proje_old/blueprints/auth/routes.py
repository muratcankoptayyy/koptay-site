"""
Authentication routes.

Routes handled:
- /register (GET, POST)
- /login (GET, POST)
- /logout (GET, POST)
- /forgot-password (GET, POST)
- /reset-password/<token> (GET, POST)
- /verify-2fa (GET, POST)
"""

from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta, timezone
import secrets
import traceback

from blueprints.auth import auth_bp
from models import db, User, PasswordReset, UserSession
from tevkil.extensions import limiter
from utils.logger import get_logger
import input_validation
import security_utils

logger = get_logger(__name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    """Yeni kullanıcı kayıt işlemi"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'GET':
        return render_template('phoenix/auth/register.html')
    
    # POST: Handle registration
    form_values = {key: (request.form.get(key) or '').strip() for key in request.form}

    full_name = input_validation.sanitize_plain_text(form_values.get('full_name'))
    email_valid, email = input_validation.validate_email(form_values.get('email'))
    # Email'i her zaman lowercase yap
    email = email.lower() if email else ''
    
    phone_valid, phone = input_validation.validate_phone(form_values.get('phone'))
    
    # TC Kimlik No - OPSIYONEL
    tc_raw = (form_values.get('tc_number') or '').strip()
    if tc_raw:
        tc_valid, tc_number = input_validation.validate_tc_kimlik(tc_raw)
    else:
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
        logger.error(f"Registration validation failed for {email}: {errors}")
        for message in errors:
            flash(message, 'error')
        return render_template('phoenix/auth/register.html', form_data=form_values)

    # Email'i lowercase yaparak kontrol et
    existing_user = User.query.filter(db.func.lower(User.email) == email.lower()).first()
    if existing_user:
        logger.error(f"Registration blocked: email already exists ({email})")
        flash('Bu e-posta adresiyle daha önce kayıt yapılmış.', 'error')
        return render_template('phoenix/auth/register.html', form_data=form_values)

    duplicate_baro = User.query.filter_by(
        bar_association=bar_association,
        bar_registration_number=bar_registration_number
    ).first()
    if duplicate_baro:
        logger.error(f"Registration blocked: bar number already in use - {bar_association}/{bar_registration_number}")
        flash('Bu baro sicil numarası zaten kayıtlı.', 'error')
        return render_template('phoenix/auth/register.html', form_data=form_values)

    # User objesi oluştur - email lowercase
    user = User(
        full_name=full_name,
        email=email.lower(),
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
        logger.info(f"Yeni kullanıcı oluşturuldu: {user.email} (ID: {user.id})")
        
        # Veritabanına kaydedildiğini doğrula
        verify_user = User.query.filter_by(email=email.lower()).first()
        if verify_user:
            logger.info(f"Kullanıcı veritabanında doğrulandı: {verify_user.email} (ID: {verify_user.id})")
        else:
            logger.warning(f"UYARI: Kullanıcı commit edildi ama sorgulamada bulunamadı!")
            
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error('Kayıt sırasında hata: %s', exc)
        logger.error(f"Registration commit failed for {email}: {str(exc)}")
        traceback.print_exc()
        flash('Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyiniz.', 'error')
        return render_template('phoenix/auth/register.html', form_data=form_values)

    if current_app.config.get('EMAIL_ENABLED'):
        try:
            from email_service import send_welcome_email
            send_welcome_email(user)
        except Exception as email_error:
            current_app.logger.warning('Hoş geldiniz e-postası gönderilemedi: %s', email_error)

    flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """Kullanıcı girişi - Güvenlik özellikleriyle"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'GET':
        return render_template('phoenix/auth/login.html')
    
    # POST: Handle login
    raw_email = request.form.get('email') or ''
    email = input_validation.sanitize_plain_text(str(raw_email)).strip().lower()
    password = request.form.get('password')
    remember = request.form.get('remember', False)
    
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    logger.info(f"Login attempt: {email} from {ip_address}")
    logger.debug(f"Password length: {len(password) if password else 0}")
    
    # Case-insensitive email search
    user = User.query.filter(db.func.lower(User.email) == email.lower()).first()
    
    if not user:
        logger.error(f"User not found: {email}")
        security_utils.log_login_attempt(
            email, ip_address, user_agent, 
            success=False, failure_reason='user_not_found'
        )
        flash('Hatalı e-posta veya şifre', 'error')
        return render_template('phoenix/auth/login.html')
    
    # 1. HESAP KİLİDİ KONTROLÜ
    if user.account_locked_until and datetime.now(timezone.utc) < user.account_locked_until:
        remaining_minutes = int((user.account_locked_until - datetime.now(timezone.utc)).total_seconds() / 60)
        security_utils.log_security_event(
            user.id, 'login_attempt_while_locked', 'WARNING',
            f'Login attempt on locked account from {ip_address}'
        )
        flash(f'Hesabınız kilitli. {remaining_minutes} dakika sonra tekrar deneyin.', 'error')
        return render_template('phoenix/auth/login.html')
    
    # Kilit süresi dolduysa kilidi kaldır
    if user.account_locked_until and datetime.now(timezone.utc) >= user.account_locked_until:
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
    logger.debug(f"Checking password for {email}...")
    password_valid = user.check_password(password)
    
    if not password_valid:
        logger.error(f"Password incorrect for {email}")
        
        security_utils.log_login_attempt(
            email, ip_address, user_agent,
            success=False, failure_reason='invalid_password'
        )
        
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
        session['pending_2fa_user_id'] = user.id
        session['pending_2fa_remember'] = remember
        return redirect(url_for('auth.verify_2fa'))
    
    # 6. LOGIN BAŞARILI
    logger.info(f"Login successful: {email}")
    
    session.permanent = False
    login_user(user, remember=False)
    
    # Başarısız deneme sayısını sıfırla
    security_utils.reset_failed_attempts(user)
    
    # Son aktiflik zamanını güncelle
    user.last_active = datetime.now(timezone.utc)
    db.session.commit()
    
    # Session token oluştur
    session_token = security_utils.create_user_session(user.id)
    session['session_token'] = session_token
    
    # Başarılı login'i logla
    security_utils.log_login_attempt(email, ip_address, user_agent, success=True)
    security_utils.log_security_event(
        user.id, 'login_success', 'INFO',
        f'Successful login from {ip_address}'
    )
    
    # Redirect
    next_page = request.args.get('next')
    redirect_url = next_page or url_for('main.dashboard')
    
    return redirect(redirect_url)


@auth_bp.route('/logout', methods=['GET', 'POST'])
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
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Şifremi unuttum"""
    if request.method == 'GET':
        return render_template('phoenix/auth/forgot_password.html')
    
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
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        flash(f'Şifre sıfırlama bağlantısı: {reset_url}', 'info')
        flash('Şifre sıfırlama bağlantısı oluşturuldu. (Email entegrasyonu sonra eklenecek)', 'success')
    else:
        # Güvenlik için her zaman başarılı mesajı göster
        flash('Eğer bu e-posta kayıtlıysa, şifre sıfırlama bağlantısı gönderildi.', 'success')
    
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Şifre sıfırlama"""
    reset = PasswordReset.query.filter_by(token=token).first()
    
    if not reset or not reset.is_valid():
        flash('Geçersiz veya süresi dolmuş token', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'GET':
        return render_template('phoenix/auth/reset_password.html', token=token)
    
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
    return redirect(url_for('auth.login'))


@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def verify_2fa():
    """2FA doğrulama sayfası"""
    if 'pending_2fa_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['pending_2fa_user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
    
    if request.method == 'GET':
        return render_template('phoenix/security/verify_2fa.html', user=user)
    
    token = request.form.get('token', '').replace('-', '').replace(' ', '')
    use_backup = request.form.get('use_backup', False)
    
    verified = False
    
    if use_backup:
        verified = security_utils.verify_backup_code(user, token)
        if verified:
            security_utils.log_security_event(
                user.id, '2fa_backup_code_used', 'INFO',
                'Backup code used for 2FA verification'
            )
    else:
        verified = security_utils.verify_2fa_token(user.two_factor_secret, token)
    
    if verified:
        # 2FA başarılı
        remember = session.get('pending_2fa_remember', False)
        session.permanent = False
        login_user(user, remember=False)
        
        session['2fa_verified'] = True
        session.pop('pending_2fa_user_id', None)
        session.pop('pending_2fa_remember', None)
        
        user.last_active = datetime.now(timezone.utc)
        db.session.commit()
        
        session_token = security_utils.create_user_session(user.id)
        session['session_token'] = session_token
        
        security_utils.log_security_event(
            user.id, '2fa_verified', 'INFO',
            'Two-factor authentication verified successfully'
        )
        security_utils.log_login_attempt(
            user.email, request.remote_addr, 
            request.headers.get('User-Agent', ''), success=True
        )
        
        flash('Giriş başarılı!', 'success')
        return redirect(url_for('main.dashboard'))
    else:
        security_utils.log_security_event(
            user.id, '2fa_failed', 'WARNING',
            '2FA verification failed - invalid token'
        )
        flash('Geçersiz doğrulama kodu. Lütfen tekrar deneyin.', 'error')
    
    return render_template('phoenix/security/verify_2fa.html', user=user)
