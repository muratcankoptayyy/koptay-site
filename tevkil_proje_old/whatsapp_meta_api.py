"""
Meta WhatsApp Cloud API Entegrasyonu
https://developers.facebook.com/docs/whatsapp/cloud-api
"""
import os
import requests
import json
from datetime import datetime
from flask import current_app
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class MetaWhatsAppAPI:
    """Meta WhatsApp Cloud API için wrapper class"""
    
    def __init__(self):
        """Meta API credentials'ları .env'den al"""
        self.phone_number_id = os.getenv('META_PHONE_NUMBER_ID')
        self.access_token = os.getenv('META_ACCESS_TOKEN')
        self.api_version = os.getenv('META_API_VERSION', 'v21.0')
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
    def send_message(self, to_phone, message_text):
        """
        WhatsApp mesajı gönder
        
        Args:
            to_phone (str): Alıcı telefon numarası (+905551234567)
            message_text (str): Mesaj içeriği
            
        Returns:
            dict: API response
        """
        if not self.phone_number_id or not self.access_token:
            raise ValueError("Meta API credentials eksik! .env dosyasını kontrol edin.")
        
        # Numara formatını düzelt (+ işareti varsa kaldır)
        to_phone = to_phone.replace('+', '').replace(' ', '')
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {
                "preview_url": True,
                "body": message_text
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ WhatsApp mesajı gönderildi: {to_phone}")
            return result
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Meta API Error: {e.response.text}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            print(f"❌ WhatsApp mesajı gönderilemedi: {str(e)}")
            raise
    
    def send_template_message(self, to_phone, template_name, language_code="tr", components=None):
        """
        Template mesajı gönder (önceden onaylanmış şablonlar için)
        
        Args:
            to_phone (str): Alıcı telefon numarası
            template_name (str): Template adı
            language_code (str): Dil kodu (tr, en, vb.)
            components (list): Template parametreleri
        """
        to_phone = to_phone.replace('+', '').replace(' ', '')
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Template mesajı gönderilemedi: {str(e)}")
            raise
    
    def verify_webhook(self, mode, token, challenge):
        """
        Webhook verification (Meta'nın webhook'u doğrulaması için)
        
        Args:
            mode (str): hub.mode
            token (str): hub.verify_token
            challenge (str): hub.challenge
            
        Returns:
            int: challenge (doğrulama başarılıysa)
        """
        verify_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'tevkil_webhook_2025')
        
        print(f"🔍 Webhook doğrulama:")
        print(f"  Mode: {mode}")
        print(f"  Token gelen: {token}")
        print(f"  Token beklenen: {verify_token}")
        print(f"  Challenge: {challenge}")
        
        if mode == "subscribe" and token == verify_token:
            print("✅ Webhook doğrulandı!")
            return int(challenge)  # Meta integer challenge bekliyor
        else:
            print(f"❌ Webhook doğrulama hatası! Token eşleşmiyor.")
            return None
    
    def parse_webhook_message(self, webhook_data):
        """
        Webhook'tan gelen mesajı parse et
        
        Args:
            webhook_data (dict): Webhook POST data
            
        Returns:
            dict: {sender_phone, message_text, message_id, timestamp}
        """
        try:
            # Meta webhook yapısı
            entry = webhook_data.get('entry', [])[0]
            changes = entry.get('changes', [])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [])
            
            if not messages:
                return None
            
            message = messages[0]
            
            # Mesaj bilgileri
            sender_phone = message.get('from')
            message_id = message.get('id')
            timestamp = message.get('timestamp')
            message_type = message.get('type')
            
            # Text mesajı al
            message_text = None
            if message_type == 'text':
                message_text = message.get('text', {}).get('body')
            elif message_type == 'audio':
                # Sesli mesaj - text olarak bilgi ver
                message_text = None  # Sesli mesajları şimdilik ignore
            elif message_type in ['image', 'video', 'document']:
                # Diğer medya tipleri
                message_text = None
            
            return {
                'sender_phone': sender_phone,
                'message_text': message_text,
                'message_id': message_id,
                'timestamp': timestamp,
                'type': message_type
            }
            
        except Exception as e:
            print(f"❌ Webhook mesajı parse edilemedi: {str(e)}")
            return None
    
    def mark_message_as_read(self, message_id):
        """Mesajı okundu olarak işaretle"""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Mesaj okundu işaretlenemedi: {str(e)}")
            return False


# Bildirim mesajları için helper fonksiyonlar
def send_new_application_notification(applicant_name, post_title, post_city, proposed_price, message, post_id, recipient_phone):
    """Yeni başvuru bildirimi gönder - Template kullanarak"""
    api = MetaWhatsAppAPI()
    
    print(f"🚀 Yeni başvuru bildirimi gönderiliyor...")
    print(f"📱 Alıcı: {recipient_phone}")
    print(f"👤 Başvuran: {applicant_name}")
    
    try:
        # Template mesaj gönder
        result = api.send_template_message(
            to_phone=recipient_phone,
            template_name="hello_world",
            language_code="en_US"
        )
        
        if result:
            print(f"✅ Bildirim template'i gönderildi!")
            
            # Detay mesajı dene (24 saat penceresi varsa çalışır)
            try:
                detail_message = f"""🔔 YENİ BAŞVURU

📋 İlan: {post_title}
👤 Başvuran: {applicant_name}
📍 Şehir: {post_city}
💰 Teklif: {proposed_price} TL

💬 Mesaj: {message}

🔗 https://tevkilagi.com/posts/{post_id}"""
                
                api.send_message(recipient_phone, detail_message)
                print(f"✅ Detay mesajı da gönderildi!")
            except:
                print(f"⚠️ Detay mesajı gönderilemedi (24 saat penceresi yok)")
        
        return result
    except Exception as e:
        print(f"❌ Bildirim gönderilemedi: {str(e)}")
        return None


