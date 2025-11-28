"""
WhatsApp Credentials Kurulum Script
Bu script size adım adım credentials girmenizi sağlar
"""
import os
from pathlib import Path

def create_env_file():
    """
    .env dosyası oluştur ve credentials al
    """
    print("=" * 60)
    print("🚀 ULUSAL TEVKİL AĞI - WHATSAPP API KURULUMU")
    print("=" * 60)
    print()
    
    # .env dosyası var mı kontrol et
    env_path = Path('.env')
    
    if env_path.exists():
        print("⚠️  .env dosyası zaten mevcut!")
        choice = input("Üzerine yazmak ister misiniz? (e/h): ").lower()
        if choice != 'e':
            print("❌ İşlem iptal edildi.")
            return
        print()
    
    print("📋 ADIM 1: Meta Developer Hesabı")
    print("-" * 60)
    print("1. https://developers.facebook.com adresine gidin")
    print("2. Hesap oluşturun (yoksa)")
    print("3. 'Uygulama Oluştur' > 'Business' seçin")
    print()
    input("Tamamladınız mı? Enter'a basın...")
    print()
    
    print("📋 ADIM 2: WhatsApp Ürünü Ekleyin")
    print("-" * 60)
    print("1. App Dashboard'da 'Add Product' > 'WhatsApp'")
    print("2. 'Set Up' butonuna tıklayın")
    print()
    input("Tamamladınız mı? Enter'a basın...")
    print()
    
    print("📋 ADIM 3: Credentials'ları Girin")
    print("-" * 60)
    print()
    
    # Phone Number ID al
    print("📱 Phone Number ID:")
    print("   (WhatsApp Dashboard → API Setup → Phone number ID)")
    print("   Örnek: 123456789012345")
    phone_number_id = input("   Phone Number ID: ").strip()
    print()
    
    # Access Token al
    print("🔑 Access Token:")
    print("   (WhatsApp Dashboard → API Setup → Temporary access token)")
    print("   VEYA")
    print("   (Business Settings → System Users → Generate Token)")
    print("   Örnek: EAAxxxxxxxxxxxx...")
    access_token = input("   Access Token: ").strip()
    print()
    
    # Webhook Verify Token
    print("🔐 Webhook Verify Token:")
    print("   (Kendiniz belirlersiniz, varsayılan: tevkil_webhook_2025)")
    webhook_token = input("   Webhook Token [tevkil_webhook_2025]: ").strip()
    if not webhook_token:
        webhook_token = "tevkil_webhook_2025"
    print()
    
    # Flask Secret Key
    print("🔒 Flask Secret Key:")
    print("   (Production için güçlü bir key, test için varsayılanı kullanabilirsiniz)")
    flask_secret = input("   Secret Key [dev-secret-key-2025]: ").strip()
    if not flask_secret:
        flask_secret = "dev-secret-key-2025"
    print()
    
    # .env dosyası içeriği
    env_content = f"""# ============================================
# ULUSAL TEVKİL AĞI - ENVIRONMENT VARIABLES
# ============================================

# Flask Configuration
FLASK_SECRET_KEY={flask_secret}
FLASK_ENV=development

# Database Configuration
DATABASE_URL=sqlite:///tevkil.db

# ============================================
# META WHATSAPP BUSINESS API
# ============================================

# Phone Number ID
META_PHONE_NUMBER_ID={phone_number_id}

# Access Token
META_ACCESS_TOKEN={access_token}

# API Version
META_API_VERSION=v21.0

# Webhook Verify Token
META_WEBHOOK_VERIFY_TOKEN={webhook_token}

# ============================================
# EMAIL (Opsiyonel)
# ============================================
SENDGRID_API_KEY=
FROM_EMAIL=noreply@utap.com.tr

# ============================================
# APPLICATION URLs
# ============================================
BASE_URL=http://localhost:5000
FRONTEND_URL=http://localhost:3000
"""
    
    # Dosyaya yaz
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("=" * 60)
    print("✅ .env DOSYASI OLUŞTURULDU!")
    print("=" * 60)
    print()
    print("📋 ÖZET:")
    print(f"   📱 Phone Number ID: {phone_number_id}")
    print(f"   🔑 Access Token: {access_token[:20]}...")
    print(f"   🔐 Webhook Token: {webhook_token}")
    print()
    
    print("📋 ADIM 4: Webhook'u Yapılandırın")
    print("-" * 60)
    print("1. WhatsApp Dashboard → Configuration → Webhook")
    print("2. 'Edit' butonuna tıklayın")
    print()
    print("   🌐 PRODUCTION için:")
    print("      Callback URL: https://utap.com.tr/api/whatsapp/webhook")
    print(f"      Verify Token: {webhook_token}")
    print()
    print("   🧪 LOCAL TEST için (Ngrok):")
    print("      a. Terminal'de: ngrok http 5000")
    print("      b. Ngrok URL'i alın (örn: https://abc123.ngrok.io)")
    print("      c. Callback URL: https://abc123.ngrok.io/api/whatsapp/webhook")
    print(f"      d. Verify Token: {webhook_token}")
    print()
    print("3. 'Verify and Save' butonuna tıklayın")
    print("4. Webhook fields: 'messages' seçin")
    print()
    
    print("📋 ADIM 5: Test Numarası Ekleyin")
    print("-" * 60)
    print("1. WhatsApp Dashboard → API Setup → 'To' bölümü")
    print("2. Kendi WhatsApp numaranızı ekleyin (+905551234567)")
    print("3. WhatsApp'tan gelen kodu doğrulayın")
    print()
    
    print("=" * 60)
    print("🎉 KURULUM TAMAMLANDI!")
    print("=" * 60)
    print()
    print("✅ Şimdi yapabilecekleriniz:")
    print("   1. python app.py (Flask'ı başlatın)")
    print("   2. http://127.0.0.1:5000/whatsapp/setup (Test sayfasına gidin)")
    print("   3. WhatsApp'tan Meta numarasına #YARDIM yazın")
    print()
    print("📚 Detaylı rehber: WHATSAPP_KURULUM.md dosyasını okuyun")
    print()

