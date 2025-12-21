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
    tc_number = db.Column(db.String(11))  # T.C. Kimlik No
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
    
    # CV Bilgileri
    education = db.Column(db.JSON) # [{'school': '...', 'degree': '...', 'year': '...'}]
    work_history = db.Column(db.JSON) # [{'company': '...', 'position': '...', 'years': '...'}]
    skills = db.Column(db.JSON) # ['Python', 'Java', ...]
    
    # Detaylı CV Bilgileri
    birth_date = db.Column(db.Date)
    birth_place = db.Column(db.String(100))
    drivers_license = db.Column(db.String(50))
    cv_references = db.Column(db.JSON) # [{'name': '...', 'position': '...', 'phone': '...'}]
    
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
    def first_name(self):
        """Ad (full_name'den ayrıştırılmış)"""
        if not self.full_name:
            return ""
        return self.full_name.split()[0]

    @property
    def last_name(self):
        """Soyad (full_name'den ayrıştırılmış)"""
        if not self.full_name:
            return ""
        parts = self.full_name.split()
        if len(parts) > 1:
            return parts[-1]
        return ""

    def get_reset_token(self, expires_sec=1800):
        """Şifre sıfırlama tokeni oluştur"""
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token):
        """Şifre sıfırlama tokenini doğrula"""
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='password-reset-salt', max_age=1800)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_masked_name(self):
        """Geriye dönük uyumluluk için"""
        return self.masked_full_name

    def law_specialization_display(self):
        """Uzmanlık alanlarını göster"""
        if not self.specializations:
            return "Genel Hukuk"
        if isinstance(self.specializations, list):
            return ", ".join(self.specializations[:2])
        return str(self.specializations)

    @property
    def experience_years(self):
        """Tecrübe yılı (Şimdilik placeholder)"""
        return "5+ Yıl"

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
    title = db.Column(db.String(200), nullable=True)  # Artık otomatik oluşturuluyor
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # "boşanma", "miras", "ticaret"
    job_type = db.Column(db.String(50))  # "durusma", "kesif", "dosya_inceleme"
    
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
    price = db.Column(db.Float)  # Tek fiyat
    price_min = db.Column(db.Float)  # Eski uyumluluk için
    price_max = db.Column(db.Float)  # Eski uyumluluk için
    
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
        
        # Ensure expires_at is timezone-aware for comparison
        expires_at_aware = self.expires_at
        if expires_at_aware.tzinfo is None:
            expires_at_aware = expires_at_aware.replace(tzinfo=timezone.utc)
            
        return datetime.now(timezone.utc) > expires_at_aware
    
    @property
    def is_active(self):
        """İlan aktif mi?"""
        return self.status == 'active' and not self.is_expired
    
    def get_category_display(self):
        """Kategori adını döndür"""
        return self.category.title() if self.category else ""

    def get_job_type_display(self):
        """Görev türü adını döndür"""
        from constants import TASK_CATEGORY_DEFINITIONS
        if self.job_type and self.job_type in TASK_CATEGORY_DEFINITIONS:
            return TASK_CATEGORY_DEFINITIONS[self.job_type]['label']
        return self.job_type or ""

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
    job_post_id = db.Column(db.Integer, db.ForeignKey('job_posts.id'))
    office_post_id = db.Column(db.Integer, db.ForeignKey('office_posts.id'))
    
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
    job_post = db.relationship('JobPost', foreign_keys=[job_post_id])
    office_post = db.relationship('OfficePost', foreign_keys=[office_post_id])
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('user1_id', 'user2_id', 'post_id', 'job_post_id', 'office_post_id', name='unique_conversation_context'),
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
    def get_or_create(user1_id, user2_id, post_id=None, job_post_id=None, office_post_id=None):
        """Conversation bul veya oluştur"""
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
        
        conversation = Conversation.query.filter_by(
            user1_id=user1_id,
            user2_id=user2_id,
            post_id=post_id,
            job_post_id=job_post_id,
            office_post_id=office_post_id
        ).first()
        
        if not conversation:
            conversation = Conversation(
                user1_id=user1_id,
                user2_id=user2_id,
                post_id=post_id,
                job_post_id=job_post_id,
                office_post_id=office_post_id
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
    message_type = db.Column(db.String(20), default='text')  # text, file, image, audio, location
    
    # Dosya bilgisi
    file_name = db.Column(db.String(255))
    file_url = db.Column(db.String(500))
    file_type = db.Column(db.String(100))
    
    # Konum ve Ses
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    duration = db.Column(db.Integer) # Saniye cinsinden ses kaydı süresi
    
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
    related_job_post_id = db.Column(db.Integer, db.ForeignKey('job_posts.id'))
    related_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Durum
    read_at = db.Column(db.DateTime)
    action_url = db.Column(db.String(500))
    
    # Zaman Damgası
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # İlişkiler
    related_post = db.relationship('TevkilPost', foreign_keys=[related_post_id])
    related_job_post = db.relationship('JobPost', foreign_keys=[related_job_post_id])
    related_user = db.relationship('User', foreign_keys=[related_user_id])
    
    @property
    def is_read(self):
        return self.read_at is not None
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.type}>'