def send_application_accepted_notification(post_title, owner_name, owner_phone, location, price, post_id, recipient_phone):
    """Başvuru kabul bildirimi gönder (başvurana) - Template kullanarak"""
    api = MetaWhatsAppAPI()
    
    print(f"🚀 Kabul bildirimi gönderiliyor...")
    print(f"📱 Alıcı: {recipient_phone}")
    
    try:
        # Template mesaj gönder
        result = api.send_template_message(
            to_phone=recipient_phone,
            template_name="hello_world",
            language_code="en_US"
        )
        
        if result:
            print(f"✅ Bildirim template'i gönderildi!")
            
            # Detay mesajı dene
            try:
                detail_message = f"""✅ BAŞVURU KABUL EDİLDİ

📋 İlan: {post_title}
👤 İlan Sahibi: {owner_name}
📞 İletişim: {owner_phone}
📍 Şehir: {location}
💰 Ücret: {price} TL

🔗 https://tevkilagi.com/posts/{post_id}"""
                
                api.send_message(recipient_phone, detail_message)
                print(f"✅ Detay mesajı da gönderildi!")
            except:
                print(f"⚠️ Detay mesajı gönderilemedi")
        
        return result
    except Exception as e:
        print(f"❌ Bildirim gönderilemedi: {str(e)}")
        return None


def send_acceptance_confirmation_to_owner(applicant_name, applicant_phone, price, post_title, recipient_phone):
    """Başvuru kabul onayı gönder (ilan sahibine) - Template kullanarak"""
    api = MetaWhatsAppAPI()
    
    print(f"🚀 Kabul onayı gönderiliyor (ilan sahibine)...")
    print(f"📱 Alıcı: {recipient_phone}")
    
    try:
        # Template mesaj gönder
        result = api.send_template_message(
            to_phone=recipient_phone,
            template_name="hello_world",
            language_code="en_US"
        )
        
        if result:
            print(f"✅ Bildirim template'i gönderildi!")
            
            # Detay mesajı dene
            try:
                detail_message = f"""✅ BAŞVURU KABUL ETTİNİZ

📋 İlan: {post_title}
👤 Avukat: {applicant_name}
📞 İletişim: {applicant_phone}
💰 Anlaşılan Ücret: {price} TL"""
                
                api.send_message(recipient_phone, detail_message)
                print(f"✅ Detay mesajı da gönderildi!")
            except:
                print(f"⚠️ Detay mesajı gönderilemedi")
        
        return result
    except Exception as e:
        print(f"❌ Bildirim gönderilemedi: {str(e)}")
        return None


def send_application_rejected_notification(post_title, location, recipient_phone):
    """Başvuru red bildirimi gönder - Template kullanarak"""
    api = MetaWhatsAppAPI()
    
    print(f"🚀 Red bildirimi gönderiliyor...")
    print(f"📱 Alıcı: {recipient_phone}")
    
    try:
        # Template mesaj gönder
        result = api.send_template_message(
            to_phone=recipient_phone,
            template_name="hello_world",
            language_code="en_US"
        )
        
        if result:
            print(f"✅ Bildirim template'i gönderildi!")
            
            # Detay mesajı dene
            try:
                detail_message = f"""❌ BAŞVURU REDDEDİLDİ

📋 İlan: {post_title}
📍 Şehir: {location}

Başka ilanlara başvurmaya devam edebilirsiniz.
🔗 https://tevkilagi.com/posts"""
                
                api.send_message(recipient_phone, detail_message)
                print(f"✅ Detay mesajı da gönderildi!")
            except:
                print(f"⚠️ Detay mesajı gönderilemedi")
        
        return result
    except Exception as e:
        print(f"❌ Bildirim gönderilemedi: {str(e)}")
        return None


def send_post_created_confirmation(post_title, post_id, recipient_phone):
    """İlan oluşturma onayı gönder - Template kullanarak"""
    api = MetaWhatsAppAPI()
    
    print(f"🚀 İlan onayı gönderiliyor...")
    print(f"📱 Alıcı: {recipient_phone}")
    print(f"📋 İlan: {post_title} (#{post_id})")
    
    try:
        # Şimdilik hello_world template'i kullan
        # Kendi template'iniz onaylandıktan sonra değiştirin
        result = api.send_template_message(
            to_phone=recipient_phone,
            template_name="hello_world",
            language_code="en_US"
        )
        
        if result:
            print(f"✅ Template mesajı gönderildi!")
            print(f"📱 Message ID: {result.get('messages', [{}])[0].get('id')}")
            
            # Ek bilgi için text mesaj dene (24 saat penceresi varsa çalışır)
            try:
                detail_message = f"""� İlan Detayları:

Başlık: {post_title}
İlan No: #{post_id}
Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}

🔗 https://tevkilagi.com/posts/{post_id}"""
                
                api.send_message(recipient_phone, detail_message)
                print(f"✅ Detay mesajı da gönderildi!")
            except:
                print(f"⚠️ Detay mesajı gönderilemedi (24 saat penceresi yok)")
        else:
            print(f"⚠️ Template mesajı gönderilemedi!")
        
        return result
    except Exception as e:
        print(f"❌ Bildirim gönderilemedi: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
