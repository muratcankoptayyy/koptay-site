"""
Complete database migration - Recreate users table with all columns in ALL databases
"""
import sqlite3
import shutil
from datetime import datetime
import os

def migrate_database(db_path):
    """Migrate a single database"""
    print(f"\n{'='*60}")
    print(f"🔧 İşleniyor: {db_path}")
    print(f"{'='*60}\n")
    
    # Backup current database
    backup_name = f'{db_path}.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    try:
        shutil.copy2(db_path, backup_name)
        print(f"✅ Yedek oluşturuldu: {backup_name}")
    except Exception as e:
        print(f"⚠️ Yedek oluşturulamadı: {e}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing data
    cursor.execute("SELECT * FROM users")
    old_users = cursor.fetchall()
    cursor.execute("PRAGMA table_info(users)")
    old_columns = [col[1] for col in cursor.fetchall()]

    print(f"\n📊 Mevcut {len(old_users)} kullanıcı bulundu")
    print(f"📊 Mevcut kolonlar: {old_columns}")

    # Drop old table and create new one with all required columns
    cursor.execute("DROP TABLE IF EXISTS users_old")
    cursor.execute("ALTER TABLE users RENAME TO users_old")

    # Create new users table with complete structure
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        
        -- Profile Information
        full_name VARCHAR(100) NOT NULL,
        phone VARCHAR(20),
        whatsapp_number VARCHAR(20),
        tc_number VARCHAR(11),
        
        -- Baro Bilgileri
        bar_association VARCHAR(100),
        bar_registration_number VARCHAR(50),
        
        -- Location
        city VARCHAR(50),
        district VARCHAR(50),
        
        -- Professional Info
        specializations TEXT,
        bio TEXT,
        avatar_url VARCHAR(255),
        
        -- İstatistikler
        attended_hearings_count INTEGER DEFAULT 0,
        completed_tasks_count INTEGER DEFAULT 0,
        rating REAL DEFAULT 0.0,
        rating_average REAL DEFAULT 0.0,
        rating_count INTEGER DEFAULT 0,
        total_jobs INTEGER DEFAULT 0,
        completed_jobs INTEGER DEFAULT 0,
        success_rate REAL DEFAULT 0.0,
        
        -- Status
        verified INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        
        -- Timestamps
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    print("✅ Yeni users tablosu oluşturuldu")

    # Migrate old data if any exists
    if old_users:
        print(f"\n🔄 {len(old_users)} kullanıcı migrate ediliyor...")
        
        for user in old_users:
            # Map old columns to new structure
            user_dict = dict(zip(old_columns, user))
            
            # Create email from username if not exists
            email = user_dict.get('email') or user_dict.get('username', f'user{user_dict.get("id")}@example.com')
            password_hash = user_dict.get('password_hash') or user_dict.get('password', '')
            full_name = user_dict.get('full_name') or user_dict.get('username', 'Kullanıcı')
            
            cursor.execute('''
                INSERT INTO users (
                    id, email, password_hash, full_name, phone, whatsapp_number,
                    tc_number, bar_association, bar_registration_number,
                    city, district, specializations, bio, avatar_url,
                    attended_hearings_count, completed_tasks_count,
                    rating, rating_average, rating_count, total_jobs, completed_jobs, success_rate,
                    verified, is_active, created_at, last_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_dict.get('id'),
                email,
                password_hash,
                full_name,
                user_dict.get('phone'),
                user_dict.get('whatsapp_number'),
                user_dict.get('tc_number'),
                user_dict.get('bar_association'),
                user_dict.get('bar_registration_number'),
                user_dict.get('city'),
                user_dict.get('district'),
                user_dict.get('specializations'),
                user_dict.get('bio'),
                user_dict.get('avatar_url'),
                user_dict.get('attended_hearings_count', 0),
                user_dict.get('completed_tasks_count', 0),
                user_dict.get('rating', 0.0),
                user_dict.get('rating_average', 0.0),
                user_dict.get('rating_count', 0),
                user_dict.get('total_jobs', 0),
                user_dict.get('completed_jobs', 0),
                user_dict.get('success_rate', 0.0),
                user_dict.get('verified', 0),
                user_dict.get('is_active', 1),
                user_dict.get('created_at'),
                user_dict.get('last_active')
            ))
        
        print(f"✅ {len(old_users)} kullanıcı migrate edildi")

    # Drop old table
    cursor.execute("DROP TABLE users_old")

    conn.commit()

    # Verify new structure
    cursor.execute("PRAGMA table_info(users)")
    new_columns = cursor.fetchall()

    print("\n=== YENİ TABLO YAPISI ===")
    for col in new_columns:
        print(f"  {col[1]} ({col[2]})")

    print(f"\n✨ Migration tamamlandı! Toplam {len(new_columns)} kolon")

    conn.close()

# Main execution
if __name__ == '__main__':
    # Check which database to fix
    db_paths = []
    if os.path.exists('tevkil.db'):
        db_paths.append('tevkil.db')
    if os.path.exists('instance/tevkil.db'):
        db_paths.append('instance/tevkil.db')

    if not db_paths:
        print("❌ Veritabanı dosyası bulunamadı!")
        exit(1)

    print(f"📁 Bulunan veritabanları: {db_paths}")

    for db_path in db_paths:
        migrate_database(db_path)

    print(f"\n{'='*60}")
    print("✨ TÜM VERİTABANLARI GÜNCELLENDİ!")
    print(f"{'='*60}")
