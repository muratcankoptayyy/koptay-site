"""
🔒 Güvenlik İyileştirmeleri - Database Migration
=================================================
2FA, Session Tracking, Security Logs, Password History

Migration eklemeleri:
1. users tablosuna 2FA kolonları
2. user_sessions tablosu (aktif oturumlar)
3. security_logs tablosu (güvenlik olayları)
4. password_history tablosu (şifre geçmişi)
5. login_attempts tablosu (başarısız denemeler)
"""

import sqlite3
from datetime import datetime

def upgrade_database():
    conn = sqlite3.connect('instance/tevkil.db')
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("🔧 Güvenlik İyileştirmeleri - Database Migration")
    print("="*60)
    
    # 1. Users tablosuna 2FA kolonları ekle
    print("\n📍 Users tablosuna 2FA kolonları ekleniyor...")
    
    two_fa_columns = {
        'two_factor_enabled': 'INTEGER DEFAULT 0',
        'two_factor_secret': 'TEXT',
        'two_factor_backup_codes': 'TEXT',  # JSON array
        'last_password_change': 'TIMESTAMP',
        'password_expires_at': 'TIMESTAMP',
        'failed_login_attempts': 'INTEGER DEFAULT 0',
        'account_locked_until': 'TIMESTAMP',
        'security_question': 'TEXT',
        'security_answer': 'TEXT'
    }
    
    for column_name, column_def in two_fa_columns.items():
        try:
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM pragma_table_info('users') 
                WHERE name=?
            """, (column_name,))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                print(f"   ✅ {column_name} kolonu eklendi")
            else:
                print(f"   ℹ️  {column_name} kolonu zaten mevcut")
        except Exception as e:
            print(f"   ⚠️  {column_name} hatası: {e}")
    
    # 2. User Sessions tablosu oluştur
    print("\n📍 User Sessions tablosu oluşturuluyor...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT NOT NULL UNIQUE,
                device_info TEXT,
                ip_address TEXT,
                user_agent TEXT,
                location TEXT,
                is_active INTEGER DEFAULT 1,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("   ✅ user_sessions tablosu oluşturuldu")
        
        # Index ekle
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_user 
            ON user_sessions(user_id, is_active)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_token 
            ON user_sessions(session_token)
        """)
        print("   ✅ Session indexleri eklendi")
    except Exception as e:
        print(f"   ⚠️  user_sessions hatası: {e}")
    
    # 3. Security Logs tablosu oluştur
    print("\n📍 Security Logs tablosu oluşturuluyor...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_type TEXT NOT NULL,
                event_severity TEXT DEFAULT 'INFO',
                ip_address TEXT,
                user_agent TEXT,
                location TEXT,
                description TEXT,
                event_metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        print("   ✅ security_logs tablosu oluşturuldu")
        
        # Index ekle
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_security_user 
            ON security_logs(user_id, created_at DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_security_type 
            ON security_logs(event_type, created_at DESC)
        """)
        print("   ✅ Security logs indexleri eklendi")
    except Exception as e:
        print(f"   ⚠️  security_logs hatası: {e}")
    
    # 4. Password History tablosu oluştur
    print("\n📍 Password History tablosu oluşturuluyor...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("   ✅ password_history tablosu oluşturuldu")
        
        # Index ekle
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_password_user 
            ON password_history(user_id, created_at DESC)
        """)
        print("   ✅ Password history indexleri eklendi")
    except Exception as e:
        print(f"   ⚠️  password_history hatası: {e}")
    
    # 5. Login Attempts tablosu oluştur
    print("\n📍 Login Attempts tablosu oluşturuluyor...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                success INTEGER DEFAULT 0,
                failure_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ login_attempts tablosu oluşturuldu")
        
        # Index ekle
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_login_email 
            ON login_attempts(email, created_at DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_login_ip 
            ON login_attempts(ip_address, created_at DESC)
        """)
        print("   ✅ Login attempts indexleri eklendi")
    except Exception as e:
        print(f"   ⚠️  login_attempts hatası: {e}")
    
    conn.commit()
    
    # İstatistikler
    print("\n" + "="*60)
    print("📊 Güvenlik Tabloları İstatistikleri:")
    
    tables = ['user_sessions', 'security_logs', 'password_history', 'login_attempts']
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   📋 {table}: {count} kayıt")
        except:
            print(f"   ⚠️  {table}: Tablo bulunamadı")
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE two_factor_enabled = 1")
    two_fa_count = cursor.fetchone()[0]
    print(f"   🔐 2FA aktif kullanıcı: {two_fa_count}")
    
    conn.close()
    
    print("="*60)
    print("✨ Güvenlik iyileştirmeleri migration tamamlandı!")
    print("="*60 + "\n")

if __name__ == '__main__':
    upgrade_database()
