"""
API Routes - Mobile Application REST API
"""
from flask import request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
from models import db, User, TevkilPost, Application, Conversation, Message, Notification, PostImage, JobPost, OfficePost, OfficePostImage
from . import api_bp
from functools import wraps
import os
from werkzeug.utils import secure_filename
from flask import current_app
from constants import COURTHOUSES


def token_required(f):
    """API Token ile kimlik doğrulama decorator'ı"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Token gerekli'
            }), 401
        
        token = auth_header.split(' ')[1]
        user = User.query.filter_by(api_token=token).first()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Geçersiz token'
            }), 401
        
        # Token son kullanım zamanını güncelle (Opsiyonel - Performans için kapalı tutulabilir)
        # user.api_token_last_used = datetime.now(timezone.utc)
        # user.last_active = datetime.now(timezone.utc)
        # db.session.commit()
        
        # current_user benzeri bir nesne ekle
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


def allowed_file(filename):
    """Dosya uzantısı kontrolü"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@api_bp.route('/courthouses/<city>', methods=['GET'])
def get_courthouses(city):
    """Şehre göre adliyeleri getir"""
    courthouses = COURTHOUSES.get(city, [])
    return jsonify(courthouses)


# =============================================================================
# AUTHENTICATION - Mobile Login/Logout
# =============================================================================

@api_bp.route('/mobile/login', methods=['POST'])
def mobile_login():
    """
    Mobil uygulama girişi - Kalıcı API token döner
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    
    Response:
    {
        "success": true,
        "token": "api_token_here",
        "user": {...}
    }
    """
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
        else:
            user.api_token_last_used = datetime.now(timezone.utc)
        
        user.last_active = datetime.now(timezone.utc)
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
                'bar_association': user.bar_association,
                'bar_registration_number': user.bar_registration_number,
                'rating_average': user.rating_average,
                'rating_count': user.rating_count,
                'is_admin': user.is_admin,
                'is_verified': user.is_verified
            }
        }), 200
        
    except Exception as e:
        print(f"Mobile login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Giriş işlemi başarısız'
        }), 500


@api_bp.route('/mobile/register', methods=['POST'])
def mobile_register():
    """
    Mobil uygulama kayıt - Yeni kullanıcı oluşturur ve token döner
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "password123",
        "full_name": "Ad Soyad",
        "phone": "5551234567",
        "city": "İstanbul",
        "bar_association": "İstanbul Barosu",
        "bar_registration_number": "12345"
    }
    """
    try:
        data = request.get_json()
        
        # Zorunlu alanlar
        required_fields = ['email', 'password', 'full_name', 'phone', 'city']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} alanı zorunludur'
                }), 400
        
        # Email kontrolü
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'error': 'Bu email adresi zaten kullanımda'
            }), 400
            
        # Yeni kullanıcı oluştur
        user = User(
            email=data['email'],
            full_name=data['full_name'],
            phone=data['phone'],
            city=data['city'],
            bar_association=data.get('bar_association'),
            bar_registration_number=data.get('bar_registration_number'),
            lawyer_type=data.get('lawyer_type', 'lawyer')
        )
        user.set_password(data['password'])
        user.generate_api_token()
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'token': user.api_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'city': user.city,
                'lawyer_type': user.lawyer_type,
                'is_verified': user.is_verified
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Mobile register error: {e}")
        return jsonify({
            'success': False,
            'error': 'Kayıt işlemi başarısız'
        }), 500


@api_bp.route('/mobile/forgot-password', methods=['POST'])
def mobile_forgot_password():
    """
    Şifre sıfırlama isteği
    
    Request Body:
    {
        "email": "user@example.com"
    }
    """
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email adresi gerekli'
            }), 400
            
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Güvenlik için kullanıcı bulunamadı dememek daha iyi olabilir
            # ama geliştirme aşamasında kolaylık olsun diye dönüyoruz
            return jsonify({
                'success': False,
                'error': 'Bu email adresi ile kayıtlı kullanıcı bulunamadı'
            }), 404
            
        # TODO: Gerçek email gönderme işlemi
        # Şimdilik sadece logluyoruz
        print(f"Password reset requested for: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Şifre sıfırlama bağlantısı email adresinize gönderildi'
        }), 200
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        return jsonify({
            'success': False,
            'error': 'İşlem başarısız'
        }), 500


@api_bp.route('/mobile/logout', methods=['POST'])
@token_required
def mobile_logout():
    """
    Mobil uygulama çıkışı - Token'ı iptal eder
    
    Headers:
    Authorization: Bearer <token>
    """
    try:
        user = request.current_user
        user.revoke_api_token()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Çıkış başarılı'
        }), 200
        
    except Exception as e:
        print(f"Mobile logout error: {e}")
        return jsonify({
            'success': False,
            'error': 'Çıkış işlemi başarısız'
        }), 500


