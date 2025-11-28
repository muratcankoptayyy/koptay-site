"""
Database Migration: Add Mobile API Token Columns
Kullanıcılara mobil kimlik doğrulama için API token alanları ekler
"""
import sqlite3
from datetime import datetime

def add_api_token_columns():
    """User tablosuna api_token alanlarını ekle"""
    
    db_path = 'instance/tevkil.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📱 Mobil API Token Migration Başlatılıyor...")
        print("=" * 60)
        
        # Kolonları ekle
        columns_to_add = [
            ('api_token', 'VARCHAR(64)'),
            ('api_token_created_at', 'DATETIME'),
            ('api_token_last_used', 'DATETIME')
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f'''
                    ALTER TABLE users 
                    ADD COLUMN {column_name} {column_type}
                ''')
                print(f"✅ {column_name} kolonu eklendi")
            except sqlite3.OperationalError as e:
                if 'duplicate column name' in str(e).lower():
                    print(f"ℹ️  {column_name} kolonu zaten mevcut")
                else:
                    print(f"❌ {column_name} eklenirken hata: {e}")
        
        # api_token için unique index oluştur
        try:
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS idx_users_api_token 
                ON users(api_token)
            ''')
            print("✅ api_token için unique index oluşturuldu")
        except Exception as e:
            print(f"❌ Index oluşturulamadı: {e}")
        
        conn.commit()
        print("\n✅ Migration tamamlandı!")
        print("=" * 60)
        
        # Sonuç kontrol
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("\n📋 Users Tablosu Kolonları:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Migration hatası: {e}")
        return False


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  MOBIL API TOKEN MIGRATION")
    print("=" * 60)
    
    success = add_api_token_columns()
    
    if success:
        print("\n✅ Migration başarıyla tamamlandı!")
        print("\n📱 Mobil API artık kullanıma hazır:")
        print("   - POST /api/mobile/login")
        print("   - POST /api/mobile/logout")
        print("   - POST /api/mobile/verify")
    else:
        print("\n❌ Migration başarısız!")
