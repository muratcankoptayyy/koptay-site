from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_user():
    with app.app_context():
        email = "koptaymuratcan@gmail.com"
        password = "123456"
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"Kullanıcı zaten var: {email}")
            user.password_hash = generate_password_hash(password)
            print("Şifre güncellendi.")
        else:
            print(f"Yeni kullanıcı oluşturuluyor: {email}")
            user = User(
                email=email,
                password_hash=generate_password_hash(password),
                full_name="Murat Can Koptay",
                phone="5551234567",
                city="İstanbul",
                bar_association="İstanbul Barosu",
                bar_registration_number="12345",
                lawyer_type="avukat",
                is_active=True,
                is_verified=True
            )
            db.session.add(user)
            print("Kullanıcı oluşturuldu.")
        
        db.session.commit()
        print("İşlem tamamlandı.")

if __name__ == "__main__":
    create_user()
