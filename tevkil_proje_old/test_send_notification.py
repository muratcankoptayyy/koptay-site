"""
WhatsApp Bildirim Testi
Template mesaj vs Normal mesaj karşılaştırması
"""
from whatsapp_meta_api import MetaWhatsAppAPI
from dotenv import load_dotenv

load_dotenv()

def test_template_message():
    """Template mesaj gönder (her zaman çalışır)"""
    api = MetaWhatsAppAPI()
    
    print("\n🧪 TEST 1: Template Mesaj (hello_world)")
    print("=" * 60)
    
    result = api.send_template_message(
        to_phone="905307111864",
        template_name="hello_world",
        language_code="en_US"
    )
    
    if result:
        print(f"✅ Template mesaj başarılı!")
        print(f"📱 Message ID: {result.get('messages', [{}])[0].get('id')}")
    else:
        print(f"❌ Template mesaj başarısız!")
    
    return result

def test_text_message():
    """Normal text mesaj gönder"""
    api = MetaWhatsAppAPI()
    
    print("\n🧪 TEST 2: Normal Text Mesaj")
    print("=" * 60)
    
    message = """✅ *TEST BİLDİRİMİ*

Bu bir test mesajıdır.

📱 Eğer bu mesajı görüyorsanız, sistem çalışıyor!"""
    
    result = api.send_message("905307111864", message)
    
    if result:
        print(f"✅ Text mesaj başarılı!")
        print(f"📱 Message ID: {result.get('messages', [{}])[0].get('id')}")
    else:
        print(f"❌ Text mesaj başarısız!")
    
    return result

if __name__ == "__main__":
    print("\n🚀 WhatsApp Bildirim Test Başlatılıyor...")
    print("=" * 60)
    
    # Test 1: Template mesaj (her zaman çalışmalı)
    template_result = test_template_message()
    
    # Test 2: Normal text mesaj
    text_result = test_text_message()
    
    print("\n📊 TEST SONUÇLARI")
    print("=" * 60)
    print(f"Template Mesaj: {'✅ Başarılı' if template_result else '❌ Başarısız'}")
    print(f"Text Mesaj: {'✅ Başarılı' if text_result else '❌ Başarısız'}")
    
    if template_result and not text_result:
        print("\n⚠️ SONUÇ: Template mesaj çalışıyor, text mesaj çalışmıyor.")
        print("Bu durum normal - Template mesaj kullanmalısınız!")
    elif template_result and text_result:
        print("\n✅ SONUÇ: Her iki mesaj tipi de çalışıyor!")
    else:
        print("\n❌ SONUÇ: Hiçbir mesaj çalışmıyor - Meta Business ayarlarını kontrol edin!")
    
    print("\n💡 NOT: Telefonunuzu kontrol edin, mesaj geldi mi?")
