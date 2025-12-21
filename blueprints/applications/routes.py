"""
Applications Routes
Handles application submission, acceptance, and rejection
"""
from flask import render_template, redirect, url_for, flash, request, abort, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime
from . import applications_bp
from models import db, Application, TevkilPost, Conversation, Notification
from utils.udf_service import create_authorization_udf

@applications_bp.route('/')
@login_required
def list():
    """List all applications (sent and received)"""
    # Get applications sent by current user
    sent = Application.query.filter_by(applicant_id=current_user.id)\
        .order_by(Application.created_at.desc()).all()
    
    # Get applications received by current user
    received_query = db.session.query(Application)\
        .join(TevkilPost, Application.post_id == TevkilPost.id)\
        .filter(TevkilPost.user_id == current_user.id)\
        .order_by(Application.created_at.desc())
    
    received = received_query.all()
    
    return render_template('pages/applications/list.html', 
                         sent_applications=sent, 
                         received_applications=received)

@applications_bp.route('/send/<int:post_id>', methods=['POST'])
@login_required
def send(post_id):
    """Send an application to a post"""
    post = TevkilPost.query.get_or_404(post_id)
    
    # Check if post is active
    if not post.is_active:
        flash('Bu ilan artık aktif değil.', 'warning')
        return redirect(url_for('posts.detail', id=post_id))
    
    # Check if user is the post owner
    if post.user_id == current_user.id:
        flash('Kendi ilanınıza başvuramazsınız.', 'warning')
        return redirect(url_for('posts.detail', id=post_id))
    
    # Check if already applied
    existing = Application.query.filter_by(
        post_id=post_id,
        applicant_id=current_user.id
    ).first()
    
    if existing:
        flash('Bu ilana zaten başvurdunuz.', 'warning')
        return redirect(url_for('posts.detail', id=post_id))
    
    # Get cover letter from form
    cover_letter = request.form.get('cover_letter', '')
    
    # Create application
    application = Application(
        post_id=post_id,
        applicant_id=current_user.id,
        message=cover_letter,
        status='pending'
    )
    
    db.session.add(application)
    
    # Create notification for post owner
    notification = Notification(
        user_id=post.user_id,
        title='Yeni Başvuru',
        message=f'{current_user.full_name} ilanınıza başvurdu.',
        type='application',
        related_post_id=post.id,
        related_user_id=current_user.id,
        action_url=url_for('applications.list')
    )
    
    db.session.add(notification)
    db.session.commit()
    
    flash('Başvurunuz gönderildi!', 'success')
    return redirect(url_for('posts.detail', id=post_id))

@applications_bp.route('/<int:id>/accept', methods=['POST'])
@login_required
def accept(id):
    """Accept an application"""
    application = Application.query.get_or_404(id)
    
    # Check if current user is the post owner
    if application.post.user_id != current_user.id:
        abort(403)
    
    # Check if any other application for this post is already accepted
    accepted_application = Application.query.filter_by(
        post_id=application.post_id,
        status='accepted'
    ).first()

    if accepted_application:
        flash('Bu ilan için zaten bir başvuru kabul edilmiş. Yeni bir görevlendirme yapmadan önce mevcut görevlendirmeyi iptal etmelisiniz.', 'warning')
        return redirect(url_for('applications.list'))
    
    # Update application status
    application.status = 'accepted'
    application.responded_at = datetime.utcnow()
    
    # Update post status to assigned (hides it from active lists)
    application.post.status = 'assigned'
    application.post.assigned_to = application.applicant_id
    
    # Create or get conversation
    conversation = Conversation.query.filter(
        ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == application.applicant_id)) |
        ((Conversation.user1_id == application.applicant_id) & (Conversation.user2_id == current_user.id))
    ).first()
    
    if not conversation:
        conversation = Conversation(
            user1_id=current_user.id,
            user2_id=application.applicant_id,
            post_id=application.post_id
        )
        db.session.add(conversation)
    
    # Create notification for applicant
    notification = Notification(
        user_id=application.applicant_id,
        title='Başvuru Kabul Edildi',
        message=f'{current_user.full_name} başvurunuzu kabul etti.',
        type='application_accepted',
        related_post_id=application.post_id,
        related_user_id=current_user.id,
        action_url=url_for('applications.list')
    )
    
    db.session.add(notification)
    db.session.commit()
    
    flash('Başvuru kabul edildi. Mesajlaşmayı başlatabilirsiniz.', 'success')
    return redirect(url_for('applications.list'))

