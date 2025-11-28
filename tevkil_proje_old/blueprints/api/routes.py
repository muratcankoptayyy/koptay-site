#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API Blueprint Routes - Core & Mobile Endpoints
All API routes for external integrations, mobile app, and webhooks
"""

import logging
import os
import re
from datetime import datetime, timezone, timedelta

from flask import jsonify, current_app, abort, request, render_template
from flask_login import login_required, current_user
from flask_mail import Message as MailMessage

from models import db, TevkilPost, User, DeviceToken
from constants import COURTHOUSES
from blueprints.api.helpers import send_push_notification
from tevkil.extensions import limiter

logger = logging.getLogger(__name__)

# Get blueprint from __init__.py
from blueprints.api import api_bp as api


# ============================================
# PUBLIC API ENDPOINTS
# ============================================

@api.route('/posts', methods=['GET'])
def posts():
    """API: İlan listesi"""
    posts = TevkilPost.query.filter_by(
        status='active'
    ).order_by(
        TevkilPost.created_at.desc()
    ).limit(20).all()
    
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'category': p.category,
        'location': p.location,
        'urgency': p.urgency_level,
        'created_at': p.created_at.isoformat()
    } for p in posts])


@api.route('/courthouses/<city>', methods=['GET'])
def courthouses(city):
    """API: Belirli bir şehrin adliyelerini döndür"""
    courthouses_list = COURTHOUSES.get(city, [])
    return jsonify(courthouses_list)


# ============================================
# WHATSAPP BOT ENDPOINTS
# ============================================

@api.route('/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    """
    Merkezi WhatsApp Cloud API Webhook
    Tek numara - Tüm avukatlar için
    """
    if not current_app.config.get('WHATSAPP_ENABLED'):
        abort(404)
    
    from whatsapp_central_bot import central_bot
    from whatsapp_meta_api import MetaWhatsAppAPI
    
    # GET request: Webhook verification (Meta tarafından)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        logger.info(f"🔍 Webhook verification isteği:")
        logger.info(f"  Mode: {mode}")
        logger.info(f"  Token: {token}")
        logger.info(f"  Challenge: {challenge}")
        
        api = MetaWhatsAppAPI()
        verified_challenge = api.verify_webhook(mode, token, challenge)
        
        if verified_challenge:
            logger.info(f"✅ Webhook verified! Challenge: {verified_challenge}")
            # Meta integer challenge bekliyor, string olarak gönder
            return str(verified_challenge), 200
        else:
            logger.error(f"❌ Webhook verification failed!")
            return 'Verification failed', 403
    
    # POST request: Gelen mesajlar
    elif request.method == 'POST':
        try:
            data = request.json
            logger.info(f"\n📱 Gelen mesaj: {data}")
            
            # Meta webhook'tan mesajı parse et
            api = MetaWhatsAppAPI()
            message_data = api.parse_webhook_message(data)
            
            if not message_data:
                logger.warning("⚠ Mesaj parse edilemedi veya status update")
                return jsonify({'status': 'ignored'}), 200
            
            sender_phone = message_data['sender_phone']
            message_text = message_data['message_text']
            message_id = message_data['message_id']
            message_type = message_data.get('type', 'text')
            
            logger.info(f"👤 Gönderen: {sender_phone}")
            logger.info(f"💬 Mesaj: {message_text}")
            logger.info(f"🆔 Message ID: {message_id}")
            logger.info(f"📝 Tip: {message_type}")
            
            # Sesli mesaj veya medya ise bildir ve ignore et
            if message_type != 'text' or message_text is None:
                logger.warning(f"⚠ Text dışı mesaj tipi ({message_type}), cevap gönderiliyor...")
                api.mark_message_as_read(message_id)
                
                # Kullanıcıya bilgi mesajı gönder
                if message_type == 'audio':
                    info_msg = """🎤 Sesli mesaj aldım!

Üzgünüm, şu anda sadece yazılı mesajları işleyebiliyorum.

Lütfen ilanınızı yazarak gönderin:

Örnek:
"Ankara 4. Asliye Ceza Mahkemesinde yarın saat 10:00 duruşma, 2000 TL"

