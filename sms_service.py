"""
Netgsm SMS Servisi
Tevkil platformu için SMS gönderim modülü
"""

import requests
import os
from datetime import datetime
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class NetgsmSMSService:
    """Netgsm SMS API wrapper"""
    
    def __init__(self):
        self.username = os.getenv('NETGSM_USERNAME')
        self.password = os.getenv('NETGSM_PASSWORD')
        self.sender = os.getenv('NETGSM_SENDER', 'TEVKIL')  # Başlık (max 11 karakter)
        self.api_url = 'https://api.netgsm.com.tr/sms/send/get'
        
        if not self.username or not self.password:
            logger.warning("⚠️ Netgsm credentials eksik! SMS gönderimi devre dışı.")
    
    def send_sms(self, phone: str, message: str) -> Dict:
        """
        Tekil SMS gönder
        
        Args:
            phone: Telefon numarası (5XXXXXXXXX formatında)
            message: Mesaj içeriği (max 917 karakter)
            
        Returns:
            dict: {'success': bool, 'message': str, 'code': str}
        """
        if not self.username or not self.password:
            return {
                'success': False,
                'message': 'Netgsm credentials tanımlı değil',
                'code': 'NO_CREDENTIALS'
            }
        
        # Telefon numarasını temizle (0 ile başlıyorsa kaldır)
        phone = phone.strip().replace(' ', '').replace('-', '')
        if phone.startswith('0'):
            phone = phone[1:]
        if phone.startswith('+90'):
            phone = phone[3:]
        if phone.startswith('90'):
            phone = phone[2:]
        
        # Netgsm API parametreleri
        params = {
            'usercode': self.username,
            'password': self.password,
            'gsmno': phone,
            'message': message,
            'msgheader': self.sender,
            'dil': 'TR'
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            result_code = response.text.split()[0]
            
            # Netgsm response kodları
            response_messages = {
                '00': 'SMS başarıyla gönderildi',
                '20': 'Mesaj metninde hata var',
                '30': 'Geçersiz kullanıcı adı/şifre',
                '40': 'Mesaj başlığı sistemde tanımlı değil',
                '50': 'Abone hesabında kredisi yok',
                '51': 'Abone hesap limitini aştı',
                '70': 'Hatalı sorgulama',
                '80': 'Gönderim sınırı aşıldı',
                '85': 'Mükerrer gönderim',
            }
            
            success = result_code == '00'
            message_text = response_messages.get(result_code, f'Bilinmeyen hata: {result_code}')
            
            if success:
                logger.info(f"✅ SMS gönderildi: {phone[:3]}***{phone[-2:]} - {message[:30]}...")
            else:
                logger.error(f"❌ SMS hatası: {message_text} (Kod: {result_code})")
            
            return {
                'success': success,
                'message': message_text,
                'code': result_code
            }
            
        except Exception as e:
            logger.error(f"❌ SMS API hatası: {str(e)}")
            return {
                'success': False,
                'message': f'API hatası: {str(e)}',
                'code': 'EXCEPTION'
            }
    
    def send_bulk_sms(self, phones: List[str], message: str) -> Dict:
        """
        Toplu SMS gönder
        
        Args:
            phones: Telefon numaraları listesi
            message: Mesaj içeriği
            
        Returns:
            dict: {'success': bool, 'sent_count': int, 'failed_count': int, 'results': list}
        """
        results = []
        sent_count = 0
        failed_count = 0
        
        for phone in phones:
            result = self.send_sms(phone, message)
            results.append({
                'phone': phone,
                'result': result
            })
            
            if result['success']:
                sent_count += 1
            else:
                failed_count += 1
        
        return {
            'success': sent_count > 0,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'results': results
        }
    
    # ============ TEVKIL PLATFORMU İÇİN ÖZELLEŞTİRİLMİŞ FONKSİYONLAR ============
    
    def send_new_post_notification(self, user_phone: str, post_title: str, city: str, 
                                   price: int, post_id: int) -> Dict:
        """
        Yeni ilan bildirimi gönder
        
        Args:
            user_phone: Kullanıcı telefonu
            post_title: İlan başlığı
            city: Şehir
            price: Fiyat
            post_id: İlan ID
        """
        message = (
            f"🔔 YENİ İLAN!\n"
            f"{post_title}\n"
            f"📍 {city}\n"
            f"💰 {price} TL\n"
            f"Detay: tevkil.app/ilan/{post_id}"
        )
        
        return self.send_sms(user_phone, message)
    
    def send_application_notification(self, owner_phone: str, applicant_name: str, 
                                      post_title: str, post_id: int) -> Dict:
        """
        İlan sahibine başvuru bildirimi gönder
        
        Args:
            owner_phone: İlan sahibi telefonu
            applicant_name: Başvuran ismi
            post_title: İlan başlığı
            post_id: İlan ID
        """
        message = (
            f"📩 YENİ BAŞVURU!\n"
            f"{applicant_name} başvurdu\n"
            f"İlan: {post_title}\n"
            f"Detay: tevkil.app/ilan/{post_id}"
        )
        
        return self.send_sms(owner_phone, message)
    
    def send_urgent_post_alert(self, user_phones: List[str], post_title: str, 
                              city: str, date: str, price: int, post_id: int) -> Dict:
        """
        Acil ilan uyarısı gönder (toplu)
        
        Args:
            user_phones: Kullanıcı telefonları listesi
            post_title: İlan başlığı
            city: Şehir
            date: Tarih
            price: Fiyat
            post_id: İlan ID
        """
        message = (
            f"🚨 ACİL İLAN!\n"
            f"{post_title}\n"
            f"📍 {city} | 📅 {date}\n"
            f"💰 {price} TL\n"
            f"Hemen başvur: tevkil.app/ilan/{post_id}"
        )
        
        return self.send_bulk_sms(user_phones, message)
    
    def send_low_application_reminder(self, owner_phone: str, post_title: str, 
                                     application_count: int, post_id: int) -> Dict:
        """
        Az başvurulu ilanlar için hatırlatma SMS'i
        
        Args:
            owner_phone: İlan sahibi telefonu
            post_title: İlan başlığı
            application_count: Başvuru sayısı
            post_id: İlan ID
        """
        message = (
            f"⚠️ İlanınıza {application_count} başvuru var\n"
            f"{post_title}\n"
            f"Ücreti artırmayı düşünebilirsiniz.\n"
            f"Düzenle: tevkil.app/ilan/{post_id}/edit"
        )
        
        return self.send_sms(owner_phone, message)
    
    def send_otp(self, phone: str, code: str) -> Dict:
        """
        2FA/OTP kodu gönder
        
        Args:
            phone: Telefon numarası
            code: 6 haneli kod
        """
        message = (
            f"Tevkil doğrulama kodunuz: {code}\n"
            f"Bu kodu kimseyle paylaşmayın.\n"
            f"Geçerlilik: 5 dakika"
        )
        
        return self.send_sms(phone, message)
    
    def send_application_accepted(self, applicant_phone: str, post_title: str, 
                                  owner_name: str, owner_phone: str) -> Dict:
        """
        Başvuru kabul bildirimi
        
        Args:
            applicant_phone: Başvuran telefonu
            post_title: İlan başlığı
            owner_name: İlan sahibi ismi
            owner_phone: İlan sahibi telefonu
        """
        message = (
            f"✅ BAŞVURUNUZ KABUL EDİLDİ!\n"
            f"{post_title}\n"
            f"İrtibat: {owner_name}\n"
            f"Tel: {owner_phone}"
        )
        
        return self.send_sms(applicant_phone, message)
    
    def send_application_rejected(self, applicant_phone: str, post_title: str) -> Dict:
        """
        Başvuru red bildirimi
        
        Args:
            applicant_phone: Başvuran telefonu
            post_title: İlan başlığı
        """
        message = (
            f"❌ Başvurunuz reddedildi\n"
            f"{post_title}\n"
            f"Diğer ilanları inceleyin: tevkil.app/ilanlar"
        )
        
        return self.send_sms(applicant_phone, message)


# Test fonksiyonu
def test_sms_service():
    """SMS servisini test et"""
    from dotenv import load_dotenv
    load_dotenv()
    
    sms = NetgsmSMSService()
    
    # Test numarası (kendi numaranı kullan)
    test_phone = "5XXXXXXXXX"  # Buraya gerçek numara gir
    
    print("\n📱 Netgsm SMS Servisi Test\n")
    
    # Test 1: Basit SMS
    print("Test 1: Basit SMS gönderimi...")
    result = sms.send_sms(test_phone, "Tevkil SMS servisi test mesajı!")
    print(f"Sonuç: {result}\n")
    
    # Test 2: Yeni ilan bildirimi
    print("Test 2: Yeni ilan bildirimi...")
    result = sms.send_new_post_notification(
        test_phone, 
        "İstanbul 3. Aile Mahkemesi Duruşma", 
        "İstanbul", 
        3000, 
        123
    )
    print(f"Sonuç: {result}\n")
    
    # Test 3: OTP kodu
    print("Test 3: OTP kodu gönderimi...")
    result = sms.send_otp(test_phone, "123456")
    print(f"Sonuç: {result}\n")


if __name__ == '__main__':
    test_sms_service()
