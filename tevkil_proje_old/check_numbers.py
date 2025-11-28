"""
Meta'da kayıtlı test numaralarını listele
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def list_test_numbers():
    """Meta'da kayıtlı test numaralarını göster"""
    
    print("=" * 60)
    print("META'DA KAYITLI TEST NUMARALARI")
    print("=" * 60)
    
    access_token = os.getenv('META_ACCESS_TOKEN')
    waba_id = os.getenv('META_WHATSAPP_BUSINESS_ACCOUNT_ID')
    
    # Test numaralarını al
    url = f"https://graph.facebook.com/v21.0/{waba_id}/phone_numbers"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("\n1️⃣ BOT NUMARALARI:")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        for phone in data.get('data', []):
            print(f"\n📱 Numara: {phone.get('display_phone_number')}")
            print(f"   ID: {phone.get('id')}")
            print(f"   Verified Name: {phone.get('verified_name')}")
            print(f"   Quality: {phone.get('quality_rating')}")
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
    
    print("\n" + "=" * 60)
    print("2️⃣ KAYITLI TEST NUMARALARI (Mesaj Gönderebileceğin):")
    print("=" * 60)
    print("\nMeta Business Manager'da kontrol et:")
    print("1. https://business.facebook.com/wa/manage/phone-numbers/")
    print("2. API Setup → Step 5")
    print("3. 'To:' dropdown'u aç")
    print("4. Orada gördüğün numaralar kayıtlı numaralar")
    print("\nEğer numaranı görmüyorsan:")
    print("- 'Manage phone number list' tıkla")
    print("- Numaranı ekle ve doğrula")

if __name__ == "__main__":
    list_test_numbers()