Yardım: #YARDIM"""
                else:
                    info_msg = f"""📎 {message_type.title()} mesajı aldım!

Üzgünüm, şu anda sadece yazılı mesajları işleyebiliyorum.

Lütfen ilanınızı yazarak gönderin.

Yardım: #YARDIM"""
                
                try:
                    api.send_message(sender_phone, info_msg)
                    logger.info(f"✅ Bilgi mesajı gönderildi")
                except:
                    pass
                
                return jsonify({'status': 'ignored', 'reason': f'Non-text message type: {message_type}'}), 200
            
            # ÖNEMLİ: Duplicate mesaj kontrolü
            # Meta bazen aynı mesajı 2 kez gönderebiliyor
            now = datetime.now(timezone.utc)
            
            # Eski message cache'leri temizle (5 dakikadan eski)
            cutoff_time = now - timedelta(minutes=5)
            central_bot.processed_messages = {
                mid: ts for mid, ts in central_bot.processed_messages.items()
                if ts > cutoff_time
            }
            
            # Bu mesaj zaten işlendi mi?
            if message_id in central_bot.processed_messages:
                logger.warning(f"⚠ DUPLICATE MESAJ! Message ID {message_id} zaten işlendi, atlıyorum.")
                return jsonify({'status': 'duplicate', 'message': 'Already processed'}), 200
            
            # Mesajı cache'e ekle
            central_bot.processed_messages[message_id] = now
            
            # Mesajı okundu olarak işaretle
            api.mark_message_as_read(message_id)
            
            # Merkezi Bot'u kullan - TEK NUMARA SİSTEMİ
            result = central_bot.process_message(sender_phone, message_text)
            
            # Kullanıcıya cevap gönder
            if result:
                api.send_message(sender_phone, result['message'])
                logger.info(f"✅ Cevap gönderildi!")
            
            return jsonify({'status': 'success'}), 200
            
        except Exception as e:
            logger.error(f"❌ Webhook error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'status': 'error', 'message': str(e)}), 500


@api.route('/whatsapp/test', methods=['POST'])
@login_required
def whatsapp_test():
    """
    WhatsApp bot test endpoint - Manuel test için
    Merkezi bot sistemini kullanır
    """
    if not current_app.config.get('WHATSAPP_ENABLED'):
        return jsonify({'success': False, 'error': 'WhatsApp özelliği şu anda devre dışı'}), 404
    
    from whatsapp_central_bot import central_bot
    
    message_text = request.form.get('message')
    
    if not current_user.phone:
        return jsonify({
            'success': False,
            'error': 'Telefon numaranız kayıtlı değil. Lütfen profilinizi düzenleyin.'
        }), 400
    
    if not message_text:
        return jsonify({'success': False, 'error': 'Mesaj boş olamaz'}), 400
    
    try:
        # Merkezi Bot'u kullan
        result = central_bot.process_message(current_user.phone, message_text)
        
        if result['success']:
            return jsonify({
                'success': True,
                'response': result['message'],
                'message': 'İşlem başarılı!'
            })
        else:
            return jsonify({
                'success': False,
                'error': result['message']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Hata: {str(e)}'
        }), 500


# ============================================
# MOBILE APP AUTHENTICATION
# ============================================

@api.route('/mobile/login', methods=['POST'])
@limiter.limit("10 per minute")
def mobile_login():
    """Mobile app login - Returns persistent API token"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email ve şifre gerekli'
            }), 400
        
        # Kullanıcıyı bul
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'error': 'Hatalı email veya şifre'
            }), 401
        
        # Hesap aktif mi kontrol et
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'Hesabınız aktif değil'
            }), 403
        
        # API token oluştur (veya mevcut olanı kullan)
        if not user.api_token:
            user.generate_api_token()
            db.session.commit()
        else:
            # Mevcut token'ı güncelle
            user.api_token_last_used = datetime.now(timezone.utc)
            db.session.commit()
        
        # Kullanıcı bilgilerini döndür
        return jsonify({
            'success': True,
            'token': user.api_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'avatar_url': user.avatar_url,
                'city': user.city,
                'lawyer_type': user.lawyer_type,
                'rating_average': user.rating_average,
                'rating_count': user.rating_count,
                'is_admin': user.is_admin
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Mobile login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Giriş işlemi başarısız'
        }), 500


@api.route('/mobile/logout', methods=['POST'])
def mobile_logout():
    """Mobile app logout - Revokes API token"""
    try:
        # Authorization header'dan token al
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Token gerekli'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Token'a sahip kullanıcıyı bul
        user = User.query.filter_by(api_token=token).first()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Geçersiz token'
            }), 401
        
        # Token'ı iptal et
        user.revoke_api_token()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Çıkış başarılı'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Mobile logout error: {e}")
        return jsonify({
            'success': False,
            'error': 'Çıkış işlemi başarısız'
        }), 500


@api.route('/mobile/verify', methods=['POST'])
def mobile_verify():
    """Verify API token and return user info"""
    try:
        # Authorization header'dan token al
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Token gerekli'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Token'a sahip kullanıcıyı bul
        user = User.query.filter_by(api_token=token).first()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Geçersiz token',
                'action': 'login_required'
            }), 401
        
        # Token'ın son kullanım zamanını güncelle
        user.api_token_last_used = datetime.now(timezone.utc)
        db.session.commit()
        
        # Kullanıcı bilgilerini döndür
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'avatar_url': user.avatar_url,
                'city': user.city,
                'lawyer_type': user.lawyer_type,
                'rating_average': user.rating_average,
                'rating_count': user.rating_count,
                'is_admin': user.is_admin,
                'unread_notifications': user.notifications_unread_count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Mobile verify error: {e}")
        return jsonify({
            'success': False,
            'error': 'Token doğrulama başarısız'
        }), 500


# ============================================
# PUSH NOTIFICATIONS (FCM)
# ============================================

@api.route('/notifications/register-device', methods=['POST'])
@login_required
def register_device_token():
    """Register device token for push notifications"""
    try:
        data = request.get_json()
        token = data.get('token')
        platform = data.get('platform', 'android')

        if not token:
            return jsonify({'error': 'Token is required'}), 400

        # Check if token already exists
        existing_token = DeviceToken.query.filter_by(token=token).first()
        
        if existing_token:
            # Update last_used time
            existing_token.last_used = datetime.now(timezone.utc)
            existing_token.user_id = current_user.id  # Update user if changed
        else:
            # Create new token
            new_token = DeviceToken(
                user_id=current_user.id,
                token=token,
                platform=platform
            )
            db.session.add(new_token)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Device registered'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error registering device token: {e}")
        return jsonify({'error': 'Failed to register device'}), 500


@api.route('/notifications/unregister-device', methods=['POST'])
@login_required
def unregister_device_token():
    """Unregister device token (when user logs out)"""
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({'error': 'Token is required'}), 400

        device = DeviceToken.query.filter_by(token=token, user_id=current_user.id).first()
        if device:
            db.session.delete(device)
            db.session.commit()

        return jsonify({'success': True, 'message': 'Device unregistered'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error unregistering device token: {e}")
        return jsonify({'error': 'Failed to unregister device'}), 500


# ============================================
# CONTACT FORM
# ============================================

@api.route('/contact', methods=['POST'])
@limiter.limit("5 per hour")  # Rate limit for contact form
def submit_contact_form():
    """İletişim formu endpoint'i (EmailJS alternatifi)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} alanı gereklidir'
                }), 400
        
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        subject = data.get('subject')
        message = data.get('message')
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({
                'success': False,
                'error': 'Geçersiz e-posta adresi'
            }), 400
        
        # Send email to admin/support
        admin_email = os.getenv('ADMIN_EMAIL', 'destek@utap.com.tr')
        
        try:
            from email_service import mail
            
            msg = MailMessage(
                subject=f'İletişim Formu: {subject}',
                recipients=[admin_email],
                sender=os.getenv('MAIL_DEFAULT_SENDER', 'Tevkil Platform <destek@utap.com.tr>'),
                html=f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                        <h2 style="color: #1f2937; border-bottom: 3px solid #3b82f6; padding-bottom: 10px;">
                            📧 Yeni İletişim Formu Mesajı
                        </h2>
                        
                        <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>📛 İsim:</strong> {name}</p>
                            <p><strong>📧 E-posta:</strong> {email}</p>
                            <p><strong>📞 Telefon:</strong> {phone}</p>
                            <p><strong>📝 Konu:</strong> {subject}</p>
                            
                            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                            
                            <p><strong>💬 Mesaj:</strong></p>
                            <p style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; white-space: pre-wrap;">
                                {message}
                            </p>
                        </div>
                        
                        <div style="text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px;">
                            <p>Bu mesaj Tevkil Platform iletişim formundan gönderildi.</p>
                            <p>📅 {datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M')}</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            )
            
            mail.send(msg)
            logger.info(f"✅ Contact form email sent: {name} <{email}>")
            
            return jsonify({
                'success': True,
                'message': 'Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.'
            }), 200
            
        except Exception as email_error:
            logger.error(f"❌ Error sending contact form email: {email_error}")
            # Don't expose email error to user
            return jsonify({
                'success': True,  # Still return success to user
                'message': 'Mesajınız alındı.'
            }), 200
        
    except Exception as e:
        logger.error(f"❌ Contact form error: {e}")
        return jsonify({
            'success': False,
            'error': 'Mesaj gönderilemedi. Lütfen daha sonra tekrar deneyin.'
        }), 500