@api_bp.route('/mobile/verify', methods=['POST'])
@token_required
def mobile_verify():
    """
    Token doğrulama - Token geçerli mi kontrol eder
    
    Headers:
    Authorization: Bearer <token>
    """
    user = request.current_user
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name
        }
    }), 200


# =============================================================================
# POSTS - İlan İşlemleri
# =============================================================================

@api_bp.route('/posts', methods=['GET'])
@token_required
def get_posts():
    """
    İlanları listele (filtreli)
    
    Query Params:
    - category: Kategori filtresi
    - city: Şehir filtresi
    - status: Durum filtresi (active, assigned, completed)
    - page: Sayfa numarası (default: 1)
    - per_page: Sayfa başına kayıt (default: 20)
    """
    try:
        # Filtreler
        category = request.args.get('category')
        city = request.args.get('city')
        status = request.args.get('status', 'active')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Default to user's city if not specified
        if city is None and request.current_user.city:
            city = request.current_user.city
        
        # Query oluştur
        query = TevkilPost.query
        
        if category:
            query = query.filter_by(category=category)
        if city:
            query = query.filter_by(city=city)
        if status:
            query = query.filter_by(status=status)
        
        # Sayfalama
        pagination = query.order_by(TevkilPost.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        posts = []
        for post in pagination.items:
            # İlk resmi al (thumbnail olarak)
            thumbnail = None
            # lazy='dynamic' olduğu için query object döner
            first_image = post.images.first()
            if first_image:
                thumbnail = first_image.image_url

            posts.append({
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'category': post.category,
                'city': post.city,
                'district': post.district,
                'courthouse': post.courthouse,
                'urgency_level': post.urgency_level,
                'remote_allowed': post.remote_allowed,
                'price_min': post.price_min,
                'price_max': post.price_max,
                'court_date': post.court_date.isoformat() if post.court_date else None,
                'deadline': post.deadline.isoformat() if post.deadline else None,
                'status': post.status,
                'views': post.views,
                'applications_count': post.applications_count,
                'created_at': post.created_at.isoformat(),
                'thumbnail': thumbnail,
                'user': {
                    'id': post.user.id,
                    'full_name': post.user.masked_full_name,
                    'city': post.user.city,
                    'rating_average': post.user.rating_average
                }
            })
        
        return jsonify({
            'success': True,
            'posts': posts,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        print(f"Get posts error: {e}")
        return jsonify({
            'success': False,
            'error': f'İlanlar yüklenemedi: {str(e)}'
        }), 500


@api_bp.route('/posts/<int:post_id>', methods=['GET'])
@token_required
def get_post_detail(post_id):
    """İlan detayını getir"""
    try:
        post = TevkilPost.query.get_or_404(post_id)
        
        # Görüntülenme sayısını artır
        post.views += 1
        db.session.commit()
        
        # Resimleri hazırla
        images = []
        for img in post.images:
            images.append({
                'id': img.id,
                'url': img.image_url,
                'created_at': img.created_at.isoformat()
            })

        return jsonify({
            'success': True,
            'post': {
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'category': post.category,
                'city': post.city,
                'district': post.district,
                'courthouse': post.courthouse,
                'urgency_level': post.urgency_level,
                'remote_allowed': post.remote_allowed,
                'price_min': post.price_min,
                'price_max': post.price_max,
                'court_date': post.court_date.isoformat() if post.court_date else None,
                'deadline': post.deadline.isoformat() if post.deadline else None,
                'status': post.status,
                'views': post.views,
                'applications_count': post.applications_count,
                'created_at': post.created_at.isoformat(),
                'images': images,
                'user': {
                    'id': post.user.id,
                    'full_name': post.user.masked_full_name,
                    'city': post.user.city,
                    'bar_association': post.user.bar_association,
                    'rating_average': post.user.rating_average,
                    'rating_count': post.user.rating_count
                }
            }
        }), 200
        
    except Exception as e:
        print(f"Get post detail error: {e}")
        return jsonify({
            'success': False,
            'error': 'İlan detayı yüklenemedi'
        }), 500


@api_bp.route('/posts', methods=['POST'])
@token_required
def create_post():
    """Yeni ilan oluştur"""
    try:
        user = request.current_user
        data = request.get_json()
        
        # Zorunlu alanlar
        required_fields = ['title', 'description', 'category', 'city']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} alanı zorunludur'
                }), 400
        
        # Yeni ilan oluştur
        post = TevkilPost(
            user_id=user.id,
            title=data['title'],
            description=data['description'],
            category=data['category'],
            city=data['city'],
            district=data.get('district'),
            courthouse=data.get('courthouse'),
            urgency_level=data.get('urgency_level', 'normal'),
            remote_allowed=data.get('remote_allowed', False),
            price_min=data.get('price_min'),
            price_max=data.get('price_max'),
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
            court_date=datetime.fromisoformat(data['court_date']) if data.get('court_date') else None
        )
        
        db.session.add(post)
        user.total_posts_created += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'İlan başarıyla oluşturuldu',
            'post_id': post.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Create post error: {e}")
        return jsonify({
            'success': False,
            'error': 'İlan oluşturulamadı'
        }), 500


