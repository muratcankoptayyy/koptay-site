"""
Database models for Tevkil Platform
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Kullanıcı (Avukat) Modeli"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profil Bilgileri
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    whatsapp_number = db.Column(db.String(20))
    
    # Baro Bilgileri
    bar_association = db.Column(db.String(100))  # "İstanbul Barosu"
    bar_registration_number = db.Column(db.String(50))  # Sicil numarası
    lawyer_type = db.Column(db.String(20), default='avukat')  # 'avukat' veya 'stajyer'
    
    # Konum
    city = db.Column(db.String(50))
    district = db.Column(db.String(50))
    address = db.Column(db.Text)
    
    # Profesyonel Bilgi
    specializations = db.Column(db.JSON)  # ["Boşanma", "Miras", "Ticaret"]
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    
    # İstatistikler
    rating_average = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    total_posts_created = db.Column(db.Integer, default=0)
    total_applications_sent = db.Column(db.Integer, default=0)
    total_applications_received = db.Column(db.Integer, default=0)
    accepted_applications = db.Column(db.Integer, default=0)
    completed_jobs = db.Column(db.Integer, default=0)
    
    # Durum
    is_verified = db.Column(db.Boolean, default=False)  # Admin onayı
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Bildirim Tercihleri
    notify_new_application = db.Column(db.Boolean, default=True)
    notify_application_status = db.Column(db.Boolean, default=True)
    notify_new_message = db.Column(db.Boolean, default=True)
    
    # Zaman Damgaları
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 📱 MOBILE API TOKEN - Kalıcı kimlik doğrulama
    api_token = db.Column(db.String(64), unique=True, index=True)
    api_token_created_at = db.Column(db.DateTime)
    api_token_last_used = db.Column(db.DateTime)
    
    # İlişkiler
    posts = db.relationship('TevkilPost', backref='user', lazy='dynamic', foreign_keys='TevkilPost.user_id')
    applications = db.relationship('Application', backref='applicant', lazy='dynamic', foreign_keys='Application.applicant_id')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', foreign_keys='Notification.user_id')
    
    @property
    def notifications_unread_count(self):
        """Okunmamış bildirim sayısı"""
        return self.notifications.filter_by(read_at=None).count()
    
    @property
    def masked_full_name(self):
        """KVKK uyumlu maskelenmiş ad"""
        if not self.full_name:
            return "Anonim"
        parts = self.full_name.strip().split()
        if not parts:
            return "Anonim"
        return ' '.join([part[0] + '*' * (len(part)-1) for part in parts])
    
    def set_password(self, password):
        """Şifre hash'le"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Şifre kontrolü"""
        return check_password_hash(self.password_hash, password)
    
    def generate_api_token(self):
        """Mobil kimlik doğrulama için benzersiz API token oluştur"""
        import secrets
        self.api_token = secrets.token_urlsafe(48)
        self.api_token_created_at = datetime.now(timezone.utc)
        self.api_token_last_used = datetime.now(timezone.utc)
        return self.api_token
    
    def verify_api_token(self, token):
        """API token doğrula ve son kullanım zamanını güncelle"""
        if self.api_token and self.api_token == token:
            self.api_token_last_used = datetime.now(timezone.utc)
            return True
        return False
    
    def revoke_api_token(self):
        """API token'ı iptal et (çıkış için)"""
        self.api_token = None
        self.api_token_created_at = None
        self.api_token_last_used = None
    
    def __repr__(self):
        return f'<User {self.email}>'


