"""
Database models for Tevkil Platform
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = (
        db.UniqueConstraint('bar_association', 'bar_registration_number', name='unique_bar_registration'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile Information
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    whatsapp_number = db.Column(db.String(20))
    tc_number = db.Column(db.String(11))  # T.C. Kimlik Numarası
    
    # Baro Bilgileri
    bar_association = db.Column(db.String(100))  # Bağlı olduğu baro (örn: "İstanbul Barosu")
    bar_registration_number = db.Column(db.String(50))  # Baro sicil numarası
    lawyer_type = db.Column(db.String(20), default='avukat')  # 'avukat' veya 'stajyer' (sadece admin için görünür)
    
    # Location
    city = db.Column(db.String(50))
    district = db.Column(db.String(50))
    address = db.Column(db.Text)  # Tam adres bilgisi (yetki belgesi için)
    
    # Professional Info
    specializations = db.Column(db.JSON)  # List of specialization areas
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    
    # Social Media Links
    linkedin_url = db.Column(db.String(255))
    twitter_url = db.Column(db.String(255))
    instagram_url = db.Column(db.String(255))
    website_url = db.Column(db.String(255))
    
    # İstatistikler - Duruşma ve Görev
    attended_hearings_count = db.Column(db.Integer, default=0)  # Katıldığı duruşma sayısı
    completed_tasks_count = db.Column(db.Integer, default=0)  # Tamamladığı görev sayısı
    
    # Stats
    rating = db.Column(db.Float, default=0.0)
    rating_average = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    total_jobs = db.Column(db.Integer, default=0)
    completed_jobs = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    total_posts_created = db.Column(db.Integer, default=0)
    total_applications_sent = db.Column(db.Integer, default=0)
    total_applications_received = db.Column(db.Integer, default=0)
    accepted_applications = db.Column(db.Integer, default=0)
    rejected_applications = db.Column(db.Integer, default=0)
    average_response_time_hours = db.Column(db.Float, default=0.0)
    total_views_received = db.Column(db.Integer, default=0)
    profile_views = db.Column(db.Integer, default=0)
    last_post_date = db.Column(db.DateTime)
    last_application_date = db.Column(db.DateTime)
    
    # Status
    verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)  # Admin kontrolü
    
    # Notification Preferences
    notify_new_application = db.Column(db.Boolean, default=True)  # Yeni başvuru bildirimi
    notify_application_status = db.Column(db.Boolean, default=True)  # Başvuru durum değişikliği
    notify_new_message = db.Column(db.Boolean, default=True)  # Yeni mesaj bildirimi
    notify_new_rating = db.Column(db.Boolean, default=True)  # Yeni değerlendirme bildirimi
    notify_post_expiring = db.Column(db.Boolean, default=True)  # İlan sona erme uyarısı
    notify_system = db.Column(db.Boolean, default=True)  # Sistem bildirimleri
    notify_email = db.Column(db.Boolean, default=False)  # Email bildirimleri
    
    # Privacy Settings
    profile_visible = db.Column(db.Boolean, default=True)  # Profil herkese açık mı?
    show_phone = db.Column(db.Boolean, default=True)  # Telefon numarası görünsün mü?
    show_email = db.Column(db.Boolean, default=False)  # E-posta görünsün mü?
    show_last_active = db.Column(db.Boolean, default=True)  # Son görülme göster
    
    # Security Settings
    two_factor_enabled = db.Column(db.Boolean, default=False)  # 2FA aktif mi?
    two_factor_secret = db.Column(db.String(32))  # TOTP secret
    two_factor_backup_codes = db.Column(db.Text)  # JSON array of backup codes
    last_password_change = db.Column(db.DateTime)  # Son şifre değişikliği
    password_expires_at = db.Column(db.DateTime)  # Şifre geçerlilik süresi
    failed_login_attempts = db.Column(db.Integer, default=0)  # Başarısız giriş sayısı
    account_locked_until = db.Column(db.DateTime)  # Hesap kilidi
    security_question = db.Column(db.String(200))  # Güvenlik sorusu
    security_answer = db.Column(db.String(255))  # Güvenlik cevabı (hashed)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 📱 MOBILE API TOKEN - Persistent authentication for mobile apps
    api_token = db.Column(db.String(64), unique=True, index=True)  # Unique token for mobile auth
    api_token_created_at = db.Column(db.DateTime)  # Token creation time
    api_token_last_used = db.Column(db.DateTime)  # Last time token was used
    
    # Relationships
    posts = db.relationship('TevkilPost', backref='user', lazy='dynamic', foreign_keys='TevkilPost.user_id')
    applications = db.relationship('Application', backref='applicant', lazy='dynamic', foreign_keys='Application.applicant_id')
    ratings_given = db.relationship('Rating', backref='reviewer', lazy='dynamic', foreign_keys='Rating.reviewer_id')
    ratings_received = db.relationship('Rating', backref='reviewed', lazy='dynamic', foreign_keys='Rating.reviewed_id')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', foreign_keys='Notification.user_id')
    
    @property
    def notifications_unread_count(self):
        """Okunmamış bildirim sayısı"""
        return self.notifications.filter_by(read_at=None).count()
    
    @property
    def is_trainee(self):
        """Kullanıcının stajyer avukat olup olmadığını kontrol eder"""
        return self.lawyer_type == 'stajyer'
    
    @property
    def can_apply_to_jobs(self):
        """Kullanıcının görevlere başvuru yapıp yapamayacağını kontrol eder"""
        # Stajyer avukatlar başvuru yapamaz
        return self.lawyer_type != 'stajyer'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_api_token(self):
        """Generate a unique API token for mobile authentication"""
        import secrets
        self.api_token = secrets.token_urlsafe(48)  # 64 characters base64url
        self.api_token_created_at = datetime.utcnow()
        self.api_token_last_used = datetime.utcnow()
        return self.api_token
    
    def verify_api_token(self, token):
        """Verify API token and update last used timestamp"""
        if self.api_token and self.api_token == token:
            self.api_token_last_used = datetime.utcnow()
            return True
        return False
    
    def revoke_api_token(self):
        """Revoke API token (for logout)"""
        self.api_token = None
        self.api_token_created_at = None
        self.api_token_last_used = None
    
    def __repr__(self):
        return f'<User {self.email}>'


class TevkilPost(db.Model):
    __tablename__ = 'tevkil_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Post Content
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # boşanma, miras, ticaret, etc.
    
    # Details
    urgency_level = db.Column(db.String(20), default='normal')  # normal, urgent, very_urgent
    location = db.Column(db.String(100))
    city = db.Column(db.String(50))  # İl
    district = db.Column(db.String(50))  # İlçe
    courthouse = db.Column(db.String(100))  # Adliye
    remote_allowed = db.Column(db.Boolean, default=False)
    
    # Geocoding - Coordinates
    latitude = db.Column(db.Float)  # Enlem
    longitude = db.Column(db.Float)  # Boylam
    formatted_address = db.Column(db.String(300))  # Google'dan gelen tam adres
    
    # Price (optional)
    price_min = db.Column(db.Float)
    price_max = db.Column(db.Float)
    
    # Dates
    deadline = db.Column(db.DateTime)
    court_date = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, assigned, completed, cancelled
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Stats
    views = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    unique_viewers = db.Column(db.Integer, default=0)
    application_rate = db.Column(db.Float, default=0.0)
    average_application_response = db.Column(db.Float, default=0.0)
    last_viewed_at = db.Column(db.DateTime)
    first_application_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    applications = db.relationship('Application', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TevkilPost {self.title}>'


class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('tevkil_posts.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Application Details
    message = db.Column(db.Text)
    proposed_price = db.Column(db.Float)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    
    # Response time (for metrics)
    response_time = db.Column(db.Integer)  # in minutes
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Application {self.id} for Post {self.post_id}>'


class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('tevkil_posts.id'))
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Ratings (1-5)
    rating = db.Column(db.Integer, nullable=False)  # Overall rating
    professionalism = db.Column(db.Integer)
    communication = db.Column(db.Integer)
    quality = db.Column(db.Integer)
    
    # Comment
    comment = db.Column(db.Text)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Rating {self.rating} by User {self.reviewer_id}>'


class Conversation(db.Model):
    """İki kullanıcı arasındaki sohbet konuşması"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Participants (her zaman 2 kişi - user1_id < user2_id olacak şekilde)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # İlan ile ilişkili mi?
    post_id = db.Column(db.Integer, db.ForeignKey('tevkil_posts.id'))
    
    # Son mesaj bilgisi
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_text = db.Column(db.Text)  # Önizleme için
    last_message_sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Okunmamış mesaj sayıları (her kullanıcı için)
    unread_count_user1 = db.Column(db.Integer, default=0)
    unread_count_user2 = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user1 = db.relationship('User', foreign_keys=[user1_id], backref='conversations_as_user1')
    user2 = db.relationship('User', foreign_keys=[user2_id], backref='conversations_as_user2')
    post = db.relationship('TevkilPost', foreign_keys=[post_id])
    last_message_sender = db.relationship('User', foreign_keys=[last_message_sender_id])
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', 
                              cascade='all, delete-orphan', order_by='Message.created_at')
    
    # Unique constraint: aynı iki kullanıcı arasında bir conversation
    __table_args__ = (
        db.UniqueConstraint('user1_id', 'user2_id', 'post_id', name='unique_conversation'),
    )
    
    def get_other_user(self, current_user_id):
        """Mevcut kullanıcının karşısındaki kişiyi döndür"""
        return self.user2 if current_user_id == self.user1_id else self.user1
    
    def get_unread_count(self, user_id):
        """Belirli bir kullanıcı için okunmamış mesaj sayısı"""
        return self.unread_count_user1 if user_id == self.user1_id else self.unread_count_user2
    
    def mark_as_read(self, user_id):
        """Kullanıcı için tüm mesajları okundu işaretle"""
        if user_id == self.user1_id:
            self.unread_count_user1 = 0
        else:
            self.unread_count_user2 = 0
    
    @staticmethod
    def get_or_create(user1_id, user2_id, post_id=None):
        """İki kullanıcı arasında conversation bul veya oluştur"""
        # user1_id her zaman küçük olsun
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
        return f'<Conversation {self.id} between {self.user1_id} and {self.user2_id}>'


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # DEPRECATED: Eski sistem uyumluluğu için (migration sonrası silinebilir)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('tevkil_posts.id'))
    
    # Message Content
    message = db.Column(db.Text, nullable=False)
    attachments = db.Column(db.JSON)  # List of attachment URLs
    
    # Message Type & File Info
    message_type = db.Column(db.String(20), default='text')  # text, file, image, emoji
    file_name = db.Column(db.String(255))  # Dosya adı
    file_size = db.Column(db.Integer)  # Dosya boyutu (bytes)
    file_url = db.Column(db.String(500))  # Dosya URL
    file_type = db.Column(db.String(100))  # MIME type
    
    # Pinning
    is_pinned = db.Column(db.Boolean, default=False)  # Sabitlenmiş mi?
    pinned_at = db.Column(db.DateTime)  # Sabitlenme zamanı
    pinned_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Kim sabitledi
    
    # Reactions (JSON: {user_id: emoji})
    reactions = db.Column(db.Text)  # JSON formatında tepkiler
    
    # Editing
    edited_at = db.Column(db.DateTime)  # Düzenlenme zamanı
    is_deleted = db.Column(db.Boolean, default=False)  # Silinmiş mi?
    
    # Reply to another message
    reply_to_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    
    # Status
    delivered_at = db.Column(db.DateTime, default=datetime.utcnow)  # Karşı tarafa ulaştı
    read_at = db.Column(db.DateTime)  # Karşı taraf okudu
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    post = db.relationship('TevkilPost', foreign_keys=[post_id])
    reply_to = db.relationship('Message', remote_side=[id], backref='replies')
    pinned_by_user = db.relationship('User', foreign_keys=[pinned_by])
    
    @property
    def is_read(self):
        """Mesaj okundu mu?"""
        return self.read_at is not None
    
    @property
    def is_delivered(self):
        """Mesaj iletildi mi?"""
        return self.delivered_at is not None
    
    def get_reactions(self):
        """Tepkileri dict olarak döndür"""
        import json
        if self.reactions:
            try:
                return json.loads(self.reactions)
            except:
                return {}
        return {}
    
    def add_reaction(self, user_id, emoji):
        """Mesaja tepki ekle"""
        import json
        reactions = self.get_reactions()
        reactions[str(user_id)] = emoji
        self.reactions = json.dumps(reactions)
    
    def remove_reaction(self, user_id):
        """Tepkiyi kaldır"""
        import json
        reactions = self.get_reactions()
        if str(user_id) in reactions:
            del reactions[str(user_id)]
            self.reactions = json.dumps(reactions)
    
    def __repr__(self):
        return f'<Message {self.id} in Conversation {self.conversation_id}>'


