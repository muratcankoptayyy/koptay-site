"""
# komutu ile test - Gemini intent sistemi bypass
"""
from whatsapp_central_bot import central_bot
from app import app, db, User

with app.app_context():
    user = User.query.filter_by(email='test@koptay.av.tr').first()
    
    print("\n" + "="*70)
    print("🧪 # KOMUT İLE TEST (Gemini intent bypass)")
    print("="*70)
    
    # Test 1: İlan oluştur
    print("\n1️⃣ İLAN MESAJI:")
    print("   'Bursa 3. Asliye Ticaret Mahkemesinde yarın saat 14:00 duruşma, 3500 TL'")
    print("-" * 70)
    
    r1 = central_bot.process_message(
        user.phone,
        'Bursa 3. Asliye Ticaret Mahkemesinde yarın saat 14:00 duruşma, 3500 TL'
    )
    
    print(f"✅ Önizleme alındı ({len(r1['message'])} karakter)")
    print("\nMesaj içeriği:")
    print(r1['message'])
    
    # Test 2: #ONAYLA ile onay (Gemini gerektirmez)
    print("\n" + "="*70)
    print("2️⃣ ONAY MESAJI (#ONAYLA komutu):")
    print("-" * 70)
    
    r2 = central_bot.process_message(user.phone, '#ONAYLA')
    
    if r2['success']:
        print("✅ BAŞARILI! İlan oluşturuldu!")
        print(f"\nYanıt:")
        print(r2['message'])
        
        # Post ID'yi bul
        if 'post_id' in r2:
            print(f"\n📋 İlan ID: #{r2['post_id']}")
    else:
        print("❌ BAŞARISIZ!")
        print(f"\nHata:")
        print(r2['message'])
    
    print("\n" + "="*70)
    print("✅ TEST TAMAMLANDI")
    print("="*70)
