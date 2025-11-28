"""
Applications Routes
Handles application submission, acceptance, and rejection
"""
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from . import applications_bp
from models import db, Application, TevkilPost, Conversation, Notification

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
        cover_letter=cover_letter,
        status='pending'
    )
    
    db.session.add(application)
    
    # Create notification for post owner
    notification = Notification(
        user_id=post.user_id,
        title='Yeni Başvuru',
        message=f'{current_user.get_full_name()} ilanınıza başvurdu.',
        type='application',
        related_id=application.id
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
    
    # Update application status
    application.status = 'accepted'
    application.responded_at = datetime.utcnow()
    
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
        message=f'{current_user.get_full_name()} başvurunuzu kabul etti.',
        type='application_accepted',
        related_id=application.id
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
        message=f'{current_user.get_full_name()} başvurunuzu reddetti.',
        type='application_rejected',
        related_id=application.id
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
