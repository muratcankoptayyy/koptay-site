"""
Spam Tespiti ve Önleme Sistemi
Uygunsuz içerikleri otomatik tespit eder
"""
import re
from datetime import datetime, timedelta

# Spam anahtar kelimeleri (Türkçe)
SPAM_KEYWORDS = [
    # Dolandırıcılık
    'garanti', 'kesin kazanç', 'bedava', 'ücretsiz', 'tıkla', 'klik',
    'para kazan', 'kolay para', 'hızlı zengin', 'kazanç garantili',
    
    # Cinsel içerik
    'seks', 'sex', 'escort', 'masaj', 'randevu',
    
    # Kumar/Bahis
    'bahis', 'casino', 'kumar', 'şans oyunu', 'slot',
    
    # Sahtecilik
    'diploma', 'sertifika sat', 'fake', 'sahte belge',
    
    # Agresif satış
    'hemen al', 'son fırsat', 'kaçırma', 'sınırlı sayıda',
    'bugün başla', 'şimdi kaydol'
]

# Uygunsız kelimeler
INAPPROPRIATE_WORDS = [
    'aptal', 'ahmak', 'salak', 'geri zekalı', 'mal', 'gerizekalı',
    # Daha fazla eklenebilir
]

def is_spam(text):
    """
    Metni spam olup olmadığını kontrol et
    
    Args:
        text: Kontrol edilecek metin
        
    Returns:
        bool: Spam ise True, değilse False
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    # 1. SPAM KELİME SAYISI
    spam_count = sum(1 for keyword in SPAM_KEYWORDS if keyword in text_lower)
    
    # 2. URL SAYISI (çok fazla link spam olabilir)
    url_count = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))
    
    # 3. TEKRARLAYAN KARAKTERLER (!!!! veya ???? spam)
    repeated_chars = len(re.findall(r'(.)\1{4,}', text))
    
    # 4. BÜYÜK HARF KULLANIMI (%80'den fazlası büyük harf)
    if len(text) > 10:
        uppercase_ratio = sum(1 for c in text if c.isupper()) / len(text)
        excessive_caps = uppercase_ratio > 0.8
    else:
        excessive_caps = False
    
    # 5. TELEFON NUMARASI/E-POSTA SAYISI (açıklamada çok fazla olabilir)
    phone_count = len(re.findall(r'0[0-9]{10}|\\+90[0-9]{10}', text))
    email_count = len(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}', text))
    
    # SPAM SKORU HESAPLA
    spam_score = (
        spam_count * 3 +           # Her spam kelime 3 puan
        url_count * 5 +             # Her URL 5 puan
        repeated_chars * 4 +        # Her tekrar 4 puan
        (10 if excessive_caps else 0) +  # Fazla büyük harf 10 puan
        phone_count * 2 +           # Her telefon 2 puan
        email_count * 2             # Her e-posta 2 puan
    )
    
    # Eşik değer: 15 ve üzeri spam
    return spam_score >= 15

def is_inappropriate(text):
    """
    Metinde uygunsuz kelime var mı kontrol et
    
    Args:
        text: Kontrol edilecek metin
        
    Returns:
        bool: Uygunsuz ise True, değilse False
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Uygunsuz kelime sayısı
    inappropriate_count = sum(1 for word in INAPPROPRIATE_WORDS if word in text_lower)
    
    return inappropriate_count > 0

def check_flood(user_id, db_session, action_type='post', max_count=5, time_window_minutes=60):
    """
    Kullanıcının belirli sürede fazla işlem yapıp yapmadığını kontrol et (flood)
    
    Args:
        user_id: Kullanıcı ID
        db_session: Database session
        action_type: İşlem tipi ('post', 'application', 'message')
        max_count: İzin verilen maksimum işlem sayısı
        time_window_minutes: Zaman penceresi (dakika)
        
    Returns:
        bool: Flood varsa True, yoksa False
    """
    from models import TevkilPost, Application, Message
    from datetime import datetime, timedelta, timezone
    
    time_threshold = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
    
    if action_type == 'post':
        count = TevkilPost.query.filter(
            TevkilPost.user_id == user_id,
            TevkilPost.created_at >= time_threshold
        ).count()
    elif action_type == 'application':
        count = Application.query.filter(
            Application.applicant_id == user_id,
            Application.created_at >= time_threshold
        ).count()
    elif action_type == 'message':
        count = Message.query.filter(
            Message.sender_id == user_id,
            Message.sent_at >= time_threshold
        ).count()
    else:
        return False
    
    return count >= max_count

def sanitize_text(text, max_length=5000):
    """
    Metni temizle ve güvenli hale getir
    
    Args:
        text: Temizlenecek metin
        max_length: Maksimum uzunluk
        
    Returns:
        str: Temizlenmiş metin
    """
    if not text:
        return ''
    
    # 1. HTML tag'lerini temizle
    text = re.sub(r'<[^>]+>', '', text)
    
    # 2. Script tag'lerini temizle
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # 3. Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 4. Maksimum uzunluk kontrolü
    if len(text) > max_length:
        text = text[:max_length]
    
    return text

def get_spam_report(text):
    """
    Detaylı spam raporu al (debug için)
    
    Args:
        text: Analiz edilecek metin
        
    Returns:
        dict: Spam analiz raporu
    """
    if not text:
        return {'is_spam': False, 'score': 0}
    
    text_lower = text.lower()
    
    spam_count = sum(1 for keyword in SPAM_KEYWORDS if keyword in text_lower)
    url_count = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))
    repeated_chars = len(re.findall(r'(.)\1{4,}', text))
    
    if len(text) > 10:
        uppercase_ratio = sum(1 for c in text if c.isupper()) / len(text)
    else:
        uppercase_ratio = 0
    
    spam_score = spam_count * 3 + url_count * 5 + repeated_chars * 4 + (10 if uppercase_ratio > 0.8 else 0)
    
    return {
        'is_spam': spam_score >= 15,
        'score': spam_score,
        'details': {
            'spam_keywords': spam_count,
            'urls': url_count,
            'repeated_chars': repeated_chars,
            'uppercase_ratio': round(uppercase_ratio, 2)
        }
    }
