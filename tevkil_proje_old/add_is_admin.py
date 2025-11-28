"""
Veritabanına is_admin kolonu ekler
"""

import sqlite3
import os
from datetime import datetime

def add_is_admin_column(db_path):
    """Belirtilen veritabanına is_admin kolonunu ekler"""
    
    if not os.path.exists(db_path):
        print(f"❌ Veritabanı bulunamadı: {db_path}")
        return False
    
    print(f"\n{'='*60}")
    print(f"🔧 İşleniyor: {db_path}")
    print(f"{'='*60}\n")
    
    # Backup oluştur
    backup_name = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    import shutil
    shutil.copy2(db_path, backup_name)
    print(f"✅ Yedek oluşturuldu: {backup_name}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Mevcut kolonları kontrol et
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'is_admin' in columns:
            print("ℹ️ 'is_admin' kolonu zaten mevcut")
        else:
            # is_admin kolonunu ekle (default: 0/False)
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN is_admin INTEGER DEFAULT 0
            """)
            
            conn.commit()
            print("✅ 'is_admin' kolonu eklendi")
        
        # Kullanıcı sayısını göster
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📊 Toplam {user_count} kullanıcı")
        
        print(f"\n✨ Migration tamamlandı!\n")
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    # Tüm veritabanlarını bul ve güncelle
    db_paths = []
    
    if os.path.exists('tevkil.db'):
        db_paths.append('tevkil.db')
    
    if os.path.exists('instance/tevkil.db'):
        db_paths.append('instance/tevkil.db')
    
    if not db_paths:
        print("❌ Hiç veritabanı bulunamadı!")
        exit(1)
    
    print(f"📁 Bulunan veritabanları: {db_paths}")
    
    # Her veritabanını güncelle
    success_count = 0
    for db_path in db_paths:
        if add_is_admin_column(db_path):
            success_count += 1
    
    print(f"{'='*60}")
    if success_count == len(db_paths):
        print(f"✨ TÜM VERİTABANLARI GÜNCELLENDİ! ({success_count}/{len(db_paths)})")
    else:
        print(f"⚠️ {success_count}/{len(db_paths)} veritabanı güncellendi")
    print(f"{'='*60}\n")