class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('tevkil_posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='favorites')
    post = db.relationship('TevkilPost', backref='favorited_by')
    
    # Unique constraint: bir kullanıcı aynı ilanı birden fazla favoriye ekleyemesin
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_favorite'),)
    
    def __repr__(self):
        return f'<Favorite user={self.user_id} post={self.post_id}>'


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Notification Content
    type = db.Column(db.String(50), nullable=False)  # new_application, application_accepted, application_rejected, message, rating, post_expiring, system
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    
    # Related Objects
    related_post_id = db.Column(db.Integer, db.ForeignKey('tevkil_posts.id'))
    related_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Priority & Category
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    category = db.Column(db.String(50), default='general')  # application, message, system, warning
    
    # Status
    read_at = db.Column(db.DateTime)
    clicked_at = db.Column(db.DateTime)
    archived_at = db.Column(db.DateTime)  # Arşivlenen bildirimler
    
    # Action URL
    action_url = db.Column(db.String(500))  # Bildiriime tıklanınca gidilecek URL
    action_text = db.Column(db.String(100))  # "İlana Git", "Mesajı Gör", vb.
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Bildirimin geçerlilik süresi
    
    @property
    def is_read(self):
        """Bildirim okundu mu?"""
        return self.read_at is not None
    
    @property
    def is_new(self):
        """Bildirim 24 saatten yeni mi?"""
        if not self.created_at:
            return False
        time_diff = datetime.now(timezone.utc) - self.created_at.replace(tzinfo=timezone.utc)
        return time_diff.total_seconds() < 86400  # 24 saat
    
    @property
    def time_ago(self):
        """Bildirim ne kadar süre önce oluşturuldu?"""
        if not self.created_at:
            return "Bilinmiyor"
        
        now = datetime.now(timezone.utc)
        created = self.created_at.replace(tzinfo=timezone.utc)
        diff = now - created
        
        seconds = diff.total_seconds()
        if seconds < 60:
            return "Az önce"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} dakika önce"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} saat önce"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days} gün önce"
        else:
            weeks = int(seconds / 604800)
            return f"{weeks} hafta önce"
    
    def __repr__(self):
        return f'<Notification {self.type} for User {self.user_id}>'

