from app import app, db
from sqlalchemy import text

def reset_database():
    with app.app_context():
        print("⚠️  DİKKAT: Veritabanı sıfırlanıyor... Tüm veriler silinecek!")
        
        # Drop all tables
        try:
            db.drop_all()
            print("✅ Tüm tablolar silindi.")
        except Exception as e:
            print(f"❌ Tablo silme hatası: {e}")
            
        # Create all tables
        try:
            db.create_all()
            print("✅ Tablolar yeniden oluşturuldu.")
            
            # Create initial admin user if needed
            # from models import User
            # admin = User(email='admin@tevkil.com', ...)
            # db.session.add(admin)
            # db.session.commit()
            
        except Exception as e:
            print(f"❌ Tablo oluşturma hatası: {e}")

if __name__ == "__main__":
    reset_database()
