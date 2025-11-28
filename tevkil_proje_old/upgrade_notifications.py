"""
Bildirim Sistemi Geliştirmeleri - Database Migration
"""
from app import app, db
from models import User, Notification
from sqlalchemy import text

def upgrade_database():
    """Veritabanını güncelle"""
    with app.app_context():
        print("🔄 Veritabanı güncelleniyor...")
        
        # Notification tablosuna yeni kolonlar ekle
        try:
            with db.engine.connect() as conn:
                # Priority kolonu
                try:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN priority VARCHAR(20) DEFAULT 'normal'"))
                    print("✅ priority kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  priority kolonu zaten var veya eklenemedi: {e}")
                
                # Category kolonu
                try:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN category VARCHAR(50) DEFAULT 'general'"))
                    print("✅ category kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  category kolonu zaten var veya eklenemedi: {e}")
                
                # archived_at kolonu
                try:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN archived_at DATETIME"))
                    print("✅ archived_at kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  archived_at kolonu zaten var veya eklenemedi: {e}")
                
                # action_url kolonu
                try:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN action_url VARCHAR(500)"))
                    print("✅ action_url kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  action_url kolonu zaten var veya eklenemedi: {e}")
                
                # action_text kolonu
                try:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN action_text VARCHAR(100)"))
                    print("✅ action_text kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  action_text kolonu zaten var veya eklenemedi: {e}")
                
                # expires_at kolonu
                try:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN expires_at DATETIME"))
                    print("✅ expires_at kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  expires_at kolonu zaten var veya eklenemedi: {e}")
                
                conn.commit()
        except Exception as e:
            print(f"❌ Notification tablosu güncellenirken hata: {e}")
        
        # User tablosuna bildirim tercihleri kolonları ekle
        try:
            with db.engine.connect() as conn:
                # notify_new_application
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN notify_new_application BOOLEAN DEFAULT 1"))
                    print("✅ notify_new_application kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  notify_new_application kolonu zaten var: {e}")
                
                # notify_application_status
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN notify_application_status BOOLEAN DEFAULT 1"))
                    print("✅ notify_application_status kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  notify_application_status kolonu zaten var: {e}")
                
                # notify_new_message
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN notify_new_message BOOLEAN DEFAULT 1"))
                    print("✅ notify_new_message kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  notify_new_message kolonu zaten var: {e}")
                
                # notify_new_rating
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN notify_new_rating BOOLEAN DEFAULT 1"))
                    print("✅ notify_new_rating kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  notify_new_rating kolonu zaten var: {e}")
                
                # notify_post_expiring
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN notify_post_expiring BOOLEAN DEFAULT 1"))
                    print("✅ notify_post_expiring kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  notify_post_expiring kolonu zaten var: {e}")
                
                # notify_system
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN notify_system BOOLEAN DEFAULT 1"))
                    print("✅ notify_system kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  notify_system kolonu zaten var: {e}")
                
                # notify_email
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN notify_email BOOLEAN DEFAULT 0"))
                    print("✅ notify_email kolonu eklendi")
                except Exception as e:
                    print(f"⚠️  notify_email kolonu zaten var: {e}")
                
                conn.commit()
        except Exception as e:
            print(f"❌ User tablosu güncellenirken hata: {e}")
        
        print("\n✨ Veritabanı güncelleme tamamlandı!")
        print("\n📊 İstatistikler:")
        print(f"   - Toplam kullanıcı: {User.query.count()}")
        print(f"   - Toplam bildirim: {Notification.query.count()}")

if __name__ == '__main__':
    upgrade_database()