class PasswordReset(db.Model):
    """Password reset token model"""
    __tablename__ = 'password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)
    
    # Relationship
    user = db.relationship('User', backref='password_resets')
    
    def is_valid(self):
        """Check if token is still valid"""
        if self.used_at:
            return False
        return datetime.now(timezone.utc) < self.expires_at
    
    def __repr__(self):
        return f'<PasswordReset {self.token} for User {self.user_id}>'


class UserSession(db.Model):
    """Kullanıcı oturum takibi"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    # Device & Location Info
    device_info = db.Column(db.String(255))  # "iPhone 12, iOS 15"
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    location = db.Column(db.String(100))  # "Istanbul, Turkey"
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationship
    user = db.relationship('User', backref='sessions')
    
    def is_expired(self):
        """Oturum süresi doldu mu?"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def __repr__(self):
        return f'<UserSession {self.id} for User {self.user_id}>'


class SecurityLog(db.Model):
    """Güvenlik olayları log'u"""
    __tablename__ = 'security_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Event Info
    event_type = db.Column(db.String(50), nullable=False, index=True)
    # login_success, login_failed, logout, password_change, 2fa_enabled, 
    # 2fa_disabled, account_locked, suspicious_activity, etc.
    
    event_severity = db.Column(db.String(20), default='INFO')  # INFO, WARNING, ERROR, CRITICAL
    
    # Request Info
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    location = db.Column(db.String(100))
    
    # Details
    description = db.Column(db.Text)
    event_metadata = db.Column(db.Text)  # JSON additional data (renamed from metadata)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = db.relationship('User', backref='security_logs')
    
    def __repr__(self):
        return f'<SecurityLog {self.event_type} for User {self.user_id}>'


class PasswordHistory(db.Model):
    """Şifre geçmişi (aynı şifre tekrar kullanılmasın)"""
    __tablename__ = 'password_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = db.relationship('User', backref='password_history')
    
    def __repr__(self):
        return f'<PasswordHistory for User {self.user_id}>'


class LoginAttempt(db.Model):
    """Login denemeleri takibi (rate limiting için)"""
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    ip_address = db.Column(db.String(50), index=True)
    user_agent = db.Column(db.Text)
    
    # Result
    success = db.Column(db.Boolean, default=False)
    failure_reason = db.Column(db.String(100))  # invalid_password, account_locked, etc.
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<LoginAttempt {self.email} - {"Success" if self.success else "Failed"}>'
