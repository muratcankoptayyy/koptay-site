"""
Authentication Routes
Handles login, logout, and registration
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from .forms import LoginForm, RegisterForm
from models import db, User

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Başarıyla giriş yaptınız!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('E-posta veya şifre hatalı!', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
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
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    flash('Çıkış yaptınız.', 'info')
    return redirect(url_for('index'))
