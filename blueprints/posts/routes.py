"""
Posts Routes
Handles tevkil post CRUD operations
"""
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime, timezone
from . import posts_bp
from .forms import PostForm
from models import db, TevkilPost, Application
from constants import CITIES, COURTHOUSES, TASK_CATEGORY_DEFINITIONS

@posts_bp.route('/')
def list():
    """List all active posts"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Filter active posts
    posts_query = TevkilPost.query.filter_by(status='active').order_by(TevkilPost.created_at.desc())
    
    # Apply filters if provided
    law_category = request.args.get('category')
    city = request.args.get('city')
    urgency = request.args.get('urgency')
    
    # Default to user's city if authenticated and no city filter is provided
    if city is None and current_user.is_authenticated and current_user.city:
        city = current_user.city
    
    if law_category:
        posts_query = posts_query.filter_by(category=law_category)
    if city:
        posts_query = posts_query.filter_by(city=city)
    if urgency:
        posts_query = posts_query.filter_by(urgency_level=urgency)
    
    posts = posts_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('pages/posts/list.html', posts=posts, cities=CITIES, current_city=city)

@posts_bp.route('/my-posts')
@login_required
def my_posts():
    """List current user's posts"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    posts = TevkilPost.query.filter_by(user_id=current_user.id)\
        .order_by(TevkilPost.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('pages/posts/my_posts.html', posts=posts)

@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new post"""
    form = PostForm()
    form.city.choices = [('', 'Şehir Seçiniz')] + [(city, city) for city in CITIES]
    
    # Adliye seçeneklerini dinamik olarak doldur (POST durumunda)
    if form.city.data and form.city.data in COURTHOUSES:
        form.courthouse.choices = [(c, c) for c in COURTHOUSES[form.city.data]]
    else:
        form.courthouse.choices = []

    if form.validate_on_submit():
        # Başlık oluştur
        job_label = TASK_CATEGORY_DEFINITIONS.get(form.job_type.data, {}).get('label', form.job_type.data)
        title = f"{form.city.data} {form.courthouse.data} - {job_label}"

        post = TevkilPost(
            user_id=current_user.id,
            title=title,
            description=form.description.data,
            category=form.law_category.data,
            job_type=form.job_type.data,
            city=form.city.data,
            courthouse=form.courthouse.data,
            court_date=form.hearing_date.data,
            price=form.price.data,
            price_min=form.price.data, # Uyumluluk için
            price_max=form.price.data, # Uyumluluk için
            urgency_level=form.urgency_level.data,
            status='active'
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('İlanınız başarıyla oluşturuldu!', 'success')
        return redirect(url_for('posts.detail', id=post.id))
    
    return render_template('pages/posts/create.html', form=form, cities=CITIES, courthouses=COURTHOUSES)

@posts_bp.route('/<int:id>')
def detail(id):
    """View post details"""
    post = TevkilPost.query.get_or_404(id)
    
    # Check if current user has already applied
    has_applied = False
    if current_user.is_authenticated:
        has_applied = Application.query.filter_by(
            post_id=post.id,
            applicant_id=current_user.id
        ).first() is not None
    
    return render_template('pages/posts/detail_new.html', post=post, has_applied=has_applied)

@posts_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a post"""
    post = TevkilPost.query.get_or_404(id)
    
    # Check ownership
    if post.user_id != current_user.id:
        abort(403)
    
    form = PostForm(obj=post)
    
    # Form alanlarını modelden doldur (isim uyuşmazlığı olanlar)
    if request.method == 'GET':
        form.law_category.data = post.category
        form.hearing_date.data = post.court_date
        form.courthouse.data = post.courthouse
        form.job_type.data = post.job_type
        form.price.data = int(post.price) if post.price else None

    form.city.choices = [('', 'Şehir Seçiniz')] + [(city, city) for city in CITIES]
    
    # Adliye seçeneklerini dinamik olarak doldur
    if form.city.data and form.city.data in COURTHOUSES:
        form.courthouse.choices = [(c, c) for c in COURTHOUSES[form.city.data]]
    else:
        form.courthouse.choices = []
    
    if form.validate_on_submit():
        # Başlık güncelle
        job_label = TASK_CATEGORY_DEFINITIONS.get(form.job_type.data, {}).get('label', form.job_type.data)
        post.title = f"{form.city.data} {form.courthouse.data} - {job_label}"
        
        post.description = form.description.data
        post.category = form.law_category.data
        post.job_type = form.job_type.data
        post.city = form.city.data
        post.courthouse = form.courthouse.data
        post.court_date = form.hearing_date.data
        post.price = form.price.data
        post.price_min = form.price.data
        post.price_max = form.price.data
        post.urgency_level = form.urgency_level.data
        
        post.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        flash('İlan güncellendi!', 'success')
        return redirect(url_for('posts.detail', id=post.id))
    
    return render_template('pages/posts/edit.html', form=form, post=post, cities=CITIES, courthouses=COURTHOUSES)

@posts_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a post"""
    post = TevkilPost.query.get_or_404(id)
    
    # Check ownership
    if post.user_id != current_user.id:
        abort(403)
    
    # Hard delete
    db.session.delete(post)
    db.session.commit()
    
    flash('İlan tamamen silindi.', 'success')
    return redirect(url_for('posts.my_posts'))

@posts_bp.route('/<int:id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(id):
    """Toggle post active status"""
    post = TevkilPost.query.get_or_404(id)
    
    # Check ownership
    if post.user_id != current_user.id:
        abort(403)
    
    if post.status == 'active':
        post.status = 'cancelled'
    else:
        post.status = 'active'
        
    db.session.commit()
    
    status = 'aktifleştirildi' if post.status == 'active' else 'pasifleştirildi'
    flash(f'İlan {status}.', 'success')
    return redirect(url_for('posts.my_posts'))