@applications_bp.route('/<int:id>/reject', methods=['POST'])
@login_required
def reject(id):
    """Reject an application"""
    application = Application.query.get_or_404(id)
    
    # Check if current user is the post owner
    if application.post.user_id != current_user.id:
        abort(403)
    
    # Update application status
    application.status = 'rejected'
    application.responded_at = datetime.utcnow()
    
    # Create notification for applicant
    notification = Notification(
        user_id=application.applicant_id,
        title='Başvuru Reddedildi',
        message=f'{current_user.full_name} başvurunuzu reddetti.',
        type='application_rejected',
        related_post_id=application.post_id,
        related_user_id=current_user.id,
        action_url=url_for('applications.list')
    )
    
    db.session.add(notification)
    db.session.commit()
    
    flash('Başvuru reddedildi.', 'info')
    return redirect(url_for('applications.list'))

@applications_bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    """Cancel an application (by applicant)"""
    application = Application.query.get_or_404(id)
    
    # Check if current user is the applicant
    if application.applicant_id != current_user.id:
        abort(403)
    
    # Can only cancel pending applications
    if application.status != 'pending':
        flash('Sadece beklemedeki başvurular iptal edilebilir.', 'warning')
        return redirect(url_for('applications.list'))
    
    # Delete application
    db.session.delete(application)
    db.session.commit()
    
    flash('Başvurunuz iptal edildi.', 'info')
    return redirect(url_for('applications.list'))

@applications_bp.route('/<int:id>/download-udf')
@login_required
def download_udf(id):
    """Download authorization document (UDF)"""
    application = Application.query.get_or_404(id)
    
    # Check permissions (only post owner or applicant can download)
    if application.post.user_id != current_user.id and application.applicant_id != current_user.id:
        abort(403)
        
    # Check if application is accepted
    if application.status != 'accepted':
        flash('Yetki belgesi sadece kabul edilmiş başvurular için oluşturulabilir.', 'warning')
        return redirect(url_for('applications.list'))
        
    # Prepare data
    post_owner = {
        'name': application.post.user.full_name,
        'baro': application.post.user.bar_association or 'Belirtilmemiş',
        'tc_number': application.post.user.tc_number or '',
        'sicil': application.post.user.bar_registration_number or 'Belirtilmemiş',
        'tax_office': '',
        'tax_number': '',
        'address': application.post.user.address or 'Belirtilmemiş'
    }
    
    applicant_data = {
        'name': application.applicant.full_name,
        'baro': application.applicant.bar_association or 'Belirtilmemiş',
        'tc_number': application.applicant.tc_number or '',
        'sicil': application.applicant.bar_registration_number or 'Belirtilmemiş',
        'tax_office': '',
        'tax_number': '',
        'address': application.applicant.address or 'Belirtilmemiş'
    }
    
    post_data = {
        'title': application.post.title,
        'category': application.post.category,
        'description': application.post.description,
        'client_name': '', # İlan detaylarında varsa eklenebilir
        'client_address': '',
        'vekaletname_info': ''
    }
    
    application_info = {
        'created_at': application.created_at.strftime('%d.%m.%Y %H:%M'),
        'accepted_at': application.updated_at.strftime('%d.%m.%Y %H:%M')
    }
    
    # Generate UDF
    try:
        udf_buffer = create_authorization_udf(
            post_owner=post_owner,
            applicant=applicant_data,
            post=post_data,
            application=application_info,
            price=application.proposed_price or 0
        )
        
        filename = f"yetki_belgesi_{application.post.user.first_name}_{application.applicant.first_name}.udf"
        
        return send_file(
            udf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip' # UDF is technically a ZIP
        )
        
    except Exception as e:
        print(f"UDF generation error: {e}")
        flash('Belge oluşturulurken bir hata oluştu.', 'error')
        return redirect(url_for('applications.list'))
