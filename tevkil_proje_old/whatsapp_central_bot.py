"""
Merkezi WhatsApp Bot - Ulusal Tevkil Ağı Projesi
Tek numara üzerinden tüm avukatlar için hizmet verir

Özellikler:
- Tek WhatsApp numarası (Ulusal Tevkil Ağı resmi numarası)
- Kullanıcı telefon numarasından kimlik doğrulama
- Otomatik ilan oluşturma (#ILAN komutu)
- AI ile doğal dil ilan parse (GitHub Models GPT-4o)
- Başvuru bildirimleri
- Durum sorgulama (#DURUM komutu)
- Yardım menüsü (#YARDIM komutu)
"""
import re
import os
from datetime import datetime, timezone, timedelta
from app import app, db
from models import User, TevkilPost, Application
from whatsapp_meta_api import MetaWhatsAppAPI

# AI parser (GitHub Models veya Gemini)
AI_AVAILABLE = False
ai_parser = None

try:
    from github_models_parser import GitHubModelsParser
    ai_parser = GitHubModelsParser()
    AI_AVAILABLE = True
    print("✅ GitHub Models AI parser aktif!")
except Exception as e:
    print(f"⚠️ GitHub Models yüklenemedi: {e}")
    try:
        from gemini_ai_parser import GeminiIlanParser
        ai_parser = GeminiIlanParser()
        AI_AVAILABLE = True
        print("✅ Gemini AI parser aktif (fallback)")
    except:
        print("⚠️ AI parser kullanılamıyor - sadece #ILAN komutu çalışacak")

