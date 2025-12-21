from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import settings_bp
from models import db

@settings_bp.route('/')
@login_required
def index():
    """Ayarlar sayfası"""
    return render_template('pages/settings/index.html')

@settings_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Profil bilgilerini güncelle"""
    try:
        current_user.full_name = request.form.get('full_name')
        current_user.phone = request.form.get('phone')
        current_user.whatsapp_number = request.form.get('whatsapp_number')
        current_user.city = request.form.get('city')
        current_user.district = request.form.get('district')
        current_user.bar_association = request.form.get('bar_association')
        current_user.registration_number = request.form.get('registration_number')
        current_user.specialization = request.form.get('specialization')
        current_user.about = request.form.get('about')
        
        db.session.commit()
        flash('Profil bilgileriniz başarıyla güncellendi!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Bir hata oluştu. Lütfen tekrar deneyin.', 'error')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/update-password', methods=['POST'])
@login_required
def update_password():
    """Şifre güncelle"""
    from werkzeug.security import check_password_hash, generate_password_hash
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not check_password_hash(current_user.password_hash, current_password):
        flash('Mevcut şifreniz yanlış!', 'error')
        return redirect(url_for('settings.index'))
    
    if new_password != confirm_password:
        flash('Yeni şifreler eşleşmiyor!', 'error')
        return redirect(url_for('settings.index'))
    
    if len(new_password) < 6:
        flash('Şifre en az 6 karakter olmalıdır!', 'error')
        return redirect(url_for('settings.index'))
    
    try:
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Şifreniz başarıyla güncellendi!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Bir hata oluştu. Lütfen tekrar deneyin.', 'error')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    """Destek ve Geri Bildirim"""
    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # TODO: Save to database or send email
        # For now, just flash
        flash('Geri bildiriminiz alındı. Teşekkür ederiz!', 'success')
        return redirect(url_for('settings.support'))
        
    return render_template('pages/settings/support.html')