class TevkilPost(db.Model):
    """Tevkil İlanı Modeli"""
    __tablename__ = 'tevkil_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # İçerik
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # "boşanma", "miras", "ticaret"
    
    # Detaylar
    urgency_level = db.Column(db.String(20), default='normal')  # normal, urgent, very_urgent
    city = db.Column(db.String(50))
    district = db.Column(db.String(50))
    courthouse = db.Column(db.String(100))  # Adliye
    remote_allowed = db.Column(db.Boolean, default=False)
    
    # Konum (Geocoding)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Fiyat
    price_min = db.Column(db.Float)
    price_max = db.Column(db.Float)
    
    # Tarihler
    deadline = db.Column(db.DateTime)
    court_date = db.Column(db.DateTime)
    
    # Durum
    status = db.Column(db.String(20), default='active')  # active, assigned, completed, cancelled
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # İstatistikler
    views = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    
    # Zaman Damgaları
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime)
    
    # İlişkiler
    applications = db.relationship('Application', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def is_expired(self):
        """İlan süresi dolmuş mu?"""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_active(self):
        """İlan aktif mi?"""
        return self.status == 'active' and not self.is_expired
    
    def __repr__(self):
        return f'<TevkilPost {self.title}>'


class PostImage(db.Model):
    """İlan Resimleri Modeli"""
    __tablename__ = 'post_images'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('tevkil_posts.id'), nullable=False)
    
    image_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # İlişki
    post = db.relationship('TevkilPost', backref=db.backref('images', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<PostImage {self.id} for Post {self.post_id}>'


class Application(db.Model):
    """Başvuru Modeli"""
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('tevkil_posts.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Başvuru Detayları
    message = db.Column(db.Text)
    proposed_price = db.Column(db.Float)
    
    # Durum
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    
    # Zaman Damgaları
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Application {self.id} for Post {self.post_id}>'


class Conversation(db.Model):
    """İki kullanıcı arasındaki sohbet"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Katılımcılar (user1_id < user2_id)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # İlan bağlantısı
    post_id = db.Column(db.Integer, db.ForeignKey('tevkil_posts.id'))
    
    # Son mesaj bilgisi
    last_message_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_message_text = db.Column(db.Text)
    last_message_sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Okunmamış mesaj sayıları
    unread_count_user1 = db.Column(db.Integer, default=0)
    unread_count_user2 = db.Column(db.Integer, default=0)
    
    # Zaman Damgaları
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # İlişkiler
    user1 = db.relationship('User', foreign_keys=[user1_id], backref='conversations_as_user1')
    user2 = db.relationship('User', foreign_keys=[user2_id], backref='conversations_as_user2')
    post = db.relationship('TevkilPost', foreign_keys=[post_id])
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('user1_id', 'user2_id', 'post_id', name='unique_conversation'),
    )
    
    def get_other_user(self, current_user_id):
        """Karşı kullanıcıyı döndür"""
        return self.user2 if current_user_id == self.user1_id else self.user1
    
    def get_unread_count(self, user_id):
        """Belirli kullanıcı için okunmamış sayısı"""
        return self.unread_count_user1 if user_id == self.user1_id else self.unread_count_user2
    
    def has_unread_messages(self, user_id):
        """Kullanıcının okunmamış mesajı var mı?"""
        return self.get_unread_count(user_id) > 0
    
    @staticmethod
    def get_or_create(user1_id, user2_id, post_id=None):
        """Conversation bul veya oluştur"""
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
        
        conversation = Conversation.query.filter_by(
            user1_id=user1_id,
            user2_id=user2_id,
            post_id=post_id
        ).first()
        
        if not conversation:
            conversation = Conversation(
                user1_id=user1_id,
                user2_id=user2_id,
                post_id=post_id
            )
            db.session.add(conversation)
            db.session.flush()
        
        return conversation
    
    def __repr__(self):
        return f'<Conversation {self.id}>'


class Message(db.Model):
    """Mesaj Modeli"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # İçerik
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, file, image
    
    # Dosya bilgisi
    file_name = db.Column(db.String(255))
    file_url = db.Column(db.String(500))
    file_type = db.Column(db.String(100))
    
    # Durum
    read_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Zaman Damgası
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # İlişkiler
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    
    @property
    def is_read(self):
        return self.read_at is not None
    
    def __repr__(self):
        return f'<Message {self.id}>'


class Notification(db.Model):
    """Bildirim Modeli"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # İçerik
    type = db.Column(db.String(50), nullable=False)  # new_application, message, system
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    
    # İlişkili Objeler
    related_post_id = db.Column(db.Integer, db.ForeignKey('tevkil_posts.id'))
    related_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Durum
    read_at = db.Column(db.DateTime)
    action_url = db.Column(db.String(500))
    
    # Zaman Damgası
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # İlişkiler
    related_post = db.relationship('TevkilPost', foreign_keys=[related_post_id])
    related_user = db.relationship('User', foreign_keys=[related_user_id])
    
    @property
    def is_read(self):
        return self.read_at is not None
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.type}>'
