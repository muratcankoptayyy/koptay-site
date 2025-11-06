"""
E-posta Bildirimleri Servisi
Flask-Mail kullanarak kullanıcılara e-posta gönderir
"""
from flask import render_template
from flask_mail import Mail, Message
import os

mail = Mail()

def init_mail(app):
    """Flask-Mail'i başlat"""
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'Tevkil Platform <destek@utap.com.tr>')
    
    mail.init_app(app)
    return mail

def send_email(to, subject, template, **kwargs):
    """
    E-posta gönder
    
    Args:
        to: Alıcı e-posta adresi
        subject: E-posta konusu
        template: HTML template dosya adı (emails/ klasöründe)
        **kwargs: Template'e geçilecek parametreler
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            html=render_template(f'emails/{template}.html', **kwargs),
            sender=os.getenv('MAIL_DEFAULT_SENDER', 'Tevkil Platform <destek@utap.com.tr>')
        )
        mail.send(msg)
        print(f"✅ E-posta gönderildi: {to} - {subject}")
        return True
    except Exception as e:
        print(f"❌ E-posta gönderilemedi: {str(e)}")
        return False

def send_welcome_email(user):
    """Hoş geldiniz e-postası"""
    return send_email(
        to=user.email,
        subject='Tevkil Platformuna Hoş Geldiniz! 🎉',
        template='welcome',
        user=user
    )

def send_application_received_email(post_owner, application):
    """Yeni başvuru bildirimi (ilan sahibine)"""
    return send_email(
        to=post_owner.email,
        subject=f'Yeni Başvuru Alındı - {application.post.title}',
        template='application_received',
        owner=post_owner,
        application=application
    )

def send_application_accepted_email(applicant, application):
    """Başvuru kabul edildi bildirimi"""
    return send_email(
        to=applicant.email,
        subject=f'🎉 Başvurunuz Kabul Edildi - {application.post.title}',
        template='application_accepted',
        applicant=applicant,
        application=application
    )

def send_application_rejected_email(applicant, application):
    """Başvuru reddedildi bildirimi"""
    return send_email(
        to=applicant.email,
        subject=f'Başvuru Durumu - {application.post.title}',
        template='application_rejected',
        applicant=applicant,
        application=application
    )

def send_new_message_email(recipient, sender, message):
    """Yeni mesaj bildirimi"""
    return send_email(
        to=recipient.email,
        subject=f'💬 Yeni Mesaj - {sender.full_name}',
        template='new_message',
        recipient=recipient,
        sender=sender,
        message=message
    )

def send_rating_received_email(rated_user, reviewer, rating):
    """Yeni değerlendirme bildirimi"""
    return send_email(
        to=rated_user.email,
        subject=f'⭐ Yeni Değerlendirme Aldınız - {reviewer.full_name}',
        template='rating_received',
        rated_user=rated_user,
        reviewer=reviewer,
        rating=rating
    )

def send_post_expiring_email(user, post, days_left):
    """İlan sona eriyor bildirimi"""
    return send_email(
        to=user.email,
        subject=f'⚠️ İlanınız Sona Eriyor - {post.title}',
        template='post_expiring',
        user=user,
        post=post,
        days_left=days_left
    )

def send_password_reset_email(user, reset_token):
    """Şifre sıfırlama e-postası"""
    return send_email(
        to=user.email,
        subject='Şifre Sıfırlama - Tevkil Platform',
        template='password_reset',
        user=user,
        reset_token=reset_token
    )
