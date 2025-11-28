"""
🔒 Input Validation & Sanitization
===================================
Protect against XSS, SQL injection, and malicious input
"""

import re
import bleach
from wtforms import validators
from werkzeug.utils import secure_filename as werkzeug_secure_filename

# ============================================================================
# XSS PROTECTION - HTML Sanitization
# ============================================================================

# Allowed HTML tags for rich text (e.g., post descriptions)
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre', 'ul', 'ol', 'li', 'a'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'img': ['src', 'alt', 'title'],
}


def sanitize_html(text, allowed_tags=None, allowed_attributes=None):
    """
    HTML içeriğini temizle - XSS saldırılarını engelle
    
    Args:
        text: Temizlenecek HTML metni
        allowed_tags: İzin verilen HTML etiketleri (None = sadece metin)
        allowed_attributes: İzin verilen HTML özellikleri
    
    Returns:
        Temizlenmiş metin
    """
    if not text:
        return ""
    
    if allowed_tags is None:
        # Sadece düz metin - tüm HTML etiketlerini kaldır
        return bleach.clean(text, tags=[], attributes={}, strip=True)
    
    # Belirli HTML etiketlerine izin ver
    if allowed_attributes is None:
        allowed_attributes = ALLOWED_ATTRIBUTES
    
    return bleach.clean(
        text,
        tags=allowed_tags or ALLOWED_TAGS,
        attributes=allowed_attributes,
        strip=True
    )


def sanitize_plain_text(text):
    """
    Düz metin - Tüm HTML etiketlerini kaldır
    Kullanıcı adı, email, telefon gibi alanlar için
    """
    if not text:
        return ""
    return bleach.clean(str(text), tags=[], attributes={}, strip=True)


def sanitize_rich_text(text):
    """
    Zengin metin - Belirli HTML etiketlerine izin ver
    İlan açıklamaları, mesajlar için
    """
    return sanitize_html(text, allowed_tags=ALLOWED_TAGS, allowed_attributes=ALLOWED_ATTRIBUTES)


# ============================================================================
# INPUT VALIDATION - Format Checks
# ============================================================================

def validate_email(email):
    """
    Email format doğrulama
    Returns: (is_valid, sanitized_email)
    """
    if not email:
        return False, ""
    
    # Temizle
    email = sanitize_plain_text(email.strip().lower())
    
    # Email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, email
    
    return True, email


def validate_phone(phone):
    """
    Telefon numarası doğrulama (Türkiye)
    Format: 05XXXXXXXXX veya +905XXXXXXXXX
    Returns: (is_valid, sanitized_phone)
    """
    if not phone:
        return False, ""
    
    # Temizle ve sadece rakamları al
    phone = re.sub(r'[^0-9+]', '', str(phone))
    
    # Türkiye formatı kontrolü
    patterns = [
        r'^05[0-9]{9}$',  # 05XXXXXXXXX
        r'^\+905[0-9]{9}$',  # +905XXXXXXXXX
        r'^905[0-9]{9}$',  # 905XXXXXXXXX
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone):
            # Standart formata çevir: 05XXXXXXXXX
            if phone.startswith('+90'):
                phone = '0' + phone[3:]
            elif phone.startswith('90'):
                phone = '0' + phone[2:]
            return True, phone
    
    return False, phone


def validate_url(url):
    """
    URL doğrulama
    Returns: (is_valid, sanitized_url)
    """
    if not url:
        return False, ""
    
    url = url.strip()
    
    # URL regex (http:// veya https://)
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    if not re.match(pattern, url):
        return False, url
    
    return True, url


def validate_tc_kimlik(tc):
    """
    TC Kimlik No doğrulama
    Returns: (is_valid, sanitized_tc)
    """
    if not tc:
        return False, ""
    
    # Sadece rakamları al
    tc = re.sub(r'[^0-9]', '', str(tc))
    
    # 11 haneli olmalı
    if len(tc) != 11:
        return False, tc
    
    # İlk hane 0 olamaz
    if tc[0] == '0':
        return False, tc
    
    # TC Kimlik algoritması
    try:
        digits = [int(d) for d in tc]
        
        # 10. hane kontrolü
        sum_odd = sum(digits[0:9:2])
        sum_even = sum(digits[1:9:2])
        check_10 = (sum_odd * 7 - sum_even) % 10
        if digits[9] != check_10:
            return False, tc
        
        # 11. hane kontrolü
        check_11 = sum(digits[0:10]) % 10
        if digits[10] != check_11:
            return False, tc
        
        return True, tc
    except:
        return False, tc