# =============================================================================
# APPLICATIONS - Başvuru İşlemleri
# =============================================================================

@api_bp.route('/applications/my', methods=['GET'])
@token_required
def get_my_applications():
    """Kullanıcının başvurularını listele (gönderilen ve alınan)"""
    try:
        user = request.current_user
        app_type = request.args.get('type', 'sent')  # sent or received
        
        if app_type == 'sent':
            # Gönderilen başvurular
            applications = Application.query.filter_by(applicant_id=user.id)\
                .order_by(Application.created_at.desc()).all()
        else:
            # Alınan başvurular
            applications = db.session.query(Application)\
                .join(TevkilPost, Application.post_id == TevkilPost.id)\
                .filter(TevkilPost.user_id == user.id)\
                .order_by(Application.created_at.desc())\
                .all()
        
        apps_data = []
        for app in applications:
            apps_data.append({
                'id': app.id,
                'post': {
                    'id': app.post.id,
                    'title': app.post.title,
                    'category': app.post.category,
                    'city': app.post.city,
                    'owner': {
                        'id': app.post.user.id,
                        'full_name': app.post.user.masked_full_name,
                        'city': app.post.user.city,
                        'rating_average': app.post.user.rating_average
                    }
                },
                'applicant': {
                    'id': app.applicant.id,
                    'full_name': app.applicant.masked_full_name,
                    'city': app.applicant.city,
                    'rating_average': app.applicant.rating_average
                },
                'message': app.message,
                'proposed_price': app.proposed_price,
                'status': app.status,
                'created_at': app.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'applications': apps_data
        }), 200
        
    except Exception as e:
        print(f"Get applications error: {e}")
        return jsonify({
            'success': False,
            'error': 'Başvurular yüklenemedi'
        }), 500


