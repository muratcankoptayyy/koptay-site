"""
Fix metadata column name in security_logs table
SQLite doesn't support ALTER TABLE RENAME COLUMN directly in old versions
"""
import sqlite3

def fix_security_logs_table():
    conn = sqlite3.connect('instance/tevkil.db')
    cursor = conn.cursor()
    
    try:
        # 1. Önce tabloyu yedekle (tüm dataları geçici tabloya al)
        print("📦 security_logs tablosunu yedekliyorum...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_logs_backup AS
            SELECT * FROM security_logs
        """)
        
        # 2. Eski tabloyu sil
        print("🗑️  Eski tabloyu siliyorum...")
        cursor.execute("DROP TABLE security_logs")
        
        # 3. Yeni tabloyu doğru kolon adıyla oluştur
        print("✨ Yeni tabloyu oluşturuyorum (metadata → event_metadata)...")
        cursor.execute("""
            CREATE TABLE security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_type VARCHAR(50) NOT NULL,
                event_severity VARCHAR(20) DEFAULT 'INFO',
                ip_address VARCHAR(50),
                user_agent TEXT,
                location VARCHAR(100),
                description TEXT,
                event_metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """)
        
        # 4. Indexleri yeniden oluştur
        print("📊 Indexleri oluşturuyorum...")
        cursor.execute("CREATE INDEX idx_security_logs_user_id ON security_logs(user_id)")
        cursor.execute("CREATE INDEX idx_security_logs_event_type ON security_logs(event_type)")
        cursor.execute("CREATE INDEX idx_security_logs_created_at ON security_logs(created_at)")
        
        # 5. Yedekteki dataları yeni tabloya aktar
        print("♻️  Verileri geri yüklüyorum...")
        cursor.execute("""
            INSERT INTO security_logs 
            (id, user_id, event_type, event_severity, ip_address, user_agent, location, description, event_metadata, created_at)
            SELECT id, user_id, event_type, event_severity, ip_address, user_agent, location, description, metadata, created_at
            FROM security_logs_backup
        """)
        
        # 6. Yedek tablosunu sil
        print("🧹 Yedek tablosunu temizliyorum...")
        cursor.execute("DROP TABLE security_logs_backup")
        
        conn.commit()
        
        # 7. Kontrol et
        cursor.execute("PRAGMA table_info(security_logs)")
        columns = cursor.fetchall()
        print("\n✅ Tablo başarıyla güncellendi!")
        print("\n📋 Yeni kolon yapısı:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Kayıt sayısını göster
        cursor.execute("SELECT COUNT(*) FROM security_logs")
        count = cursor.fetchone()[0]
        print(f"\n📊 Toplam kayıt sayısı: {count}")
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fix_security_logs_table()
