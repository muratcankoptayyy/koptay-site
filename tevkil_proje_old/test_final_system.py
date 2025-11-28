"""
Test: Duplicate mesaj önleme ve AI intent sistemi
"""
from whatsapp_central_bot import central_bot
from app import app, db, User
from datetime import datetime, timezone

with app.app_context():
    user = User.query.filter_by(email='test@koptay.av.tr').first()
    
    print("\n" + "="*70)
    print("🧪 DUPLICATE MESAJ ÖNLEME + AI INTENT TESTİ")
    print("="*70)
    
    # Test 1: İlan oluştur
    print("\n1️⃣ İlan mesajı gönder:")
    print("-" * 70)
    
    r1 = central_bot.process_message(
        user.phone,
        'Ankara Asliye Hukuk Mahkemesinde 22.10.2025 saat 13:30 duruşma, 1500 TL'
    )
    
    print(f"✅ Önizleme alındı (uzunluk: {len(r1['message'])} karakter)")
    print(f"İlk 300 karakter:\n{r1['message'][:300]}...\n")
    
    # Test 2: "Tamamdır paylaşabilirsin" ile onay
    print("2️⃣ Onay mesajı: 'Tamamdır paylaşabilirsin'")
    print("-" * 70)
    
    r2 = central_bot.process_message(user.phone, 'Tamamdır paylaşabilirsin')
    
    if r2['success']:
        print("✅ BAŞARILI! İlan oluşturuldu!")
        print(f"Yanıt: {r2['message'][:200]}")
    else:
        print("❌ BAŞARISIZ!")
        print(f"Hata: {r2['message'][:500]}")
    
    print("\n" + "="*70)
    
    # Test 3: Yeni ilan + farklı onay kelimeleri
    print("\n3️⃣ Farklı onay kelimeleri testi:")
    print("="*70)
    
    test_approvals = [
        'Paylaş',
        'Tamamdır',
        'Süper paylaş',
        'Evet olur'
    ]
    
    for approval_word in test_approvals:
        print(f"\n📝 Test: '{approval_word}'")
        print("-" * 70)
        
        # Yeni ilan
        central_bot.process_message(
            user.phone,
            'İstanbul 3. Ticaret Mahkemesinde yarın duruşma, 4000 TL'
        )
        
        # Onay kelimesi
        r = central_bot.process_message(user.phone, approval_word)
        
        if r['success']:
            print(f"✅ '{approval_word}' → ONAY algılandı")
        else:
            print(f"❌ '{approval_word}' → ONAY OLARAK ALGILANMADI")
            print(f"   Yanıt: {r['message'][:150]}")
    
    print("\n" + "="*70)
    print("✅ TEST TAMAMLANDI")
    print("="*70)
    print(f"\nCache'deki mesaj sayısı: {len(central_bot.processed_messages)}")
    print(f"Pending AI posts: {len(central_bot.pending_ai_posts)}")