@api_bp.route('/applications/<int:post_id>', methods=['POST'])
@token_required
def apply_to_post(post_id):
    """İlana başvur"""
    try:
        user = request.current_user
        data = request.get_json()
        
        post = TevkilPost.query.get_or_404(post_id)
        
        # Kendi ilanına başvuru kontrolü
        if post.user_id == user.id:
            return jsonify({
                'success': False,
                'error': 'Kendi ilanınıza başvuramazsınız'
            }), 400
        
        # Daha önce başvuru kontrolü
        existing = Application.query.filter_by(
            post_id=post_id,
            applicant_id=user.id
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': 'Bu ilana zaten başvurdunuz'
            }), 400
        
        # Başvuru oluştur
        application = Application(
            post_id=post_id,
            applicant_id=user.id,
            message=data.get('message', ''),
            proposed_price=data.get('proposed_price')
        )
        
        db.session.add(application)
        post.applications_count += 1
        user.total_applications_sent += 1
        db.session.commit()
        
        # Bildirim oluştur
        notification = Notification(
            user_id=post.user_id,
            type='new_application',
            title='Yeni Başvuru',
            message=f'{user.masked_full_name} ilanınıza başvurdu',
            related_post_id=post_id,
            related_user_id=user.id,
            action_url=f'/applications/{application.id}'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Başvurunuz gönderildi',
            'application_id': application.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Apply error: {e}")
        return jsonify({
            'success': False,
            'error': 'Başvuru gönderilemedi'
        }), 500


@api_bp.route('/applications/<int:app_id>/accept', methods=['POST'])
@token_required
def accept_application(app_id):
    """Başvuruyu kabul et"""
    try:
        user = request.current_user
        application = Application.query.get_or_404(app_id)
        
        # İlan sahibi kontrolü
        if application.post.user_id != user.id:
            return jsonify({
                'success': False,
                'error': 'Bu işlem için yetkiniz yok'
            }), 403
            
        # Zaten işlem yapılmış mı?
        if application.status != 'pending':
            return jsonify({
                'success': False,
                'error': 'Bu başvuru zaten sonuçlandırılmış'
            }), 400
        
        # Check if any other application for this post is already accepted
        accepted_application = Application.query.filter_by(
            post_id=application.post_id,
            status='accepted'
        ).first()

        if accepted_application:
            return jsonify({
                'success': False,
                'error': 'Bu ilan için zaten bir başvuru kabul edilmiş. Yeni bir görevlendirme yapmadan önce mevcut görevlendirmeyi iptal etmelisiniz.'
            }), 400
        
        # Durumu güncelle
        application.status = 'accepted'
        application.responded_at = datetime.now(timezone.utc)
        
        # Update post status to assigned (hides it from active lists)
        application.post.status = 'assigned'
        application.post.assigned_to = application.applicant_id
        
        # Konuşma başlat/bul
        conversation = Conversation.query.filter(
            ((Conversation.user1_id == user.id) & (Conversation.user2_id == application.applicant_id)) |
            ((Conversation.user1_id == application.applicant_id) & (Conversation.user2_id == user.id))
        ).first()
        
        if not conversation:
            conversation = Conversation(
                user1_id=user.id,
                user2_id=application.applicant_id,
                post_id=application.post_id
            )
            db.session.add(conversation)
        
        # Bildirim oluştur
        notification = Notification(
            user_id=application.applicant_id,
            type='application_accepted',
            title='Başvuru Kabul Edildi',
            message=f'{user.masked_full_name} başvurunuzu kabul etti.',
            related_post_id=application.post_id,
            related_user_id=user.id,
            action_url=f'/applications/{application.id}'
        )
        db.session.add(notification)
        
        # İstatistikleri güncelle
        user.accepted_applications += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Başvuru kabul edildi'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Accept application error: {e}")
        return jsonify({
            'success': False,
            'error': 'İşlem başarısız'
        }), 500


@api_bp.route('/applications/<int:app_id>/reject', methods=['POST'])
@token_required
def reject_application(app_id):
    """Başvuruyu reddet"""
    try:
        user = request.current_user
        application = Application.query.get_or_404(app_id)
        
        # İlan sahibi kontrolü
        if application.post.user_id != user.id:
            return jsonify({
                'success': False,
                'error': 'Bu işlem için yetkiniz yok'
            }), 403
            
        # Zaten işlem yapılmış mı?
        if application.status != 'pending':
            return jsonify({
                'success': False,
                'error': 'Bu başvuru zaten sonuçlandırılmış'
            }), 400
        
        # Durumu güncelle
        application.status = 'rejected'
        application.responded_at = datetime.now(timezone.utc)
        
        # Bildirim oluştur
        notification = Notification(
            user_id=application.applicant_id,
            type='application_rejected',
            title='Başvuru Reddedildi',
            message=f'{user.masked_full_name} başvurunuzu reddetti.',
            related_post_id=application.post_id,
            related_user_id=user.id,
            action_url=f'/applications/{application.id}'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Başvuru reddedildi'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Reject application error: {e}")
        return jsonify({
            'success': False,
            'error': 'İşlem başarısız'
        }), 500


# =============================================================================
# MESSAGES - Mesajlaşma
# =============================================================================

@api_bp.route('/conversations', methods=['GET'])
@token_required
def get_conversations():
    """Kullanıcının konuşmalarını listele"""
    try:
        user = request.current_user
        
        conversations = Conversation.query.filter(
            (Conversation.user1_id == user.id) | (Conversation.user2_id == user.id)
        ).order_by(Conversation.last_message_at.desc()).all()
        
        convs_data = []
        for conv in conversations:
            other_user = conv.get_other_user(user.id)
            unread_count = conv.get_unread_count(user.id)
            
            convs_data.append({
                'id': conv.id,
                'other_user': {
                    'id': other_user.id,
                    'full_name': other_user.masked_full_name,
                    'avatar_url': other_user.avatar_url,
                    'city': other_user.city
                },
                'last_message': conv.last_message_text,
                'last_message_at': conv.last_message_at.isoformat() if conv.last_message_at else None,
                'unread_count': unread_count,
                'post_id': conv.post_id
            })
        
        return jsonify({
            'success': True,
            'conversations': convs_data
        }), 200
        
    except Exception as e:
        print(f"Get conversations error: {e}")
        return jsonify({
            'success': False,
            'error': 'Konuşmalar yüklenemedi'
        }), 500


@api_bp.route('/conversations/<int:conv_id>/messages', methods=['GET'])
@token_required
def get_messages(conv_id):
    """Konuşma mesajlarını getir"""
    try:
        user = request.current_user
        conv = Conversation.query.get_or_404(conv_id)
        
        # Erişim kontrolü
        if conv.user1_id != user.id and conv.user2_id != user.id:
            return jsonify({
                'success': False,
                'error': 'Bu konuşmaya erişim yetkiniz yok'
            }), 403
        
        messages = Message.query.filter_by(conversation_id=conv_id)\
            .order_by(Message.created_at.asc()).all()
        
        msgs_data = []
        for msg in messages:
            msgs_data.append({
                'id': msg.id,
                'sender_id': msg.sender_id,
                'message': msg.message,
                'message_type': msg.message_type,
                'file_url': msg.file_url,
                'file_name': msg.file_name,
                'latitude': msg.latitude,
                'longitude': msg.longitude,
                'duration': msg.duration,
                'created_at': msg.created_at.isoformat(),
                'read_at': msg.read_at.isoformat() if msg.read_at else None,
                'is_mine': msg.sender_id == user.id
            })
        
        # Okunmamış sayacını sıfırla
        if conv.user1_id == user.id:
            conv.unread_count_user1 = 0
        else:
            conv.unread_count_user2 = 0
        db.session.commit()
        
        return jsonify({
            'success': True,
            'messages': msgs_data
        }), 200
        
    except Exception as e:
        print(f"Get messages error: {e}")
        return jsonify({
            'success': False,
            'error': 'Mesajlar yüklenemedi'
        }), 500


@api_bp.route('/conversations/<int:conv_id>/messages', methods=['POST'])
@token_required
def send_message(conv_id):
    """Mesaj gönder"""
    try:
        user = request.current_user
        
        # Handle both JSON and Multipart
        file = None
        if request.is_json:
            data = request.get_json()
            message_text = data.get('message', '').strip()
            message_type = data.get('message_type', 'text')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            duration = data.get('duration')
        else:
            message_text = request.form.get('message', '').strip()
            message_type = request.form.get('message_type', 'text')
            latitude = request.form.get('latitude', type=float)
            longitude = request.form.get('longitude', type=float)
            duration = request.form.get('duration', type=int)
            file = request.files.get('file')
        
        conv = Conversation.query.get_or_404(conv_id)
        
        # Erişim kontrolü
        if conv.user1_id != user.id and conv.user2_id != user.id:
            return jsonify({
                'success': False,
                'error': 'Bu konuşmaya erişim yetkiniz yok'
            }), 403
            
        # Dosya İşlemleri
        file_url = None
        file_name = None
        file_mime_type = None

        if file and file.filename:
            filename = secure_filename(file.filename)
            # Create directory if not exists
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'messages')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file with timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            file_url = f"/static/uploads/messages/{unique_filename}"
            file_name = filename
            file_mime_type = file.content_type

            # Auto-detect type if generic
            if message_type == 'text':
                if file.content_type.startswith('image/'):
                    message_type = 'image'
                elif file.content_type.startswith('audio/'):
                    message_type = 'audio'
                else:
                    message_type = 'file'
        
        if not message_text and message_type == 'text' and not file:
            return jsonify({
                'success': False,
                'error': 'Mesaj boş olamaz'
            }), 400
        
        # Mesaj oluştur
        message = Message(
            conversation_id=conv_id,
            sender_id=user.id,
            message=message_text,
            message_type=message_type,
            latitude=latitude,
            longitude=longitude,
            duration=duration,
            file_url=file_url,
            file_name=file_name,
            file_type=file_mime_type
        )
        db.session.add(message)
        
        # Konuşmayı güncelle
        conv.last_message_at = datetime.now(timezone.utc)
        conv.last_message_text = message_text[:100] if message_text else (f"[{message_type}]" if message_type != 'text' else "Dosya")
        conv.last_message_sender_id = user.id
        
        # Karşı tarafın okunmamış sayacını artır
        if conv.user1_id == user.id:
            conv.unread_count_user2 += 1
            other_user_id = conv.user2_id
        else:
            conv.unread_count_user1 += 1
            other_user_id = conv.user1_id
        
        db.session.commit()
        
        # Bildirim oluştur
        notification_text = message_text[:50] if message_text else (f"Bir {message_type} gönderdi" if message_type != 'text' else "Bir dosya gönderdi")
        notification = Notification(
            user_id=other_user_id,
            type='new_message',
            title='Yeni Mesaj',
            message=f'{user.masked_full_name}: {notification_text}',
            related_user_id=user.id,
            action_url=f'/messages/{conv_id}'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message_id': message.id,
            'file_url': file_url,
            'type': message_type
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Send message error: {e}")
        return jsonify({
            'success': False,
            'error': 'Mesaj gönderilemedi'
        }), 500


# =============================================================================
# PROFILE - Profil İşlemleri
# =============================================================================

@api_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Kullanıcının profilini getir"""
    user = request.current_user
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'city': user.city,
            'district': user.district,
            'bar_association': user.bar_association,
            'bar_registration_number': user.bar_registration_number,
            'lawyer_type': user.lawyer_type,
            'bio': user.bio,
            'avatar_url': user.avatar_url,
            'rating_average': user.rating_average,
            'rating_count': user.rating_count,
            'total_posts_created': user.total_posts_created,
            'total_applications_sent': user.total_applications_sent,
            'accepted_applications': user.accepted_applications,
            'completed_jobs': user.completed_jobs,
            'is_verified': user.is_verified,
            'created_at': user.created_at.isoformat()
        }
    }), 200


@api_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Profili güncelle"""
    try:
        user = request.current_user
        data = request.get_json()
        
        # Güncellenebilir alanlar
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'city' in data:
            user.city = data['city']
        if 'district' in data:
            user.district = data['district']
        if 'bio' in data:
            user.bio = data['bio']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profil güncellendi'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Update profile error: {e}")
        return jsonify({
            'success': False,
            'error': 'Profil güncellenemedi'
        }), 500


@api_bp.route('/profile/avatar', methods=['POST'])
@token_required
def upload_avatar():
    """Profil fotoğrafı yükle"""
    try:
        user = request.current_user
        
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Dosya bulunamadı'
            }), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Dosya seçilmedi'
            }), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(f"avatar_{user.id}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}")
            
            # Upload klasörünü kontrol et
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Dosyayı kaydet
            file.save(os.path.join(upload_dir, filename))
            
            # Veritabanını güncelle
            # URL formatı: /static/uploads/avatars/filename
            avatar_url = f"/static/uploads/avatars/{filename}"
            user.avatar_url = avatar_url
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Profil fotoğrafı güncellendi',
                'avatar_url': avatar_url
            }), 200
            
        else:
            return jsonify({
                'success': False,
                'error': 'Geçersiz dosya türü'
            }), 400
            
    except Exception as e:
        print(f"Upload avatar error: {e}")
        return jsonify({
            'success': False,
            'error': 'Yükleme başarısız'
        }), 500


