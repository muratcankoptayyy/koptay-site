"""
Profil & Ayarlar - Database Migration
- Gizlilik ayarları (profile_visible, show_phone, show_email, show_last_active)
"""

import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = 'instance/tevkil.db'

def upgrade_database():
    print("🔧 Profil & Ayarlar İyileştirmeleri - Database Migration")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Users tablosunun var olup olmadığını kontrol et
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        """)
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("\n⚠️  Users tablosu bulunamadı.")
            print("   Lütfen önce Flask uygulamasını başlatın (database oluşturulsun).")
            return
        
        print("\n📍 Yeni kolonlar ekleniyor...")
        
        # Eklenecek kolonlar (kolun adı, SQL tipi, açıklama)
        new_columns = [
            ('profile_visible', 'BOOLEAN DEFAULT 1', 'Profil görünürlüğü (1=herkese açık)'),
            ('show_phone', 'BOOLEAN DEFAULT 1', 'Telefon numarası göster'),
            ('show_email', 'BOOLEAN DEFAULT 0', 'E-posta adresi göster'),
            ('show_last_active', 'BOOLEAN DEFAULT 1', 'Son görülme göster'),
        ]
        
        # Kolonları ekle
        for col_name, col_type, description in new_columns:
            try:
                # Kolon zaten var mı kontrol et
                cursor.execute(f"PRAGMA table_info(users)")
                existing_columns = [row[1] for row in cursor.fetchall()]
                
                if col_name not in existing_columns:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                    print(f"   ✅ {col_name} kolonu eklendi - {description}")
                else:
                    print(f"   ⏭️  {col_name} zaten mevcut")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   ⏭️  {col_name} zaten mevcut")
                else:
                    raise
        
        conn.commit()
        print("\n✅ Kolonlar başarıyla eklendi!")
        
        # İstatistik
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        print(f"\n📊 Kullanıcı İstatistikleri:")
        print(f"   👥 Toplam kullanıcı sayısı: {user_count}")
        
        # Tüm kullanıcılar için varsayılan değerleri ayarla
        print(f"\n📝 Mevcut kullanıcılar için varsayılan ayarlar yapılıyor...")
        cursor.execute("""
            UPDATE users 
            SET profile_visible = 1,
                show_phone = 1,
                show_email = 0,
                show_last_active = 1
            WHERE profile_visible IS NULL
        """)
        updated = cursor.rowcount
        print(f"   ✅ {updated} kullanıcı güncellendi")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✨ Profil & Ayarlar iyileştirmeleri migration tamamlandı!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    upgrade_database()
