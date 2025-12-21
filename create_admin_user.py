
from app import app, db
from models import User

def create_or_update_user():
    with app.app_context():
        email = "koptaymuratcan@gmail.com"
        full_name = "Murat Can Koptay"
        password = "password123"
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"Kullanıcı zaten var: {email}")
            user.set_password(password)
            user.is_active = True
            user.is_verified = True
            print("Şifre güncellendi: password123")
        else:
            print(f"Yeni kullanıcı oluşturuluyor: {email}")
            user = User(
                email=email,
                full_name=full_name,
                bar_association="İstanbul Barosu",
                city="İstanbul",
                is_active=True,
                is_verified=True,
                is_admin=True 
            )
            user.set_password(password)
            db.session.add(user)
            print("Kullanıcı oluşturuldu.")
            
        db.session.commit()
        print("İşlem tamamlandı.")

if __name__ == "__main__":
    create_or_update_user()
