"""
Doğal Dil İntent Testi
# kullanmadan onay/red/düzeltme
"""
from whatsapp_central_bot import central_bot
from app import app, db, User

with app.app_context():
    user = User.query.filter_by(email='test@koptay.av.tr').first()
    
    if not user:
        print("❌ Test kullanıcısı bulunamadı!")
        exit(1)
    
    print("\n" + "="*60)
    print("🧪 DOĞAL DİL TEST - # İŞARETİ YOK!")
    print("="*60)
    
    # Test 1: İlan oluştur
    print("\n1️⃣ İLAN MESAJI GÖNDER:")
    print("Mesaj: 'İstanbul 2. Asliye Ticaret Mahkemesinde yarın saat 14:00 duruşma var, 5000 TL'")
    print("-" * 60)
    
    r1 = central_bot.process_message(
        user.phone, 
        'İstanbul 2. Asliye Ticaret Mahkemesinde yarın saat 14:00 duruşma var, 5000 TL'
    )
    
    print(r1['message'][:500])
    print("\n")
    
    # Test 2: Doğal dil ile onay
    print("2️⃣ DOĞAL DİL İLE ONAY (# YOK!):")
    print("Mesaj: 'Tamam güzel olmuş paylaş'")
    print("-" * 60)
    
    r2 = central_bot.process_message(user.phone, 'Tamam güzel olmuş paylaş')
    
    if r2['success']:
        print("✅ ONAY BAŞARILI!")
        print(r2['message'][:400])
    else:
        print("❌ ONAY BAŞARISIZ")
        print(r2['message'])
    
    print("\n" + "="*60)
    print("3️⃣ YENİ İLAN + DÜZELTME TESTİ:")
    print("="*60)
    
    # Test 3: Yeni ilan
    print("\nİlan mesajı: 'Ankara 3. Aile Mahkemesinde bugün saat 10:00 duruşma, 2000 TL'")
    r3 = central_bot.process_message(
        user.phone,
        'Ankara 3. Aile Mahkemesinde bugün saat 10:00 duruşma, 2000 TL'
    )
    print("Önizleme alındı!\n")
    
    # Test 4: Düzeltme
    print("Düzeltme mesajı: 'Ücret 3000 TL olmalı'")
    print("-" * 60)
    
    r4 = central_bot.process_message(user.phone, 'Ücret 3000 TL olmalı')
    
    if r4['success']:
        print("✅ DÜZELTME BAŞARILI!")
        print(r4['message'][:500])
    else:
        print("❌ DÜZELTME BAŞARISIZ")
        print(r4['message'])
    
    print("\n" + "="*60)
    print("✅ TEST TAMAMLANDI!")
    print("="*60)
