"""
Posts Routes
Handles tevkil post CRUD operations
"""
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime
from . import posts_bp
from .forms import PostForm
from models import db, TevkilPost, Application

@posts_bp.route('/')
def list():
    """List all active posts"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Filter active posts
    posts_query = TevkilPost.query.filter_by(is_active=True).order_by(TevkilPost.created_at.desc())
    
    # Apply filters if provided
    law_category = request.args.get('category')
    city = request.args.get('city')
    urgency = request.args.get('urgency')
    
    if law_category:
        posts_query = posts_query.filter_by(law_category=law_category)
    if city:
        posts_query = posts_query.filter_by(city=city)
    if urgency:
        posts_query = posts_query.filter_by(urgency_level=urgency)
    
    posts = posts_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('pages/posts/list.html', posts=posts)

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
    
    if form.validate_on_submit():
        post = TevkilPost(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            law_category=form.law_category.data,
            case_type=form.case_type.data,
            city=form.city.data,
            district=form.district.data,
            court_name=form.court_name.data,
            file_number=form.file_number.data,
            hearing_date=form.hearing_date.data,
            budget_min=form.budget_min.data,
            budget_max=form.budget_max.data,
            urgency_level=form.urgency_level.data,
            is_active=True
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('İlanınız başarıyla oluşturuldu!', 'success')
        return redirect(url_for('posts.detail', id=post.id))
    
    return render_template('pages/posts/create.html', form=form)

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
    
    return render_template('pages/posts/detail.html', post=post, has_applied=has_applied)

@posts_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a post"""
    post = TevkilPost.query.get_or_404(id)
    
    # Check ownership
    if post.user_id != current_user.id:
        abort(403)
    
    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        form.populate_obj(post)
        post.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('İlan güncellendi!', 'success')
        return redirect(url_for('posts.detail', id=post.id))
    
    return render_template('pages/posts/edit.html', form=form, post=post)

@posts_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a post"""
    post = TevkilPost.query.get_or_404(id)
    
    # Check ownership
    if post.user_id != current_user.id:
        abort(403)
    
    # Soft delete - just deactivate
    post.is_active = False
    db.session.commit()
    
    flash('İlan silindi.', 'success')
    return redirect(url_for('posts.my_posts'))

@posts_bp.route('/<int:id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(id):
    """Toggle post active status"""
    post = TevkilPost.query.get_or_404(id)
    
    # Check ownership
    if post.user_id != current_user.id:
        abort(403)
    
    post.is_active = not post.is_active
    db.session.commit()
    
    status = 'aktifleştirildi' if post.is_active else 'pasifleştirildi'
    flash(f'İlan {status}.', 'success')
    return redirect(url_for('posts.my_posts'))