class JobPost(db.Model):
    """İş İlanı Modeli (Kariyer)"""
    __tablename__ = 'job_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # İlan Başlığı ve Açıklama
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Pozisyon Detayları
    position_type = db.Column(db.String(50), nullable=False)  # avukat, stajyer, katip, sekreter
    employment_type = db.Column(db.String(50), default='full_time')  # full_time, part_time, freelance
    
    # Konum
    city = db.Column(db.String(50))
    district = db.Column(db.String(50))
    office_name = db.Column(db.String(100))  # Ofis adı (Opsiyonel, kullanıcı adından farklı olabilir)
    
    # Maaş ve Yan Haklar
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    currency = db.Column(db.String(10), default='TRY')
    
    # Gereksinimler
    experience_years = db.Column(db.Integer)  # Tecrübe yılı
    requirements = db.Column(db.JSON)  # ["İngilizce", "Sürücü Belgesi"]
    
    # Durum
    is_active = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    
    # Zaman Damgaları
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime)
    
    # İlişkiler
    applications = db.relationship('JobApplication', backref='job_post', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='job_posts')
    
    def __repr__(self):
        return f'<JobPost {self.title}>'


class OfficePost(db.Model):
    """Ofis/Mobilya İlanı Modeli"""
    __tablename__ = 'office_posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # İlan Detayları
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # rent_office, rent_room, share_office, sell_furniture

    # Fiyat
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='TRY')

    # Konum
    city = db.Column(db.String(50))
    district = db.Column(db.String(50))
    address = db.Column(db.Text)
    
    # Konum (Harita)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # Özellikler
    square_meters = db.Column(db.Integer) # m2
    room_count = db.Column(db.String(20)) # 1+1, 2+1 etc or just number
    floor = db.Column(db.String(20))
    heating_type = db.Column(db.String(50))
    is_furnished = db.Column(db.Boolean, default=False)

    # Durum
    is_active = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)

    # Zaman
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # İlişkiler
    user = db.relationship('User', backref='office_posts')
    images = db.relationship('OfficePostImage', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<OfficePost {self.title}>'


class OfficePostImage(db.Model):
    """Ofis İlanı Resimleri"""
    __tablename__ = 'office_post_images'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('office_posts.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<OfficePostImage {self.id} for Post {self.post_id}>'


class JobApplication(db.Model):
    """İş Başvurusu Modeli"""
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('job_posts.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Başvuru Detayları
    message = db.Column(db.Text)
    cv_url = db.Column(db.String(500))  # CV dosyası linki
    
    # Durum
    status = db.Column(db.String(20), default='pending')  # pending, viewed, accepted, rejected
    
    # Zaman Damgaları
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # İlişkiler
    applicant = db.relationship('User', backref='job_applications')
    
    def __repr__(self):
        return f'<JobApplication {self.id} for Job {self.post_id}>'
