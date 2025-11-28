"""Applications Blueprint Routes

Başvuru yönetimi route'ları:
- Gelen/gönderilen başvurular
- Kabul/Red işlemleri  
- Yetki belgesi oluşturma
"""

import logging
from datetime import datetime, timedelta, timezone
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user

from models import db, TevkilPost, Application
from blueprints.decorators import dev_login_optional
from blueprints.helpers import create_notification
from . import applications_bp

logger = logging.getLogger(__name__)


@applications_bp.route('/received')
@dev_login_optional  
def received():
    """Gelen başvurular"""
    logger.info(f"Received applications for user {current_user.id}")
    # TODO: Full implementation from app.py line 614
    return render_template('phoenix/applications/received.html', applications=[])


@applications_bp.route('/sent')
@dev_login_optional
def sent():
    """Gönderilen başvurular"""
    logger.info(f"Sent applications for user {current_user.id}")
    # TODO: Full implementation from app.py line 801
    return render_template('phoenix/applications/sent.html', applications=[])


@applications_bp.route('/<int:app_id>/accept', methods=['POST'])
@login_required
def accept_application(app_id):
    """Başvuruyu kabul et"""
    application = Application.query.get_or_404(app_id)
    post = application.post
    
    if post.user_id != current_user.id:
        return jsonify({'error': 'Yetkiniz yok'}), 403
    
    # Duplicate check
    existing = Application.query.filter_by(post_id=post.id, status='accepted').first()
    if existing:
        flash('Bu ilana zaten bir başvuru kabul edilmiş', 'error')
        return redirect(url_for('posts.post_detail', post_id=post.id))
    
    application.status = 'accepted'
    post.status = 'assigned'
    post.assigned_to = application.applicant_id
    
    create_notification(
        user_id=application.applicant_id,
        notification_type='application_accepted',
        title='Başvurunuz Kabul Edildi!',
        message=f'"{post.title}" ilanına başvurunuz kabul edildi.',
        related_post_id=post.id,
        related_user_id=current_user.id
    )
    
    db.session.commit()
    flash('Başvuru kabul edildi!', 'success')
    return redirect(url_for('posts.post_detail', post_id=post.id))


@applications_bp.route('/<int:app_id>/reject', methods=['POST'])
@login_required
def reject_application(app_id):
    """Başvuruyu reddet"""
    application = Application.query.get_or_404(app_id)
    post = application.post
    
    if post.user_id != current_user.id:
        return jsonify({'error': 'Yetkiniz yok'}), 403
    
    application.status = 'rejected'
    
    create_notification(
        user_id=application.applicant_id,
        notification_type='application_rejected',
        title='Başvurunuz Değerlendirildi',
        message=f'"{post.title}" ilanına başvurunuz kabul edilmedi.',
        related_post_id=post.id,
        related_user_id=current_user.id
    )
    
    db.session.commit()
    flash('Başvuru reddedildi', 'info')
    return redirect(url_for('posts.post_detail', post_id=post.id))


@applications_bp.route('/<int:app_id>/authorization-info')
@login_required
def authorization_info(app_id):
    """Yetkilendirme bilgilerini getir (JSON)"""
    application = Application.query.get_or_404(app_id)
    post = application.post
    
    if post.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Yetkiniz yok'}), 403
    
    if application.status != 'accepted':
        return jsonify({'success': False, 'error': 'Bu başvuru kabul edilmemiş'}), 400
    
    return jsonify({
        'success': True,
        'data': {
            'post_owner': {
                'full_name': post.user.masked_full_name,
                'bar_association': post.user.bar_association,
                'tc_number': post.user.tc_number,
            },
            'applicant': {
                'full_name': application.applicant.masked_full_name,
                'bar_association': application.applicant.bar_association,
                'tc_number': application.applicant.tc_number,
            }
        }
    })


@applications_bp.route('/<int:app_id>/generate-authorization-pdf')
@login_required
def generate_authorization_pdf(app_id):
    """Yetki belgesi UDF oluştur"""
    application = Application.query.get_or_404(app_id)
    post = application.post
    
    if post.user_id != current_user.id:
        flash('Bu belgeyi indirme yetkiniz yok', 'error')
        return redirect(url_for('posts.post_detail', post_id=post.id))
    
    if application.status != 'accepted':
        flash('Bu başvuru kabul edilmemiş', 'error')
        return redirect(url_for('posts.post_detail', post_id=post.id))
    
    from udf_service_dynamic import create_authorization_udf_dynamic
    
    post_owner = {
        'name': post.user.masked_full_name,
        'baro': post.user.bar_association or 'Belirtilmemiş',
        'tc_number': post.user.tc_number or '',
        'sicil': post.user.bar_registration_number or 'Belirtilmemiş',
    }
    
    applicant_data = {
        'name': application.applicant.masked_full_name,
        'baro': application.applicant.bar_association or 'Belirtilmemiş',
        'tc_number': application.applicant.tc_number or '',
        'sicil': application.applicant.bar_registration_number or 'Belirtilmemiş',
    }
    
    post_data = {
        'title': post.title,
        'category': post.category,
        'location': post.location,
    }
    
    application_info = {
        'created_at': application.created_at.strftime('%d.%m.%Y %H:%M') if application.created_at else '',
        'accepted_at': application.updated_at.strftime('%d.%m.%Y %H:%M') if application.updated_at else '',
    }
    
    udf_buffer = create_authorization_udf_dynamic(
        post_owner=post_owner,
        applicant=applicant_data,
        post=post_data,
        application=application_info,
        price=application.proposed_price or 0
    )
    
    filename = f"yetki_belgesi_{datetime.now().strftime('%Y%m%d')}.udf"
    
    return send_file(
        udf_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )
