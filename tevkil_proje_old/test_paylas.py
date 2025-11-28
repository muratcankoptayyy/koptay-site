"""
Test: "Paylaş" ve diğer kelimelerin AI ile algılanması
Artık keyword yok, sadece AI!
"""
from whatsapp_central_bot import central_bot
from app import app, db, User

with app.app_context():
    user = User.query.filter_by(email='test@koptay.av.tr').first()
    
    print("\n" + "="*70)
    print("🧪 TAM AI İNTENT TESTİ - KEYWORD YOK!")
    print("="*70)
    
    # Test kelimeleri
    test_cases = [
        ("Paylaş", "approve"),
        ("Tamamdır", "approve"),
        ("Hadi gönder", "approve"),
        ("Süper olmuş", "approve"),
        ("Evet paylaş", "approve"),
        ("Vazgeç", "reject"),
        ("İptal et", "reject"),
        ("Şehir Ankara olmalı", "correction"),
        ("Ücret 5000 TL", "correction"),
    ]
    
    for word, expected_intent in test_cases:
        print(f"\n{'='*70}")
        print(f"TEST: '{word}' (Beklenen: {expected_intent})")
        print("-" * 70)
        
        # Yeni ilan oluştur
        central_bot.process_message(
            user.phone,
            'Ankara 5. Asliye Ceza Mahkemesinde yarın duruşma, 3000 TL'
        )
        
        # Test kelimesini gönder
        r = central_bot.process_message(user.phone, word)
        
        if expected_intent == "approve":
            if r['success']:
                print(f"✅ BAŞARILI! '{word}' → ONAY algılandı ve ilan oluşturuldu")
            else:
                print(f"❌ BAŞARISIZ! '{word}' → ONAY olarak algılanmadı")
                print(f"Yanıt: {r['message'][:200]}")
        
        elif expected_intent == "reject":
            if r['success'] and 'iptal' in r['message'].lower():
                print(f"✅ BAŞARILI! '{word}' → RED algılandı")
            else:
                print(f"❌ BAŞARISIZ! '{word}' → RED olarak algılanmadı")
        
        elif expected_intent == "correction":
            if r['success'] and 'düzelt' in r['message'].lower():
                print(f"✅ BAŞARILI! '{word}' → DÜZELTME algılandı")
            else:
                print(f"❌ BAŞARISIZ! '{word}' → DÜZELTME olarak algılanmadı")
    
    print("\n" + "="*70)
    print("✅ TEST TAMAMLANDI - TAM AI İNTENT SİSTEMİ")
    print("="*70)
