"""
Authentication Routes
Handles login, logout, and registration
"""
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from .forms import LoginForm, RegisterForm, ResetPasswordForm
from models import db, User
from sms_service import NetgsmSMSService
from email_service import send_email
import random

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('hub'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Başarıyla giriş yaptınız!', 'success')
            
            # Redirect to next page or hub
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('hub'))
        else:
            flash('E-posta veya şifre hatalı!', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('hub'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Create new user
        user = User(
            email=form.email.data.lower(),
            full_name=f"{form.first_name.data} {form.last_name.data}",
            phone=form.phone.data,
            bar_association=form.bar_association.data,
            bar_registration_number=form.bar_number.data,
            specializations=[form.law_specialization.data] if form.law_specialization.data else [],
            bio=form.bio.data,
            city=form.city.data,
            district=form.district.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Hesabınız başarıyla oluşturuldu! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login', registered='true'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    flash('Çıkış yaptınız.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password route"""
    if current_user.is_authenticated:
        return redirect(url_for('hub'))
        
    if request.method == 'POST':
        contact = request.form.get('contact')
        
        if not contact:
            flash('Lütfen e-posta veya telefon numarası girin.', 'danger')
            return redirect(url_for('auth.forgot_password'))
            
        if '@' in contact:
            # Email logic
            user = User.query.filter_by(email=contact.lower()).first()
            if user:
                token = user.get_reset_token()
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                send_email(
                    to=user.email,
                    subject='Şifre Sıfırlama İsteği',
                    template='email/reset_password.html',
                    user=user,
                    reset_url=reset_url
                )
            flash('Şifre sıfırlama bağlantısı e-posta adresinize gönderildi.', 'success')
            return redirect(url_for('auth.login'))
        else:
            # Phone logic
            # Clean phone number
            phone = contact.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if phone.startswith('0'):
                phone = phone[1:]
            if phone.startswith('+90'):
                phone = phone[3:]
            if phone.startswith('90'):
                phone = phone[2:]
                
            # Try to find user by phone
            user = User.query.filter(User.phone.like(f'%{phone}')).first()
            
            if user:
                # Generate OTP
                otp = str(random.randint(100000, 999999))
                session['reset_otp'] = otp
                session['reset_user_id'] = user.id
                
                # Send SMS
                sms = NetgsmSMSService()
                result = sms.send_otp(user.phone or phone, otp)
                
                if result['success']:
                    flash('Doğrulama kodu telefonunuza gönderildi.', 'success')
                    return redirect(url_for('auth.verify_otp'))
                else:
                    flash(f'SMS gönderilemedi: {result["message"]}', 'danger')
            else:
                flash('Bu telefon numarası ile kayıtlı kullanıcı bulunamadı.', 'warning')
                
    return render_template('auth/forgot_password.html')

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """Verify OTP route"""
    if 'reset_user_id' not in session or 'reset_otp' not in session:
        return redirect(url_for('auth.forgot_password'))
        
    if request.method == 'POST':
        otp = request.form.get('otp')
        if otp == session.get('reset_otp'):
            session['reset_verified'] = True
            return redirect(url_for('auth.reset_password_confirm'))
        else:
            flash('Hatalı doğrulama kodu!', 'danger')
            
    return render_template('auth/verify_otp.html')

@auth_bp.route('/reset-password-confirm', methods=['GET', 'POST'])
def reset_password_confirm():
    """Reset password confirm route"""
    if not session.get('reset_verified') or 'reset_user_id' not in session:
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user_id = session.get('reset_user_id')
        user = User.query.get(user_id)
        
        if user:
            user.set_password(form.password.data)
            db.session.commit()
            
            # Clear session
            session.pop('reset_otp', None)
            session.pop('reset_user_id', None)
            session.pop('reset_verified', None)
            
            flash('Şifreniz başarıyla güncellendi. Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Kullanıcı bulunamadı.', 'danger')
            
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('hub'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('Geçersiz veya süresi dolmuş token.', 'warning')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('�ifreniz ba�ar�yla g�ncellendi! Giri� yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='�ifre S�f�rlama', form=form)