def validate_baro_number(baro_no):
    """
    Baro sicil numarası doğrulama
    Returns: (is_valid, sanitized_baro_no)
    """
    if not baro_no:
        return False, ""
    
    # Sadece rakam ve harf
    baro_no = re.sub(r'[^0-9A-Za-z]', '', str(baro_no).upper())
    
    # En az 4 karakter olmalı
    if len(baro_no) < 4:
        return False, baro_no
    
    return True, baro_no


# ============================================================================
# FILE UPLOAD VALIDATION
# ============================================================================

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_file_upload(file, allowed_extensions=None, max_size=MAX_FILE_SIZE):
    """
    Dosya yükleme doğrulaması
    
    Args:
        file: Werkzeug FileStorage object
        allowed_extensions: İzin verilen dosya uzantıları
        max_size: Maximum dosya boyutu (bytes)
    
    Returns:
        (is_valid, error_message, safe_filename)
    """
    if not file or not file.filename:
        return False, "Dosya seçilmedi", ""
    
    # Güvenli dosya adı
    filename = werkzeug_secure_filename(file.filename)
    
    # Uzantı kontrolü
    if '.' not in filename:
        return False, "Dosya uzantısı bulunamadı", filename
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_IMAGE_EXTENSIONS
    
    if ext not in allowed_extensions:
        return False, f"İzin verilen formatlar: {', '.join(allowed_extensions)}", filename
    
    # Dosya boyutu kontrolü
    file.seek(0, 2)  # Dosya sonuna git
    file_size = file.tell()
    file.seek(0)  # Başa dön
    
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        return False, f"Dosya boyutu en fazla {max_mb:.1f}MB olmalıdır", filename
    
    # MIME type kontrolü (double extension attacks için)
    if file.content_type and not file.content_type.startswith(('image/', 'application/pdf', 'application/msword', 'text/')):
        return False, "Geçersiz dosya tipi", filename
    
    return True, "", filename


def validate_image_upload(file):
    """Sadece resim dosyaları için"""
    return validate_file_upload(file, ALLOWED_IMAGE_EXTENSIONS, 2 * 1024 * 1024)  # 2MB


def validate_document_upload(file):
    """Sadece doküman dosyaları için"""
    return validate_file_upload(file, ALLOWED_DOCUMENT_EXTENSIONS, 5 * 1024 * 1024)  # 5MB


# ============================================================================
# SQL INJECTION PROTECTION (Info Only - SQLAlchemy handles this)
# ============================================================================

def sanitize_sql_input(text):
    """
    SQL injection koruması - Bilgilendirme amaçlı
    
    Not: SQLAlchemy ORM kullanıyorsanız buna ihtiyacınız YOK!
    ORM otomatik olarak parametreli sorgular kullanır.
    
    Bu fonksiyon sadece raw SQL kullanmanız durumunda gerekli.
    """
    # SQLAlchemy kullanıyoruz, bu fonksiyona gerek yok
    # Ancak eğer raw SQL kullanacaksanız:
    # KULLANMAYIN: f"SELECT * FROM users WHERE email = '{email}'"
    # KULLANIN: session.execute("SELECT * FROM users WHERE email = :email", {"email": email})
    
    return text


# ============================================================================
# WTForms Validators (Form validation için)
# ============================================================================

class TurkishPhoneValidator:
    """WTForms için Türk telefon numarası validator"""
    def __init__(self, message=None):
        self.message = message or 'Geçerli bir telefon numarası girin (05XXXXXXXXX)'
    
    def __call__(self, form, field):
        is_valid, _ = validate_phone(field.data)
        if not is_valid:
            raise validators.ValidationError(self.message)


class TCKimlikValidator:
    """WTForms için TC Kimlik validator"""
    def __init__(self, message=None):
        self.message = message or 'Geçerli bir TC Kimlik numarası girin'
    
    def __call__(self, form, field):
        is_valid, _ = validate_tc_kimlik(field.data)
        if not is_valid:
            raise validators.ValidationError(self.message)


class BaroNumberValidator:
    """WTForms için Baro sicil numarası validator"""
    def __init__(self, message=None):
        self.message = message or 'Geçerli bir baro sicil numarası girin'
    
    def __call__(self, form, field):
        is_valid, _ = validate_baro_number(field.data)
        if not is_valid:
            raise validators.ValidationError(self.message)