# =============================================================================
# SYNC - Real-time Updates
# =============================================================================

@api_bp.route('/mobile/sync', methods=['GET'])
@token_required
def mobile_sync():
    """
    Yeni bildirimleri ve mesajları kontrol et
    Query Params: last_check (ISO format timestamp)
    """
    try:
        user = request.current_user
        last_check_str = request.args.get('last_check')
        
        if last_check_str and last_check_str != 'null' and last_check_str != '':
            try:
                last_check = datetime.fromisoformat(last_check_str.replace('Z', '+00:00'))
                # Safety cap: 5 minutes
                five_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
                if last_check < five_mins_ago:
                    last_check = five_mins_ago
            except ValueError:
                last_check = datetime.now(timezone.utc) - timedelta(seconds=60)
        else:
            last_check = datetime.now(timezone.utc) - timedelta(seconds=60)
            
        # New Notifications
        new_notifications = Notification.query.filter(
            Notification.user_id == user.id,
            Notification.created_at > last_check,
            Notification.read_at.is_(None)
        ).all()
        
        # New Messages (from others)
        new_messages = Message.query.filter(
            Message.created_at > last_check,
            Message.sender_id != user.id,
            Message.read_at.is_(None)
        ).join(User, Message.sender_id == User.id).add_columns(User.full_name, User.avatar_url).all()
        
        sync_data = []
        
        # Process notifications
        for n in new_notifications:
            sync_data.append({
                'id': f'notif-{n.id}',
                'type': n.type,
                'title': n.title,
                'message': n.message,
                'url': n.action_url,
                'created_at': n.created_at.isoformat(),
                'is_message': False
            })
            
        # Process messages
        for msg, sender_name, sender_avatar in new_messages:
            # Verify conversation participation
            conversation = msg.conversation
            if conversation and (conversation.user1_id == user.id or conversation.user2_id == user.id):
                sync_data.append({
                    'id': f'msg-{msg.id}',
                    'type': 'message',
                    'title': sender_name,
                    'message': msg.message if msg.message_type == 'text' else f'[{msg.message_type}]',
                    'url': f'/messages/{msg.conversation_id}',
                    'conversation_id': msg.conversation_id,
                    'created_at': msg.created_at.isoformat(),
                    'avatar': sender_avatar,
                    'is_message': True
                })
                
        return jsonify({
            'success': True,
            'items': sync_data,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        print(f"Mobile sync error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =============================================================================
# NOTIFICATIONS - Bildirimler
# =============================================================================

@api_bp.route('/notifications', methods=['GET'])
@token_required
def get_notifications():
    """Bildirimleri listele"""
    try:
        user = request.current_user
        
        notifications = Notification.query.filter_by(user_id=user.id)\
            .order_by(Notification.created_at.desc())\
            .limit(50).all()
        
        notifs_data = []
        for notif in notifications:
            notifs_data.append({
                'id': notif.id,
                'type': notif.type,
                'title': notif.title,
                'message': notif.message,
                'read_at': notif.read_at.isoformat() if notif.read_at else None,
                'created_at': notif.created_at.isoformat(),
                'action_url': notif.action_url
            })
        
        return jsonify({
            'success': True,
            'notifications': notifs_data,
            'unread_count': user.notifications_unread_count
        }), 200
        
    except Exception as e:
        print(f"Get notifications error: {e}")
        return jsonify({
            'success': False,
            'error': 'Bildirimler yüklenemedi'
        }), 500


@api_bp.route('/notifications/<int:notif_id>/read', methods=['POST'])
@token_required
def mark_notification_read(notif_id):
    """Bildirimi okundu olarak işaretle"""
    try:
        user = request.current_user
        notif = Notification.query.get_or_404(notif_id)
        
        if notif.user_id != user.id:
            return jsonify({
                'success': False,
                'error': 'Erişim yetkiniz yok'
            }), 403
        
        if not notif.read_at:
            notif.read_at = datetime.now(timezone.utc)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bildirim okundu olarak işaretlendi'
        }), 200
        
    except Exception as e:
        print(f"Mark notification read error: {e}")
        return jsonify({
            'success': False,
            'error': 'İşlem başarısız'
        }), 500


@api_bp.route('/posts/<int:post_id>/images', methods=['POST'])
@token_required
def upload_post_image(post_id):
    """İlana resim yükle"""
    try:
        user = request.current_user
        post = TevkilPost.query.get_or_404(post_id)
        
        # İlan sahibi kontrolü
        if post.user_id != user.id:
            return jsonify({
                'success': False,
                'error': 'Bu işlem için yetkiniz yok'
            }), 403
            
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Dosya bulunamadı'
            }), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Dosya seçilmedi'
            }), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(f"post_{post.id}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}")
            
            # Upload klasörünü kontrol et
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'posts')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Dosyayı kaydet
            file.save(os.path.join(upload_dir, filename))
            
            # Veritabanına kaydet
            image_url = f"/static/uploads/posts/{filename}"
            post_image = PostImage(
                post_id=post.id,
                image_url=image_url
            )
            db.session.add(post_image)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Resim yüklendi',
                'image': {
                    'id': post_image.id,
                    'url': post_image.image_url
                }
            }), 201
            
        else:
            return jsonify({
                'success': False,
                'error': 'Geçersiz dosya türü'
            }), 400
            
    except Exception as e:
        print(f"Upload post image error: {e}")
        return jsonify({
            'success': False,
            'error': 'Yükleme başarısız'
        }), 500


