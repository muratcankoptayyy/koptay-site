"""
Check and fix test users
"""
from app import app
from models import db, User

with app.app_context():
    # Check existing users
    users = User.query.all()
    print(f"\n📊 Toplam kullanıcı sayısı: {len(users)}")
    
    for user in users:
        print(f"\n👤 Kullanıcı: {user.email}")
        print(f"   Ad: {user.full_name}")
        print(f"   Şifre hash var mı: {'Evet' if user.password_hash else 'Hayır'}")
    
    # Update test user password
    test_user = User.query.filter_by(email='ahmet@example.com').first()
    if test_user:
        print(f"\n🔧 Test kullanıcısı bulundu: {test_user.email}")
        test_user.set_password('password123')
        db.session.commit()
        print("✅ Şifre güncellendi: password123")
        
        # Verify password
        if test_user.check_password('password123'):
            print("✅ Şifre doğrulandı!")
        else:
            print("❌ Şifre doğrulaması başarısız!")
    else:
        print("\n❌ Test kullanıcısı bulunamadı!")
        print("Yeni test kullanıcısı oluşturuluyor...")
        
        new_user = User(
            email='ahmet@example.com',
            full_name='Ahmet Yılmaz',
            phone='5551234567',
            bar_association='İstanbul Barosu',
            bar_registration_number='12345',
            specializations=['Ceza Hukuku'],
            city='İstanbul',
            district='Kadıköy',
            bio='Deneyimli ceza avukatı'
        )
        new_user.set_password('password123')
        db.session.add(new_user)
        db.session.commit()
        print("✅ Yeni kullanıcı oluşturuldu!")
        print(f"   E-posta: ahmet@example.com")
        print(f"   Şifre: password123")