def test_credentials():
    """
    Credentials'ları test et
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    print()
    print("=" * 60)
    print("🧪 CREDENTIALS TESTİ")
    print("=" * 60)
    print()
    
    phone_id = os.getenv('META_PHONE_NUMBER_ID')
    token = os.getenv('META_ACCESS_TOKEN')
    webhook_token = os.getenv('META_WEBHOOK_VERIFY_TOKEN')
    
    if not phone_id or phone_id == 'your_phone_number_id_here':
        print("❌ META_PHONE_NUMBER_ID eksik veya geçersiz!")
        return False
    
    if not token or token == 'your_permanent_access_token_here':
        print("❌ META_ACCESS_TOKEN eksik veya geçersiz!")
        return False
    
    print(f"✅ Phone Number ID: {phone_id}")
    print(f"✅ Access Token: {token[:20]}..." + ("*" * 20))
    print(f"✅ Webhook Token: {webhook_token}")
    print()
    
    # Meta API'ye test isteği gönder
    print("📡 Meta API bağlantı testi yapılıyor...")
    try:
        import requests
        url = f"https://graph.facebook.com/v21.0/{phone_id}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bağlantı başarılı!")
            print(f"   Telefon: {data.get('display_phone_number', 'N/A')}")
            print(f"   Durum: {data.get('quality_rating', 'N/A')}")
            return True
        else:
            print(f"❌ Bağlantı hatası: {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ Test hatası: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Test modu
        test_credentials()
    else:
        # Kurulum modu
        create_env_file()
        
        # Test yapmak ister mi?
        print()
        choice = input("Şimdi test yapmak ister misiniz? (e/h): ").lower()
        if choice == 'e':
            test_credentials()
