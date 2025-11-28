"""
Test: "Tamamdır" kelimesinin algılanması
"""
from whatsapp_central_bot import central_bot
from app import app, db, User

with app.app_context():
    user = User.query.filter_by(email='test@koptay.av.tr').first()
    
    print("\n" + "="*60)
    print("🧪 'TAMAMDIR' KELİMESİ TESTİ")
    print("="*60)
    
    # Önce ilan oluştur
    print("\n1️⃣ İlan mesajı gönder:")
    r1 = central_bot.process_message(
        user.phone,
        'Bursa 2. Ağır Ceza Mahkemesinde yarın saat 11:00 duruşma, 4000 TL'
    )
    print("✅ Önizleme alındı\n")
    
    # "Tamamdır" ile onay
    print("2️⃣ 'Tamamdır' kelimesi ile onay:")
    print("-" * 60)
    
    r2 = central_bot.process_message(user.phone, 'Tamamdır')
    
    if r2['success']:
        print("✅ BAŞARILI! 'Tamamdır' kelimesi algılandı!")
        print(r2['message'][:300])
    else:
        print("❌ BAŞARISIZ")
        print(r2['message'][:500])
    
    print("\n" + "="*60)
    
    # Başka varyasyonlar
    print("\n3️⃣ Diğer onay varyasyonları:")
    print("="*60)
    
    test_words = ['tamamdir', 'harika', 'süper', 'okey', 'kabul']
    
    for word in test_words:
        # Yeni ilan
        central_bot.process_message(
            user.phone,
            'İzmir 3. Aile Mahkemesinde duruşma, 3000 TL'
        )
        
        # Test kelimesi
        r = central_bot.process_message(user.phone, word)
        
        status = "✅" if r['success'] else "❌"
        print(f"{status} '{word}': {r['success']}")
    
    print("\n" + "="*60)
    print("✅ TEST TAMAMLANDI")
    print("="*60)
