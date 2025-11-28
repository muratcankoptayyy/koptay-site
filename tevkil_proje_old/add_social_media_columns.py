"""
Veritabanına sosyal medya kolonları ekler
"""
import sqlite3
import os

def add_social_media_columns(db_path):
    """Sosyal medya kolonlarını ekle"""
    print(f"📁 Veritabanı: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Mevcut kolonları kontrol et
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        new_columns = {
            'linkedin_url': 'VARCHAR(255)',
            'twitter_url': 'VARCHAR(255)',
            'instagram_url': 'VARCHAR(255)',
            'website_url': 'VARCHAR(255)'
        }
        
        added_count = 0
        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"✅ '{col_name}' kolonu eklendi")
                added_count += 1
            else:
                print(f"ℹ️ '{col_name}' kolonu zaten mevcut")
        
        conn.commit()
        
        if added_count > 0:
            print(f"\n✨ {added_count} yeni kolon eklendi!")
        else:
            print("\n✅ Tüm kolonlar zaten mevcut")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    # Veritabanlarını bul ve güncelle
    db_paths = []
    
    if os.path.exists('tevkil.db'):
        db_paths.append('tevkil.db')
    
    if os.path.exists('instance/tevkil.db'):
        db_paths.append('instance/tevkil.db')
    
    if not db_paths:
        print("❌ Hiç veritabanı bulunamadı!")
        exit(1)
    
    print(f"📁 Bulunan veritabanları: {db_paths}\n")
    
    for db_path in db_paths:
        add_social_media_columns(db_path)
        print()
    
    print("🎉 Migration tamamlandı!")