@api_bp.route('/posts/images/<int:image_id>', methods=['DELETE'])
@token_required
def delete_post_image(image_id):
    """İlan resmini sil"""
    try:
        user = request.current_user
        image = PostImage.query.get_or_404(image_id)
        post = TevkilPost.query.get(image.post_id)
        
        # İlan sahibi kontrolü
        if post.user_id != user.id:
            return jsonify({
                'success': False,
                'error': 'Bu işlem için yetkiniz yok'
            }), 403
            
        # Dosyayı sistemden sil
        try:
            # URL'den dosya yolunu bul
            # /static/uploads/posts/filename -> static/uploads/posts/filename
            file_path = image.image_url.lstrip('/')
            full_path = os.path.join(current_app.root_path, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"File delete error: {e}")
            
        # Veritabanından sil
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Resim silindi'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete post image error: {e}")
        return jsonify({
            'success': False,
            'error': 'Silme işlemi başarısız'
        }), 500


# =============================================================================
# JOBS - İş İlanları
# =============================================================================

@api_bp.route('/jobs', methods=['GET'])
@token_required
def get_jobs():
    """
    İş ilanlarını listele
    """
    try:
        # Filtreler
        city = request.args.get('city')
        position_type = request.args.get('position_type')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        query = JobPost.query.filter_by(is_active=True)
        
        if city:
            query = query.filter_by(city=city)
        if position_type:
            query = query.filter_by(position_type=position_type)
        if search:
            query = query.filter(JobPost.title.ilike(f'%{search}%') | JobPost.description.ilike(f'%{search}%'))
            
        pagination = query.order_by(JobPost.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        posts = []
        for post in pagination.items:
            posts.append({
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'position_type': post.position_type,
                'employment_type': post.employment_type,
                'city': post.city,
                'district': post.district,
                'office_name': post.office_name,
                'salary_min': post.salary_min,
                'salary_max': post.salary_max,
                'currency': post.currency,
                'experience_years': post.experience_years,
                'requirements': post.requirements,
                'views': post.views,
                'applications_count': post.applications_count,
                'created_at': post.created_at.isoformat(),
                'user': {
                    'id': post.user.id,
                    'full_name': post.user.masked_full_name,
                    'avatar_url': post.user.avatar_url
                }
            })
            
        return jsonify({
            'success': True,
            'posts': posts,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next
            }
        }), 200
    except Exception as e:
        print(f"Get jobs error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/jobs/<int:post_id>', methods=['GET'])
@token_required
def get_job_detail(post_id):
    try:
        post = JobPost.query.get_or_404(post_id)
        post.views += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'post': {
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'position_type': post.position_type,
                'employment_type': post.employment_type,
                'city': post.city,
                'district': post.district,
                'office_name': post.office_name,
                'salary_min': post.salary_min,
                'salary_max': post.salary_max,
                'currency': post.currency,
                'experience_years': post.experience_years,
                'requirements': post.requirements,
                'views': post.views,
                'applications_count': post.applications_count,
                'created_at': post.created_at.isoformat(),
                'user': {
                    'id': post.user.id,
                    'full_name': post.user.masked_full_name,
                    'avatar_url': post.user.avatar_url,
                    'city': post.user.city
                }
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/jobs', methods=['POST'])
@token_required
def create_job():
    try:
        user = request.current_user
        data = request.get_json()
        
        post = JobPost(
            user_id=user.id,
            title=data['title'],
            description=data['description'],
            position_type=data['position_type'],
            employment_type=data.get('employment_type', 'full_time'),
            city=data['city'],
            district=data.get('district'),
            office_name=data.get('office_name'),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            currency=data.get('currency', 'TRY'),
            experience_years=data.get('experience_years'),
            requirements=data.get('requirements', [])
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'İş ilanı oluşturuldu',
            'post_id': post.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# OFFICE - Ofis İlanları
# =============================================================================

@api_bp.route('/office', methods=['GET'])
@token_required
def get_office_posts():
    """
    Ofis ilanlarını listele
    """
    try:
        # Filtreler
        city = request.args.get('city')
        office_type = request.args.get('office_type') # category field in model
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        query = OfficePost.query.filter_by(is_active=True)
        
        if city:
            query = query.filter_by(city=city)
        if office_type:
            query = query.filter_by(category=office_type)
        if search:
            query = query.filter(OfficePost.title.ilike(f'%{search}%') | OfficePost.description.ilike(f'%{search}%'))
            
        pagination = query.order_by(OfficePost.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        posts = []
        for post in pagination.items:
            image_urls = [img.image_url for img in post.images]
            
            posts.append({
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'office_type': post.category,
                'price': post.price,
                'currency': post.currency,
                'city': post.city,
                'district': post.district,
                'm2': post.square_meters,
                'room_count': post.room_count,
                'image_urls': image_urls,
                'views': post.views,
                'created_at': post.created_at.isoformat(),
                'user': {
                    'id': post.user.id,
                    'full_name': post.user.masked_full_name,
                    'avatar_url': post.user.avatar_url
                }
            })
            
        return jsonify({
            'success': True,
            'posts': posts,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next
            }
        }), 200
    except Exception as e:
        print(f"Get office posts error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/office/<int:post_id>', methods=['GET'])
@token_required
def get_office_post_detail(post_id):
    try:
        post = OfficePost.query.get_or_404(post_id)
        post.views += 1
        db.session.commit()
        
        image_urls = [img.image_url for img in post.images]
        
        return jsonify({
            'success': True,
            'post': {
                'id': post.id,
                'title': post.title,
                'description': post.description,
                'office_type': post.category,
                'price': post.price,
                'currency': post.currency,
                'city': post.city,
                'district': post.district,
                'address': post.address,
                'm2': post.square_meters,
                'room_count': post.room_count,
                'floor': post.floor,
                'heating_type': post.heating_type,
                'is_furnished': post.is_furnished,
                'image_urls': image_urls,
                'views': post.views,
                'created_at': post.created_at.isoformat(),
                'user': {
                    'id': post.user.id,
                    'full_name': post.user.masked_full_name,
                    'avatar_url': post.user.avatar_url,
                    'city': post.user.city
                }
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/office', methods=['POST'])
@token_required
def create_office_post():
    try:
        user = request.current_user
        data = request.get_json()
        
        post = OfficePost(
            user_id=user.id,
            title=data['title'],
            description=data['description'],
            category=data['office_type'],
            price=data['price'],
            currency=data.get('currency', 'TRY'),
            city=data['city'],
            district=data.get('district'),
            address=data.get('address'),
            square_meters=data.get('m2'),
            room_count=data.get('room_count'),
            floor=data.get('floor'),
            heating_type=data.get('heating_type'),
            is_furnished=data.get('is_furnished', False)
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Ofis ilanı oluşturuldu',
            'post_id': post.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
