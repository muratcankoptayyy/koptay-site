from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Kullanıcı var mı kontrol et
    existing_user = User.query.filter_by(email='test@koptay.av.tr').first()
    
    if existing_user:
        print(f"✓ Kullanıcı zaten var: {existing_user.email}")
    else:
        # Yeni kullanıcı oluştur
        new_user = User(
            email='test@koptay.av.tr',
            password_hash=generate_password_hash('123456'),
            full_name='Test Kullanıcı',
            phone='5551234567',
            city='Ankara',
            lawyer_type='avukat',
            verified=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"✓ Test kullanıcısı eklendi!")
        print(f"  Email: test@koptay.av.tr")
        print(f"  Şifre: 123456")
