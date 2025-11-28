"""
Profile Routes
Handles profile viewing and editing
"""
from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from . import profile_bp
from .forms import ProfileForm
from models import db, User, TevkilPost

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
        return redirect(url_for('profile.view', user_id=current_user.id))
    
    return render_template('pages/profile/edit.html', form=form)

@profile_bp.route('/my-profile')
@login_required
def my_profile():
    """View current user's own profile"""
    return redirect(url_for('profile.view', user_id=current_user.id))
