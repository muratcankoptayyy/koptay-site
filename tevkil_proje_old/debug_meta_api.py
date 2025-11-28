"""
Meta WhatsApp API Debug Script
Mesaj gönderilmeme sorunlarını tespit eder
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def debug_meta_api():
    """Meta API sorunlarını debug et"""
    
    print("=" * 60)
    print("META WHATSAPP API DEBUG")
    print("=" * 60)
    
    access_token = os.getenv('META_ACCESS_TOKEN')
    phone_number_id = os.getenv('META_PHONE_NUMBER_ID')
    api_version = os.getenv('META_API_VERSION', 'v21.0')
    
    # 1. Credentials Kontrolü
    print("\n1️⃣ CREDENTIALS KONTROLÜ:")
    print(f"Access Token: {access_token[:30]}...")
    print(f"Phone Number ID: {phone_number_id}")
    print(f"API Version: {api_version}")
    
    # 2. Phone Number Status Kontrolü
    print("\n2️⃣ PHONE NUMBER STATUS KONTROLÜ:")
    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Phone Number Status: {data.get('verified_name', 'N/A')}")
        print(f"✅ Display Name: {data.get('display_phone_number', 'N/A')}")
        print(f"✅ Quality Rating: {data.get('quality_rating', 'N/A')}")
        print(f"✅ Code Verification Status: {data.get('code_verification_status', 'N/A')}")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HATA: {e.response.text}")
        print("\n🔧 Olası Sebepler:")
        print("- Access Token geçersiz (24 saat geçerli)")
        print("- Phone Number ID yanlış")
        print("- Meta Business hesabında izin sorunu")
        return False
    except Exception as e:
        print(f"❌ Bağlantı Hatası: {str(e)}")
        return False
    
    # 3. WhatsApp Business Account Kontrolü
    print("\n3️⃣ WHATSAPP BUSINESS ACCOUNT KONTROLÜ:")
    waba_id = os.getenv('META_WHATSAPP_BUSINESS_ACCOUNT_ID')
    if waba_id:
        url = f"https://graph.facebook.com/{api_version}/{waba_id}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            print(f"✅ Account ID: {data.get('id', 'N/A')}")
            print(f"✅ Account Status: {data.get('account_review_status', 'N/A')}")
            print(f"✅ Timezone: {data.get('timezone_id', 'N/A')}")
        except Exception as e:
            print(f"⚠️ Account bilgisi alınamadı: {str(e)}")
    
    # 4. Mesaj Gönderme İzinleri Kontrolü
    print("\n4️⃣ MESAJ GÖNDERME İZİNLERİ:")
    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/message_templates"
    try:
        response = requests.get(url, headers=headers, params={"limit": 5})
        response.raise_for_status()
        templates = response.json().get('data', [])
        print(f"✅ Kayıtlı Template Sayısı: {len(templates)}")
        if templates:
            print("Templates:")
            for t in templates:
                print(f"  - {t.get('name')} ({t.get('status')})")
    except Exception as e:
        print(f"⚠️ Template bilgisi alınamadı: {str(e)}")
    
    # 5. Test Mesajı Gönder (Detaylı)
    print("\n5️⃣ TEST MESAJI GÖNDERME:")
    test_phone = input("Test telefon numarası (örn: 905307111864): ")
    
    if not test_phone:
        print("❌ Telefon numarası girilmedi!")
        return False
    
    # Numara formatı kontrol
    test_phone = test_phone.replace('+', '').replace(' ', '').replace('-', '')
    print(f"📱 Formatlanmış numara: {test_phone}")
    
    # Basit mesaj gönder
    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": test_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": "Test mesajı - Tevkil Ağı WhatsApp Bot"
        }
    }
    
    print(f"\n📤 Mesaj gönderiliyor...")
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'N/A')
            print(f"\n✅ MESAJ GÖNDERİLDİ!")
            print(f"Message ID: {message_id}")
            print(f"\n📱 WhatsApp'ını kontrol et!")
            return True
        else:
            error_data = response.json()
            error = error_data.get('error', {})
            print(f"\n❌ MESAJ GÖNDERİLEMEDİ!")
            print(f"Error Code: {error.get('code')}")
            print(f"Error Type: {error.get('type')}")
            print(f"Error Message: {error.get('message')}")
            print(f"Error Subcode: {error.get('error_subcode')}")
            
            # Özel hata mesajları
            error_code = error.get('code')
            if error_code == 100:
                print("\n🔧 ÇÖZÜM:")
                print("- Telefon numarası WhatsApp Business'a kayıtlı değil")
                print("- Numarayı Meta Business Manager'dan eklemen gerekiyor")
                print("- Test için kendi numaranı kullan")
            elif error_code == 190:
                print("\n🔧 ÇÖZÜM:")
                print("- Access Token geçersiz!")
                print("- Meta Business Manager'dan yeni token al")
                print("- Token 24 saat geçerli, yeniden oluştur")
            elif error_code == 131056:
                print("\n🔧 ÇÖZÜM:")
                print("- Phone Number ID yanlış veya yetkisiz")
                print("- Meta Business Manager'dan doğru ID'yi al")
            
            return False
            
    except Exception as e:
        print(f"\n❌ Beklenmeyen Hata: {str(e)}")
        return False
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    debug_meta_api()
