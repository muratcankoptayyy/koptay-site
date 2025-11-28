"""
WhatsApp Bot - Tevkil Ağı
Gelen WhatsApp mesajlarını dinler ve otomatik ilan oluşturur
Meta WhatsApp Cloud API kullanır
"""
import re
import os
from datetime import datetime, timezone, timedelta
from app import app, db
from models import User, TevkilPost
from whatsapp_meta_api import (
    MetaWhatsAppAPI,
    send_post_created_confirmation
)

class WhatsAppBot:
    def __init__(self):
        self.api = MetaWhatsAppAPI()
        self.bot_number = os.getenv('META_PHONE_NUMBER_ID')
        self.message_format = """
📋 İLAN OLUŞTURMA FORMATI:
#ILAN
Başlık: [İlan başlığı]
Kategori: [Boşanma/Ceza/Ticaret/vb]
Şehir: [Şehir adı]
Açıklama: [Detaylı açıklama]
Fiyat: [Ücret tutarı]
Aciliyet: [Normal/Acil/Çok Acil]

📌 ÖRNEK:
#ILAN
Başlık: İstanbul Anadolu Adliyesi Duruşma Temsili
Kategori: Ceza Hukuku
Şehir: İstanbul
Açıklama: 15 Ocak tarihinde saat 10:00'da duruşma temsili gerekiyor
Fiyat: 2500
Aciliyet: Acil
        """
    
    def parse_message(self, message_text):
        """
        WhatsApp mesajını parse et ve ilan verisini çıkar
        """
        # #ILAN tag'i var mı kontrol et
        if not message_text.strip().startswith('#ILAN'):
            return None
        
        data = {}
        
        # Regex patterns
        patterns = {
            'title': r'Başlık:\s*(.+)',
            'category': r'Kategori:\s*(.+)',
            'city': r'Şehir:\s*(.+)',
            'description': r'Açıklama:\s*(.+)',
            'price': r'Fiyat:\s*(\d+)',
            'urgency': r'Aciliyet:\s*(.+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, message_text, re.IGNORECASE)
            if match:
                data[key] = match.group(1).strip()
        
        # Zorunlu alanlar kontrolü
        required_fields = ['title', 'category', 'city', 'description']
        if not all(field in data for field in required_fields):
            return None
        
        return data
    
    def map_urgency_level(self, urgency_text):
        """
        Aciliyet metnini system değerine çevir
        """
        urgency_map = {
            'çok acil': 'very_urgent',
            'acil': 'urgent',
            'normal': 'normal'
        }
        return urgency_map.get(urgency_text.lower(), 'normal')
    
    def create_post_from_whatsapp(self, user_phone, message_text):
        """
        WhatsApp mesajından ilan oluştur
        """
        with app.app_context():
            # Parse message
            data = self.parse_message(message_text)
            
            if not data:
                return False, "❌ Mesaj formatı hatalı. Lütfen doğru format ile tekrar deneyin."
            
            # Kullanıcıyı telefon numarasından bul
            user = User.query.filter_by(whatsapp_number=user_phone).first()
            
            if not user:
                return False, f"❌ Bu numara ({user_phone}) sistemde kayıtlı değil. Lütfen önce web sitesinden kayıt olun: https://utap.com.tr"
            
            # İlan oluştur
            try:
                post = TevkilPost(
                    user_id=user.id,
                    title=data['title'],
                    description=data['description'],
                    category=data['category'],
                    location=data['city'],
                    urgency_level=self.map_urgency_level(data.get('urgency', 'Normal')),
                    price_max=float(data.get('price', 0)) if data.get('price') else None,
                    status='active',
                    expires_at=datetime.now(timezone.utc) + timedelta(days=30)
                )
                
                db.session.add(post)
                db.session.commit()
                
                print(f"\n📱 WhatsApp bildirimi gönderiliyor...")
                print(f"Kullanıcı: {user.email}")
                print(f"Telefon: {user.whatsapp_number}")
                print(f"İlan: {post.title} (#{post.id})")
                
                # Meta API ile onay mesajı gönder
                result = send_post_created_confirmation(
                    post_title=post.title,
                    post_id=post.id,
                    recipient_phone=user.whatsapp_number
                )
                
                if result:
                    print(f"✅ WhatsApp bildirimi gönderildi!")
                else:
                    print(f"⚠️ WhatsApp bildirimi gönderilemedi!")
                
                success_message = f"""✅ İlan başarıyla oluşturuldu!
                
İlan No: #{post.id}
Başlık: {post.title}
Kategori: {post.category}
Şehir: {post.location}

Başvurular geldiğinde WhatsApp'tan bildirim alacaksınız."""
                
                return True, success_message
                
            except Exception as e:
                print(f"❌ İlan oluşturma hatası: {str(e)}")
                import traceback
                traceback.print_exc()
                return False, f"❌ İlan oluşturulurken hata: {str(e)}"
    
    def send_whatsapp_message(self, phone_number, message):
        """
        Meta WhatsApp Cloud API ile mesaj gönder
        """
        try:
            result = self.api.send_message(phone_number, message)
            return True
        except Exception as e:
            print(f"WhatsApp mesajı gönderilemedi: {str(e)}")
            return False
    
    def send_format_info(self, phone_number):
        """
        Format bilgisini kullanıcıya gönder
        """
        return self.send_whatsapp_message(phone_number, self.message_format)
    
    def process_incoming_message(self, sender_phone, message_text):
        """
        Gelen WhatsApp mesajını işle
        """
        # Eğer #ILAN ile başlıyorsa ilan oluştur
        if message_text.strip().startswith('#ILAN'):
            success, response_message = self.create_post_from_whatsapp(sender_phone, message_text)
            self.send_whatsapp_message(sender_phone, response_message)
            return success
        
        # Eğer #FORMAT veya #YARDIM yazarsa format bilgisi gönder
        elif message_text.strip().upper() in ['#FORMAT', '#YARDIM', '#HELP']:
            self.send_format_info(sender_phone)
            return True
        
        # Diğer mesajlar için yardım mesajı
        else:
            help_message = """
👋 Merhaba! Tevkil Ağı WhatsApp Bot'a hoş geldiniz!

📝 İlan oluşturmak için #ILAN ile başlayan bir mesaj gönderin.
ℹ️ Format bilgisi için #FORMAT yazın.

Örnek kullanım için #FORMAT yazabilirsiniz.
            """
            self.send_whatsapp_message(sender_phone, help_message)
            return False


# Bot instance
bot = WhatsAppBot()


# Test fonksiyonu
def test_bot():
    """Bot'u test et"""
    test_message = """
#ILAN
Başlık: Ankara Adliyesi Duruşma Temsili
Kategori: Ceza Hukuku
Şehir: Ankara
Açıklama: 20 Ocak 2025 tarihinde saat 14:00'da duruşma temsili gerekiyor. CMK kapsamında dosya.
Fiyat: 3000
Aciliyet: Acil
    """
    
    # Parse test
    data = bot.parse_message(test_message)
    print("Parse edilen veri:")
    print(data)
    
    # İlan oluşturma testi
    # success, message = bot.create_post_from_whatsapp("+905xxxxxxxxx", test_message)
    # print(message)


if __name__ == "__main__":
    test_bot()

