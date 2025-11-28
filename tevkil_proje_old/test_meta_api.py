"""
Meta WhatsApp API Test Script
Test eder: API connection, mesaj gönderme
"""
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Meta API'yi import et
from whatsapp_meta_api import MetaWhatsAppAPI

def test_meta_api():
    """Meta API'yi test et"""
    
    print("=" * 50)
    print("META WHATSAPP API TEST")
    print("=" * 50)
    
    # Credentials kontrolü
    print("\n1️⃣ Credentials Kontrolü:")
    access_token = os.getenv('META_ACCESS_TOKEN')
    phone_number_id = os.getenv('META_PHONE_NUMBER_ID')
    
    if access_token and phone_number_id:
        print(f"✅ Access Token: {access_token[:20]}...")
        print(f"✅ Phone Number ID: {phone_number_id}")
    else:
        print("❌ Credentials eksik! .env dosyasını kontrol edin.")
        return
    
    # API instance oluştur
    print("\n2️⃣ API Instance Oluşturma:")
    try:
        api = MetaWhatsAppAPI()
        print("✅ MetaWhatsAppAPI instance oluşturuldu")
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return
    
    # Test mesajı gönder (kendi numarana)
    print("\n3️⃣ Test Mesajı Gönderme:")
    test_phone = input("Test için telefon numaranı gir (örn: 905551234567): ")
    
    if not test_phone:
        print("❌ Telefon numarası girilmedi!")
        return
    
    test_message = """🎉 META WHATSAPP API TEST

Bu bir test mesajıdır!

✅ Sistem çalışıyor
✅ Mesaj gönderme başarılı
✅ Tevkil Ağı WhatsApp Bot hazır!

Şimdi #ILAN ile ilan oluşturabilirsiniz."""
    
    try:
        print(f"📤 Mesaj gönderiliyor: {test_phone}")
        result = api.send_message(test_phone, test_message)
        print(f"✅ Mesaj başarıyla gönderildi!")
        print(f"📊 Response: {result}")
    except Exception as e:
        print(f"❌ Mesaj gönderilemedi: {str(e)}")
        print("\nOlası Sebepler:")
        print("- Access token geçersiz olabilir (24 saat geçerli)")
        print("- Phone number ID yanlış olabilir")
        print("- Test telefon numarası WhatsApp Business'a kayıtlı değil")
        print("- Meta Business hesabında kısıtlama olabilir")
        return
    
    print("\n" + "=" * 50)
    print("TEST TAMAMLANDI! ✅")
    print("=" * 50)
    print("\nBir sonraki adım:")
    print("1. WhatsApp'ı aç ve test mesajını kontrol et")
    print("2. Webhook'u ayarla (META_SETUP_GUIDE.md Adım 5)")
    print("3. Web sitesinden test et: http://localhost:5000/whatsapp-ilan")

if __name__ == "__main__":
    test_meta_api()
