from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from . import office_bp
from .forms import OfficePostForm
from models import db, OfficePost, OfficePostImage
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, timezone

@office_bp.route('/')
def index():
    """Ofis ilanlarını listele"""
    category = request.args.get('category')
    query = OfficePost.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
        
    posts = query.order_by(OfficePost.created_at.desc()).all()
    return render_template('pages/office/list.html', posts=posts, category=category)

@office_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Yeni ofis ilanı oluştur"""
    form = OfficePostForm()
    if form.validate_on_submit():
        post = OfficePost(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            price=form.price.data,
            currency=form.currency.data,
            city=form.city.data,
            district=form.district.data,
            address=form.address.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            square_meters=form.square_meters.data,
            room_count=form.room_count.data,
            floor=form.floor.data,
            heating_type=form.heating_type.data,
            is_furnished=form.is_furnished.data
        )
        db.session.add(post)
        db.session.commit()
        
        # Resim yükleme işlemi
        if form.images.data:
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'office_images')
            os.makedirs(upload_folder, exist_ok=True)
            
            for file in form.images.data:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    # Benzersiz dosya adı oluştur
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file_path = os.path.join(upload_folder, unique_filename)
                    file.save(file_path)
                    
                    # Veritabanına kaydet
                    image = OfficePostImage(
                        post_id=post.id,
                        image_url=f"/static/uploads/office_images/{unique_filename}"
                    )
                    db.session.add(image)
            
            db.session.commit()
            
        flash('İlanınız başarıyla oluşturuldu.', 'success')
        return redirect(url_for('office.index'))
        
    return render_template('pages/office/create.html', form=form)

@office_bp.route('/<int:id>')
def detail(id):
    """İlan detayı"""
    post = OfficePost.query.get_or_404(id)
    return render_template('pages/office/detail.html', post=post)

@office_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Ofis ilanını düzenle"""
    post = OfficePost.query.get_or_404(id)
    
    # Yetki kontrolü
    if post.user_id != current_user.id:
        abort(403)
        
    form = OfficePostForm(obj=post)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.description = form.description.data
        post.category = form.category.data
        post.price = form.price.data
        post.currency = form.currency.data
        post.city = form.city.data
        post.district = form.district.data
        post.address = form.address.data
        post.latitude = form.latitude.data
        post.longitude = form.longitude.data
        post.square_meters = form.square_meters.data
        post.room_count = form.room_count.data
        post.floor = form.floor.data
        post.heating_type = form.heating_type.data
        post.is_furnished = form.is_furnished.data
        
        post.updated_at = datetime.now(timezone.utc)
        
        # Yeni resim ekleme
        if form.images.data:
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'office_images')
            os.makedirs(upload_folder, exist_ok=True)
            
            for file in form.images.data:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file_path = os.path.join(upload_folder, unique_filename)
                    file.save(file_path)
                    
                    image = OfficePostImage(
                        post_id=post.id,
                        image_url=f"/static/uploads/office_images/{unique_filename}"
                    )
                    db.session.add(image)
        
        db.session.commit()
        flash('İlan başarıyla güncellendi.', 'success')
        return redirect(url_for('office.detail', id=post.id))
        
    return render_template('pages/office/edit.html', form=form, post=post)

@office_bp.route('/my-posts')
@login_required
def my_posts():
    """İlanlarım"""
    posts = OfficePost.query.filter_by(user_id=current_user.id).order_by(OfficePost.created_at.desc()).all()
    return render_template('pages/office/my_posts.html', posts=posts)