class CentralWhatsAppBot:
    """
    Merkezi WhatsApp Bot
    Tüm avukatlar için tek numaradan hizmet verir
    """
    
    def __init__(self):
        self.api = MetaWhatsAppAPI()
        self.commands = {
            '#ILAN': self.create_post,
            '#YARDIM': self.send_help,
            '#HELP': self.send_help,
            '#DURUM': self.check_status,
            '#ILANLARIM': self.list_my_posts,
            '#BASVURULARIM': self.list_my_applications,
            '#ONAYLA': self.confirm_ai_post,  # YENİ: AI ilanını onayla
            '#IPTAL': self.cancel_ai_post,     # YENİ: AI ilanını iptal et
        }
        
        # AI parser'ı başlat (global değişkenden)
        self.ai_parser = ai_parser
        if AI_AVAILABLE:
            print("✅ AI parser aktif - doğal dil ilanları destekleniyor")
        else:
            print("⚠️ AI parser yok - sadece #ILAN komutu çalışacak")
        
        # Onay bekleyen AI ilanları (geçici depolama)
        # Format: {phone_number: {parsed_data, timestamp}}
        self.pending_ai_posts = {}
        
        # Mesaj cache - duplicate önleme
        # Format: {message_id: timestamp}
        self.processed_messages = {}
        self.message_cache_duration = 300  # 5 dakika
    
    def find_user_by_phone(self, phone_number):
        """
        Telefon numarasından kullanıcıyı bul
        
        Args:
            phone_number (str): WhatsApp numarası (905551234567 formatında)
        
        Returns:
            User: Kullanıcı nesnesi veya None
        """
        with app.app_context():
            # Farklı formatlarda ara
            formats = [
                phone_number,
                f'+{phone_number}',
                phone_number.replace('+', ''),
                phone_number.replace(' ', ''),
            ]
            
            for fmt in formats:
                user = User.query.filter_by(phone=fmt).first()
                if user:
                    return user
                
                # whatsapp_number field'ında ara (eğer varsa)
                user = User.query.filter(
                    (User.phone == fmt) | 
                    (User.phone == f'+{fmt}') |
                    (User.phone == fmt.replace('+', ''))
                ).first()
                if user:
                    return user
            
            return None
    
    def request_ai_post_confirmation(self, user, sender_phone, ai_result, original_message):
        """
        AI'nin parse ettiği bilgileri kullanıcıya göster ve onay iste
        
        Args:
            user (User): Kullanıcı
            sender_phone (str): Telefon numarası
            ai_result (dict): AI'nin parse ettiği bilgiler
            original_message (str): Kullanıcının orijinal mesajı
        
        Returns:
            dict: Onay mesajı
        """
        # Onay bekleyen ilan olarak kaydet
        self.pending_ai_posts[sender_phone] = {
            'user_id': user.id,
            'ai_result': ai_result,
            'original_message': original_message,
            'timestamp': datetime.now(timezone.utc)
        }
        
        # Aciliyet tahmin et (varsayılan: Normal)
        urgency = "Normal"
        urgency_words = {
            'acil': 'Acil',
            'çok acil': 'Çok Acil',
            'bugün': 'Acil',
            'yarın': 'Normal',
            'hemen': 'Acil'
        }
        msg_lower = original_message.lower()
        for word, level in urgency_words.items():
            if word in msg_lower:
                urgency = level
                break
        
        # Kategori tahmin et (varsayılan: Genel Hukuk)
        category = "Genel Hukuk"
        category_keywords = {
            'aile': 'Aile Hukuku',
            'boşanma': 'Aile Hukuku',
            'ceza': 'Ceza Hukuku',
            'ağır ceza': 'Ceza Hukuku',
            'ticaret': 'Ticaret Hukuku',
            'icra': 'İcra ve İflas',
            'iş': 'İş Hukuku',
            'idare': 'İdare Hukuku',
        }
        for keyword, cat in category_keywords.items():
            if keyword in ai_result['courthouse'].lower() or keyword in msg_lower:
                category = cat
                break
        
        # Onay mesajı oluştur
        return {
            'success': True,
            'message': f"""🤖 *İLAN ÖNİZLEMESİ*

📋 *{ai_result['title']}*

🏛️ Mahkeme: {ai_result['courthouse']}
📍 Şehir: {ai_result['city']}
📂 Kategori: {category}
💰 Ücret: *{ai_result['price']} TL*
⚡ Aciliyet: {urgency}

_{ai_result['description']}_

─────────────────────
✅ *Onaylamak:* "Tamam" / "Evet" / "Paylaş"
🔧 *Düzeltmek:* "Şehir Ankara olsun"
❌ *İptal:* "Hayır" / "Vazgeç"

💡 Doğal yazın, AI anlıyor."""
        }
    
    def confirm_ai_post(self, user, message_text):
        """
        Onay bekleyen AI ilanını oluştur
        """
        with app.app_context():
            sender_phone = user.phone
            
            # Onay bekleyen ilan var mı?
            if sender_phone not in self.pending_ai_posts:
                return {
                    'success': False,
                    'message': """❌ Onay bekleyen ilan yok.

Yeni ilan oluşturmak için mesajınızı gönderin.

Örnek:
"Ankara 4. Asliye Ceza Mahkemesi'nde saat 10:00 duruşma, 2000 TL"

Yardım: #YARDIM"""
                }
            
            pending = self.pending_ai_posts[sender_phone]
            ai_result = pending['ai_result']
            
            # Zaman aşımı kontrolü (15 dakika)
            if (datetime.now(timezone.utc) - pending['timestamp']).seconds > 900:
                del self.pending_ai_posts[sender_phone]
                return {
                    'success': False,
                    'message': """⏰ Onay süresi doldu.

Lütfen ilanınızı yeniden gönderin."""
                }
            
            try:
                # Kategori ve aciliyet tahmin et
                category = "Genel Hukuk"
                urgency = "Normal"
                
                original_msg = pending['original_message'].lower()
                
                # Kategori
                if 'aile' in ai_result['courthouse'].lower() or 'boşanma' in original_msg:
                    category = 'Aile Hukuku'
                elif 'ceza' in ai_result['courthouse'].lower():
                    category = 'Ceza Hukuku'
                elif 'ticaret' in ai_result['courthouse'].lower():
                    category = 'Ticaret Hukuku'
                elif 'icra' in ai_result['courthouse'].lower():
                    category = 'İcra ve İflas'
                elif 'iş' in ai_result['courthouse'].lower():
                    category = 'İş Hukuku'
                elif 'idare' in ai_result['courthouse'].lower():
                    category = 'İdare Hukuku'
                
                # Aciliyet
                if 'acil' in original_msg or 'bugün' in original_msg or 'hemen' in original_msg:
                    urgency = 'Acil' if 'çok' not in original_msg else 'Çok Acil'
                elif 'yarın' in original_msg:
                    urgency = 'Normal'
                
                # İlan oluştur
                price_value = float(ai_result['price']) if ai_result['price'] else 0.0
                
                # Urgency seviyesini doğru formata çevir
                urgency_db_map = {
                    'Normal': 'normal',
                    'Acil': 'urgent',
                    'Çok Acil': 'very_urgent'
                }
                urgency_db = urgency_db_map.get(urgency, 'normal')
                
                post = TevkilPost(
                    user_id=user.id,
                    title=ai_result['title'][:100],
                    category=category,
                    location=ai_result['city'],
                    city=ai_result['city'],
                    courthouse=ai_result['courthouse'],
                    description=ai_result['description'],
                    price_min=price_value,
                    price_max=price_value,
                    urgency_level=urgency_db,
                    status='active',
                    created_at=datetime.now(timezone.utc)
                )
                
                db.session.add(post)
                db.session.commit()
                
                # Onay bekleyen ilanı sil
                del self.pending_ai_posts[sender_phone]
                
                print(f"✅ AI ilan onaylandı ve oluşturuldu: #{post.id} - {post.title}")
                
                # Urgency'yi Türkçe'ye çevir
                urgency_display = {
                    'normal': 'Normal',
                    'urgent': 'Acil', 
                    'very_urgent': 'Çok Acil'
                }.get(post.urgency_level, 'Normal')
                
                return {
                    'success': True,
                    'post_id': post.id,
                    'message': f"""✅ İLAN YAYINLANDI!

📋 {post.title}
🏛️ {post.courthouse}
📍 {post.location}
📂 {post.category}
💰 {post.price_min} TL
⚡ {urgency_display}

🔗 https://utap.com.tr/posts/{post.id}

✅ İlanınız aktif! Başvurular gelmeye başlayacak."""
                }
                
            except Exception as e:
                print(f"❌ İlan oluşturma hatası: {str(e)}")
                return {
                    'success': False,
                    'message': f"""❌ İlan oluşturulamadı.

Hata: {str(e)}

Lütfen #ILAN komutu ile manuel deneyin."""
                }
    
    def cancel_ai_post(self, user, message_text):
        """
        Onay bekleyen AI ilanını iptal et
        """
        sender_phone = user.phone
        
        if sender_phone in self.pending_ai_posts:
            del self.pending_ai_posts[sender_phone]
            return {
                'success': True,
                'message': """❌ İlan iptal edildi.

Yeni ilan oluşturmak için mesajınızı gönderin.

Yardım: #YARDIM"""
            }
        else:
            return {
                'success': False,
                'message': """❌ İptal edilecek ilan yok.

Yardım: #YARDIM"""
            }
    
    def correct_ai_post(self, user, message_text):
        """
        Onay bekleyen AI ilanını düzelt (doğal dil ile)
        
        Örnek: "Şehir İstanbul olmalı", "Ücret 3000 TL", "Mahkeme adı yanlış, Ankara 5. Asliye Ceza olacak"
        """
        sender_phone = user.phone
        
        if sender_phone not in self.pending_ai_posts:
            return {
                'success': False,
                'message': """❌ Düzeltilecek ilan yok.

Yeni ilan oluşturmak için mesajınızı gönderin."""
            }
        
        if not self.ai_parser:
            return {
                'success': False,
                'message': """❌ AI parser kullanılamıyor.

#IPTAL yazarak iptal edin veya #ONAYLA ile onaylayın."""
            }
        
        pending = self.pending_ai_posts[sender_phone]
        ai_result = pending['ai_result']
        
        # AI ile düzeltme yap
        correction_result = self.ai_parser.extract_correction_from_message(message_text, ai_result)
        
        if not correction_result['success']:
            return {
                'success': False,
                'message': f"""❓ Düzeltmeyi anlayamadım.

Lütfen daha açık yazın:
"Şehir İstanbul olmalı"
"Ücret 3000 TL"
"Mahkeme adı Ankara 5. Asliye Ceza olacak"

VEYA:
• Onaylamak için: "Tamam", "Evet", "Olur"
• İptal etmek için: "Vazgeç", "İptal", "Hayır"

Hata: {correction_result.get('error', 'Bilinmeyen hata')}"""
            }
        
        # Güncellenmiş bilgileri kaydet
        self.pending_ai_posts[sender_phone]['ai_result'] = {
            'title': correction_result['title'],
            'courthouse': correction_result['courthouse'],
            'city': correction_result['city'],
            'description': correction_result['description'],
            'price': correction_result['price']
        }
        
        # Aciliyet ve kategori tahmin et (yeniden)
        category = "Genel Hukuk"
        urgency = "Normal"
        
        courthouse_lower = correction_result['courthouse'].lower()
        if 'aile' in courthouse_lower:
            category = 'Aile Hukuku'
        elif 'ceza' in courthouse_lower:
            category = 'Ceza Hukuku'
        elif 'ticaret' in courthouse_lower:
            category = 'Ticaret Hukuku'
        elif 'icra' in courthouse_lower:
            category = 'İcra ve İflas'
        elif 'iş' in courthouse_lower:
            category = 'İş Hukuku'
        elif 'idare' in courthouse_lower:
            category = 'İdare Hukuku'
        
        original_msg = pending['original_message'].lower()
        if 'acil' in original_msg or 'bugün' in original_msg:
            urgency = 'Acil'
        
        # Güncellenmiş önizleme göster
        return {
            'success': True,
            'message': f"""✅ DÜZELTİLDİ: {correction_result['change_summary']}

🤖 YENİ ÖNİZLEME

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 BAŞLIK
{correction_result['title']}

🏛️ MAHKEME
{correction_result['courthouse']}

📍 ŞEHİR
{correction_result['city']}

📂 KATEGORİ
{category}

📝 AÇIKLAMA
{correction_result['description']}

💰 ÜCRET
{correction_result['price']} TL

⚡ ACİLİYET
{urgency}
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Şimdi doğru mu?

👍 ONAYLAMAK İÇİN:
"Tamam", "Evet", "Olur", "Paylaş"

❌ İPTAL İÇİN:
"Vazgeç", "İptal", "Hayır"

🔧 BAŞKA DÜZELTME:
"Ücret 4000 TL olmalı" gibi yazın"""
        }
    
    def register_user_from_whatsapp(self, phone_number, name):
        """
        WhatsApp'tan hızlı kullanıcı kaydı
        (Tam kayıt için web sitesine yönlendirilecek)
        """
        with app.app_context():
            # Basit kullanıcı oluştur
            from werkzeug.security import generate_password_hash
            import random
            
            temp_password = f"temp{random.randint(100000, 999999)}"
            
            user = User(
                email=f"whatsapp_{phone_number}@temp.utap.com.tr",
                password_hash=generate_password_hash(temp_password),
                full_name=name or "WhatsApp Kullanıcı",
                phone=phone_number,
                city="Belirtilmedi",
                lawyer_type="avukat",
                verified=False,  # Web'den tam kayıt yapana kadar False
                is_active=True
            )
            
            db.session.add(user)
            db.session.commit()
            
            return user, temp_password
    
    def parse_ilan_message(self, message_text):
        """
        #ILAN mesajını parse et
        
        Format:
        #ILAN
        Başlık: ...
        Kategori: ...
        Şehir: ...
        Açıklama: ...
        Fiyat: ...
        Aciliyet: Normal/Acil/Çok Acil
        """
        data = {}
        
        patterns = {
            'title': r'Başlık:\s*(.+?)(?:\n|$)',
            'category': r'Kategori:\s*(.+?)(?:\n|$)',
            'city': r'Şehir:\s*(.+?)(?:\n|$)',
            'description': r'Açıklama:\s*(.+?)(?:\n|$)',
            'price': r'(?:Fiyat|Ücret):\s*(\d+)',
            'urgency': r'Aciliyet:\s*(.+?)(?:\n|$)',
            'date': r'Tarih:\s*(.+?)(?:\n|$)',
            'time': r'Saat:\s*(.+?)(?:\n|$)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, message_text, re.IGNORECASE | re.MULTILINE)
            if match:
                data[key] = match.group(1).strip()
        
        return data
    
    def create_post(self, user, message_text):
        """İlan oluştur"""
        with app.app_context():
            data = self.parse_ilan_message(message_text)
            
            # Zorunlu alanlar kontrolü
            required = ['title', 'category', 'city', 'description']
            missing = [field for field in required if field not in data]
            
            if missing:
                return {
                    'success': False,
                    'message': f"""❌ Eksik bilgi!

Lütfen şu alanları ekleyin:
{', '.join(missing)}

Doğru format için #YARDIM yazın."""
                }
            
            # Aciliyet seviyesi
            urgency_map = {
                'çok acil': 'very_urgent',
                'acil': 'urgent',
                'normal': 'normal'
            }
            urgency = urgency_map.get(data.get('urgency', 'normal').lower(), 'normal')
            
            # İlan oluştur
            try:
                post = TevkilPost(
                    user_id=user.id,
                    title=data['title'],
                    description=data['description'],
                    category=data['category'],
                    location=data['city'],
                    urgency_level=urgency,
                    price_max=float(data['price']) if data.get('price') else None,
                    status='active',
                    expires_at=datetime.now(timezone.utc) + timedelta(days=30)
                )
                
                db.session.add(post)
                db.session.commit()
                
                return {
                    'success': True,
                    'message': f"""✅ İLAN OLUŞTURULDU!

📋 İlan No: #{post.id}
📌 Başlık: {post.title}
🏛 Kategori: {post.category}
📍 Şehir: {post.location}
{'💰 Ücret: ' + str(post.price_max) + ' TL' if post.price_max else ''}
⚡ Aciliyet: {data.get('urgency', 'Normal')}

Başvurular geldiğinde size WhatsApp'tan bildirim göndereceğiz!

İlanınızı görmek için:
🔗 https://utap.com.tr/posts/{post.id}"""
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'message': f"❌ Hata oluştu: {str(e)}\n\nLütfen tekrar deneyin veya #YARDIM yazın."
                }
    
    def list_my_posts(self, user, message_text):
        """Kullanıcının ilanlarını listele"""
        with app.app_context():
            posts = TevkilPost.query.filter_by(
                user_id=user.id,
                status='active'
            ).order_by(TevkilPost.created_at.desc()).limit(5).all()
            
            if not posts:
                return {
                    'success': True,
                    'message': """📋 AKTİF İLANINIZ YOK

İlan oluşturmak için:
#ILAN yazıp gerekli bilgileri ekleyin.

Format için #YARDIM yazın."""
                }
            
            message = "📋 AKTİF İLANLARINIZ:\n\n"
            
            for post in posts:
                # Başvuru sayısı
                app_count = Application.query.filter_by(post_id=post.id).count()
                
                message += f"""🔹 #{post.id} - {post.title}
📍 {post.location} | {post.category}
📊 {app_count} başvuru
🔗 https://utap.com.tr/posts/{post.id}

"""
            
            message += "\nDetaylar için web sitesine giriş yapın."
            
            return {
                'success': True,
                'message': message
            }
    
    def list_my_applications(self, user, message_text):
        """Kullanıcının başvurularını listele"""
        with app.app_context():
            applications = Application.query.filter_by(
                applicant_id=user.id
            ).order_by(Application.created_at.desc()).limit(5).all()
            
            if not applications:
                return {
                    'success': True,
                    'message': """📝 BAŞVURUNUZ YOK

İlanlara göz atmak için:
🔗 https://utap.com.tr/posts"""
                }
            
            message = "📝 BAŞVURULARINIZ:\n\n"
            
            for app in applications:
                status_emoji = {
                    'pending': '⏳',
                    'accepted': '✅',
                    'rejected': '❌'
                }
                
                message += f"""{status_emoji.get(app.status, '❓')} {app.post.title}
📍 {app.post.location}
💰 Teklifiniz: {app.proposed_price} TL
Durum: {app.status}

"""
            
            message += "\nDetaylar için web sitesine giriş yapın."
            
            return {
                'success': True,
                'message': message
            }
    
    def check_status(self, user, message_text):
        """Durum kontrolü"""
        with app.app_context():
            # Aktif ilanlar
            active_posts = TevkilPost.query.filter_by(
                user_id=user.id,
                status='active'
            ).count()
            
            # Bekleyen başvurular (kullanıcının ilanlarına gelenler)
            pending_applications_to_me = db.session.query(Application).join(TevkilPost).filter(
                TevkilPost.user_id == user.id,
                Application.status == 'pending'
            ).count()
            
            # Kullanıcının yaptığı başvurular
            my_applications = Application.query.filter_by(
                applicant_id=user.id
            ).count()
            
            return {
                'success': True,
                'message': f"""📊 HESAP DURUMUNUZ

👤 {user.full_name}
📞 {user.phone}

📋 Aktif İlanlarınız: {active_posts}
📥 Bekleyen Başvurular: {pending_applications_to_me}
📤 Yaptığınız Başvurular: {my_applications}

🔗 Detaylar: https://utap.com.tr/dashboard

Komutlar için #YARDIM yazın."""
            }
    
    def send_help(self, user, message_text):
        """Yardım menüsü"""
        
        ai_status = "✅ Aktif" if self.ai_parser else "❌ Kapalı"
        
        return {
            'success': True,
            'message': f"""📖 ULUSAL TEVKİL AĞI - YARDIM

━━━━━━━━━━━━━━━━━━━━━━━━━
� İLAN OLUŞTURMA (2 YOL):
━━━━━━━━━━━━━━━━━━━━━━━━━

💬 1) DOĞAL DİL (AI) {ai_status}
Direkt yazın:
"İstanbul 5. Aile Mahkemesi'nde yarın saat 10:00 duruşmam var, 3000 TL"

📋 2) ŞABLONLU
#ILAN
Başlık: Boşanma Davası  
Kategori: Aile Hukuku
Şehir: İstanbul
Açıklama: Yarın 10:00 duruşma
Fiyat: 3000

━━━━━━━━━━━━━━━━━━━━━━━━━
� DİĞER KOMUTLAR:
━━━━━━━━━━━━━━━━━━━━━━━━━

#ILANLARIM - Aktif ilanlarımı göster
#BASVURULARIM - Başvurularımı göster
#DURUM - Hesap durumumu göster
#YARDIM - Bu yardım menüsü

🌐 Web: https://utap.com.tr
📧 Destek: destek@utap.com.tr"""
        }
    
    def send_notification_new_application(self, post_owner, application):
        """Yeni başvuru bildirimi gönder (ilan sahibine)"""
        message = f"""🔔 YENİ BAŞVURU!

📋 İlanınız: {application.post.title}
👤 Başvuran: {application.applicant.full_name}
📍 Şehir: {application.applicant.city}
💰 Teklif: {application.proposed_price} TL

💬 Mesaj: {application.message}

Kabul/Red için:
🔗 https://utap.com.tr/posts/{application.post_id}

Başvuruyu kabul ettiğinizde başvuran avukata otomatik bildirim gönderilir."""
        
        try:
            self.api.send_message(post_owner.phone, message)
            return True
        except Exception as e:
            print(f"❌ Bildirim gönderilemedi: {e}")
            return False
    
    def send_notification_application_accepted(self, applicant, application):
        """Başvuru kabul bildirimi gönder (başvuran avukata)"""
        message = f"""✅ BAŞVURUNUZ KABUL EDİLDİ!

📋 İlan: {application.post.title}
👤 İlan Sahibi: {application.post.user.full_name}
📞 İletişim: {application.post.user.phone}
📍 Şehir: {application.post.location}
💰 Anlaşılan Ücret: {application.proposed_price} TL

Detaylar:
🔗 https://utap.com.tr/posts/{application.post_id}

İlan sahibi ile iletişime geçebilirsiniz."""
        
        try:
            self.api.send_message(applicant.phone, message)
            return True
        except Exception as e:
            print(f"❌ Bildirim gönderilemedi: {e}")
            return False
    
    def send_notification_application_rejected(self, applicant, application):
        """Başvuru red bildirimi gönder"""
        message = f"""❌ BAŞVURUNUZ REDDEDİLDİ

📋 İlan: {application.post.title}
📍 Şehir: {application.post.location}

Başka ilanlara göz atmaya devam edebilirsiniz:
🔗 https://utap.com.tr/posts"""
        
        try:
            self.api.send_message(applicant.phone, message)
            return True
        except Exception as e:
            print(f"❌ Bildirim gönderilemedi: {e}")
            return False
    
    def process_message(self, sender_phone, message_text):
        """
        Gelen WhatsApp mesajını işle
        
        Args:
            sender_phone (str): Gönderen telefon numarası
            message_text (str): Mesaj içeriği
        
        Returns:
            dict: {success: bool, message: str}
        """
        with app.app_context():
            # Kullanıcıyı bul
            user = self.find_user_by_phone(sender_phone)
            
            if not user:
                # Kullanıcı kayıtlı değil - kayıt ol mesajı
                return {
                    'success': False,
                    'message': f"""👋 Merhaba!

Bu numara ({sender_phone}) sistemimizde kayıtlı değil.

Ulusal Tevkil Ağı'na katılmak için:
🔗 https://utap.com.tr/register

Kayıt olduktan sonra bu numaradan ilan oluşturabilir, başvuru yapabilirsiniz!

❓ Sorularınız için: destek@utap.com.tr"""
                }
            
            # Mesajı temizle
            message_text = message_text.strip()
            
            # Önce onay bekleyen ilan var mı kontrol et
            if sender_phone in self.pending_ai_posts:
                # Kullanıcının niyetini AI ile algıla (doğal dil)
                if self.ai_parser:
                    intent_result = self.ai_parser.detect_user_intent(message_text)
                    
                    print(f"🤖 AI Intent Algıladı: '{intent_result['intent']}' (güven: {intent_result['confidence']:.2f})")
                    
                    # AI güvenli bir intent belirlediyse, uygula!
                    # Gemini çok iyi anlıyor, threshold'ları çok düşük tutuyoruz
                    if intent_result['intent'] == 'approve':
                        if intent_result['confidence'] > 0.5:
                            # Yüksek güven - direkt onayla
                            return self.confirm_ai_post(user, message_text)
                        else:
                            # Orta güven - yine de onayla ama bilgi ver
                            print(f"⚠️ Düşük güvenle onay algılandı: {intent_result['confidence']}")
                            return self.confirm_ai_post(user, message_text)
                    
                    elif intent_result['intent'] == 'reject':
                        if intent_result['confidence'] > 0.4:
                            return self.cancel_ai_post(user, message_text)
                    
                    elif intent_result['intent'] == 'correction':
                        if intent_result['confidence'] > 0.3:
                            return self.correct_ai_post(user, message_text)
                    
                    # Sadece çok belirsizse hata göster
                    else:
                        return {
                            'success': False,
                            'message': f"""❓ Mesajınızı tam anlayamadım.

Lütfen daha açık yazabilir misiniz?

✅ ONAYLAMAK İÇİN:
"Tamam", "Evet", "Olur", "Paylaş", "Gönder"

🔧 DÜZELTME İÇİN:
"Şehir İstanbul olmalı", "Ücret 4000 TL"

❌ İPTAL İÇİN:
"Vazgeç", "İptal", "Hayır"

[Debug: Intent={intent_result['intent']}, Güven={intent_result['confidence']:.2f}]"""
                        }
            
            # Komutu bul (eski sistem hala çalışıyor)
            command = None
            for cmd in self.commands.keys():
                if message_text.upper().startswith(cmd):
                    command = cmd
                    break
            
            if command:
                # Komutu çalıştır
                handler = self.commands[command]
                result = handler(user, message_text)
                return result
            else:
                # Komut yok - AI ile doğal dil parse deneyelim
                if self.ai_parser and self.ai_parser.is_ilan_message(message_text):
                    # Mesaj ilan gibi görünüyor, AI ile parse et
                    print(f"🤖 AI ile parse deneniyor: {message_text[:50]}...")
                    
                    ai_result = self.ai_parser.parse_natural_message(message_text)
                    
                    if ai_result['success']:
                        # AI başarıyla parse etti - ONAY İSTE (değişiklik burada!)
                        return self.request_ai_post_confirmation(user, sender_phone, ai_result, message_text)
                    else:
                        # AI parse edemedi, kullanıcıya bilgi ver
                        return {
                            'success': False,
                            'message': f"""❓ Mesajınızı anlayamadım.

Lütfen daha detaylı yazın:

✅ İyi Örnek:
"Ankara 4. Asliye Ceza Mahkemesi'nde saat 10:00'da duruşmam var, tevkil arıyorum, 2000 TL ücret"

VEYA şablonlu format:
#ILAN
Başlık: Ceza Davası
Şehir: Ankara
Mahkeme: Ankara 4. Asliye Ceza Mahkemesi
Açıklama: Saat 10:00 duruşma
Ücret: 2000

Detay: #YARDIM"""
                        }
                
                # Ne komut ne de ilan - yardım göster
                return {
                    'success': False,
                    'message': f"""❓ Anlamadım.

💡 İlan oluşturmak için:
• Doğal dil: "Ankara 2. Ağır Ceza'da yarın duruşmam var, tevkil lazım"
• Komut: #ILAN ile şablonlu format

📋 Diğer komutlar:
• #ILANLARIM - İlanlarımı göster
• #BASVURULARIM - Başvurularımı göster
• #DURUM - Hesap durumu
• #YARDIM - Detaylı yardım

Detaylı bilgi için #YARDIM yazın."""
                }


# Global bot instance
central_bot = CentralWhatsAppBot()


# Test fonksiyonu
def test_central_bot():
    """Bot'u test et"""
    
    # Test 1: Yardım
    print("=== TEST 1: YARDIM ===")
    result = central_bot.process_message("+905551234567", "#YARDIM")
    print(result['message'])
    
    # Test 2: İlan oluşturma
    print("\n=== TEST 2: ILAN OLUŞTURMA ===")
    test_message = """#ILAN
Başlık: Test Duruşma Ankara
Kategori: Ceza Hukuku
Şehir: Ankara
Açıklama: Test amaçlı ilan
Fiyat: 2500
Aciliyet: Normal"""
    
    result = central_bot.process_message("+905551234567", test_message)
    print(result['message'])


if __name__ == "__main__":
    test_central_bot()
