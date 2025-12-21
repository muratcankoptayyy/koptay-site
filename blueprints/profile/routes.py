"""
Profile Routes
Handles profile viewing and editing
"""
from flask import render_template, redirect, url_for, flash, abort, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from . import profile_bp
from .forms import ProfileForm
from models import db, User, TevkilPost, Notification
from datetime import datetime, timezone

@profile_bp.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Upload profile picture"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Dosya bulunamadı'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Dosya seçilmedi'})
        
    if file:
        filename = secure_filename(file.filename)
        # Benzersiz isim oluştur
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"avatar_{current_user.id}_{timestamp}_{filename}"
        
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Eski avatarı sil (opsiyonel, şimdilik kalsın)
        
        # DB güncelle
        current_user.avatar_url = f"/static/uploads/avatars/{unique_filename}"
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'avatar_url': current_user.avatar_url,
            'message': 'Profil fotoğrafı güncellendi'
        })
        
    return jsonify({'success': False, 'error': 'Yükleme başarısız'})

@profile_bp.route('/notifications')
@login_required
def notifications():
    """View user notifications"""
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc())\
        .all()
    
    # Mark all as read
    unread_exists = False
    for notification in notifications:
        if not notification.read_at:
            notification.read_at = datetime.now(timezone.utc)
            unread_exists = True
            
    if unread_exists:
        db.session.commit()
    
    return render_template('pages/notifications.html', notifications=notifications)

@profile_bp.route('/<int:user_id>')
def view(user_id):
    """View user profile"""
    user = User.query.get_or_404(user_id)
    
    # Get user's active posts
    posts = user.posts.filter_by(status='active').order_by(TevkilPost.created_at.desc()).limit(5).all()
    
    return render_template('pages/profile/view.html', user=user, posts=posts)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit current user's profile"""
    # Form için mevcut verileri ayarla
    class FormData:
        pass
    
    form_data = FormData()
    if current_user.full_name:
        name_parts = current_user.full_name.split(' ', 1)
        form_data.first_name = name_parts[0] if len(name_parts) > 0 else ''
        form_data.last_name = name_parts[1] if len(name_parts) > 1 else ''
    else:
        form_data.first_name = ''
        form_data.last_name = ''
    
    form_data.phone = current_user.phone
    form_data.bio = current_user.bio
    form_data.law_specialization = current_user.specializations[0] if current_user.specializations else ''
    form_data.experience_years = '0-2'  # Default
    form_data.city = current_user.city
    form_data.district = current_user.district
    form_data.address = current_user.address
    
    form = ProfileForm(obj=form_data)
    
    if form.validate_on_submit():
        # Full name'i birleştir
        current_user.full_name = f"{form.first_name.data} {form.last_name.data}"
        current_user.phone = form.phone.data
        current_user.bio = form.bio.data
        current_user.specializations = [form.law_specialization.data] if form.law_specialization.data else []
        current_user.city = form.city.data
        current_user.district = form.district.data
        current_user.address = form.address.data
        
        db.session.commit()
        
        flash('Profiliniz güncellendi!', 'success')
        
        # Platform bilgisini koru
        platform = request.args.get('platform')
        if platform:
            return redirect(url_for('profile.view', user_id=current_user.id, platform=platform))
        return redirect(url_for('profile.view', user_id=current_user.id))
    
    return render_template('pages/profile/edit.html', form=form)

@profile_bp.route('/my-profile')
@login_required
def my_profile():
    """View current user's own profile"""
    platform = request.args.get('platform')
    if platform:
        return redirect(url_for('profile.view', user_id=current_user.id, platform=platform))
    return redirect(url_for('profile.view', user_id=current_user.id))

@profile_bp.route('/verify', methods=['GET', 'POST'])
@login_required
def verify():
    """Account verification"""
    if request.method == 'POST':
        # TODO: Handle file upload
        # For now, just simulate
        flash('Doğrulama isteğiniz alındı. En kısa sürede incelenecektir.', 'success')
        return redirect(url_for('profile.view', user_id=current_user.id))
        
    return render_template('pages/profile/verify.html')
