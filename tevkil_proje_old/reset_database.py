"""
Veritabanını sıfırla ve yeniden oluştur
"""
from app import app, db
from models import User, TevkilPost, Application, Rating, Message, Notification
import os

def reset_database():
    with app.app_context():
        print("⚠️  Uyarı: Tüm veriler silinecek!")
        response = input("Devam etmek istiyor musunuz? (evet/hayır): ")
        
        if response.lower() != 'evet':
            print("❌ İşlem iptal edildi.")
            return
        
        print("\n🗑️  Eski veritabanı siliniyor...")
        db.drop_all()
        
        print("🔨 Yeni veritabanı oluşturuluyor...")
        db.create_all()
        
        print("✅ Veritabanı başarıyla sıfırlandı!")
        print("\n📝 Şimdi test verilerini oluşturabilirsiniz:")
        print("   python create_test_data.py")

if __name__ == '__main__':
    reset_database()
