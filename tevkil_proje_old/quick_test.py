"""
Hızlı sistem testi
"""
from whatsapp_central_bot import central_bot
from app import app, db, User

with app.app_context():
    user = User.query.filter_by(email='test@koptay.av.tr').first()
    
    print("\n" + "="*70)
    print("🚀 SİSTEM TAM TESTİ")
    print("="*70)
    
    # Test 1: İlan oluştur
    print("\n1️⃣ İLAN MESAJI:")
    print("   'Ankara Asliye Hukuk Mahkemesinde 22.10.2025 saat 13:30 duruşma, 1500 TL'")
    print("-" * 70)
    
    r1 = central_bot.process_message(
        user.phone,
        'Ankara Asliye Hukuk Mahkemesinde 22.10.2025 saat 13:30 duruşma, 1500 TL'
    )
    
    print(f"✅ Önizleme alındı ({len(r1['message'])} karakter)")
    print("\nİlk 500 karakter:")
    print(r1['message'][:500])
    
    # Test 2: Onay (doğal dil)
    print("\n" + "="*70)
    print("2️⃣ ONAY MESAJI (Doğal Dil):")
    print("   'Tamamdır paylaşabilirsin'")
    print("-" * 70)
    
    r2 = central_bot.process_message(user.phone, 'Tamamdır paylaşabilirsin')
    
    if r2['success']:
        print("✅ BAŞARILI! İlan oluşturuldu!")
        print(f"\nYanıt ({len(r2['message'])} karakter):")
        print(r2['message'][:400])
    else:
        print("❌ BAŞARISIZ!")
        print(f"\nHata mesajı:")
        print(r2['message'][:500])
    
    print("\n" + "="*70)
    print("✅ TEST TAMAMLANDI")
    print("="*70)
