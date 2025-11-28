"""
TevkilPost tablosuna city, district, courthouse kolonlarını ekler
"""

import sqlite3
import os
from datetime import datetime

def add_location_columns(db_path):
    """Belirtilen veritabanına konum kolonlarını ekler"""
    
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
        cursor.execute("PRAGMA table_info(tevkil_posts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        columns_to_add = []
        
        if 'city' not in columns:
            columns_to_add.append(('city', 'VARCHAR(50)'))
        
        if 'district' not in columns:
            columns_to_add.append(('district', 'VARCHAR(50)'))
        
        if 'courthouse' not in columns:
            columns_to_add.append(('courthouse', 'VARCHAR(100)'))
        
        if not columns_to_add:
            print("ℹ️ Tüm kolonlar zaten mevcut")
            return True
        
        # Kolonları ekle
        for col_name, col_type in columns_to_add:
            cursor.execute(f"""
                ALTER TABLE tevkil_posts 
                ADD COLUMN {col_name} {col_type}
            """)
            print(f"✅ '{col_name}' kolonu eklendi")
        
        conn.commit()
        
        # İlan sayısını göster
        cursor.execute("SELECT COUNT(*) FROM tevkil_posts")
        post_count = cursor.fetchone()[0]
        print(f"\n📊 Toplam {post_count} ilan güncellendi")
        
        # Yeni yapıyı göster
        cursor.execute("PRAGMA table_info(tevkil_posts)")
        print("\n=== YENİ KOLONLAR ===")
        for col in cursor.fetchall():
            if col[1] in ['city', 'district', 'courthouse']:
                print(f"  {col[1]} ({col[2]})")
        
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
        if add_location_columns(db_path):
            success_count += 1
    
    print(f"{'='*60}")
    if success_count == len(db_paths):
        print(f"✨ TÜM VERİTABANLARI GÜNCELLENDİ! ({success_count}/{len(db_paths)})")
    else:
        print(f"⚠️ {success_count}/{len(db_paths)} veritabanı güncellendi")
    print(f"{'='*60}\n")
