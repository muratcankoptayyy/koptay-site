"""
Mesajlaşma İyileştirmeleri - Database Migration
- Dosya paylaşımı desteği
- Mesaj tipleri (text, file, image, emoji)
- Mesaj tepkileri (reactions)
- Sabitlenmiş mesajlar
- Gelişmiş okundu bilgisi
"""

import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = 'instance/tevkil.db'

def upgrade_database():
    print("🔧 Mesajlaşma İyileştirmeleri - Database Migration")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Önce messages tablosunun var olup olmadığını kontrol et
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='messages'
        """)
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("\n⚠️  Messages tablosu bulunamadı.")
            print("   Lütfen önce Flask uygulamasını başlatın (database oluşturulsun).")
            print("   Komut: python app.py")
            return
        
        print("\n📍 Yeni kolonlar ekleniyor...")
        
        # Message tablosuna yeni kolonlar ekle
        new_columns = [
            # Mesaj tipi
            ("message_type", "VARCHAR(20) DEFAULT 'text'", "Mesaj tipi (text, file, image, emoji)"),
            
            # Dosya bilgileri
            ("file_name", "VARCHAR(255)", "Dosya adı"),
            ("file_size", "INTEGER", "Dosya boyutu (bytes)"),
            ("file_url", "VARCHAR(500)", "Dosya URL"),
            ("file_type", "VARCHAR(100)", "Dosya MIME tipi"),
            
            # Mesaj özellikleri
            ("is_pinned", "BOOLEAN DEFAULT 0", "Sabitlenmiş mi?"),
            ("pinned_at", "DATETIME", "Sabitlenme zamanı"),
            ("pinned_by", "INTEGER", "Kim sabitledi (user_id)"),
            
            # Tepkiler (reactions) - JSON formatında
            ("reactions", "TEXT", "Mesaj tepkileri JSON"),
            
            # Düzenleme bilgisi
            ("edited_at", "DATETIME", "Düzenlenme zamanı"),
            ("is_deleted", "BOOLEAN DEFAULT 0", "Silinmiş mi?"),
        ]
        
        for column_name, column_type, description in new_columns:
            try:
                cursor.execute(f"ALTER TABLE messages ADD COLUMN {column_name} {column_type}")
                print(f"   ✅ {column_name} kolonu eklendi - {description}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"   ⚠️  {column_name} kolonu zaten mevcut")
                else:
                    raise
        
        conn.commit()
        print("\n✅ Kolonlar başarıyla eklendi!")
        
        # Mevcut mesajları güncelle (message_type'ı text yap)
        print("\n📝 Mevcut mesajlar güncelleniyor...")
        cursor.execute("""
            UPDATE messages 
            SET message_type = 'text' 
            WHERE message_type IS NULL
        """)
        updated_count = cursor.rowcount
        conn.commit()
        print(f"   ✅ {updated_count} mesaj güncellendi")
        
        # İstatistikler
        print("\n📊 Mesajlaşma İstatistikleri:")
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]
        print(f"   📨 Toplam mesaj sayısı: {total_messages}")
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]
        print(f"   💬 Toplam konuşma sayısı: {total_conversations}")
        
        print("\n" + "=" * 60)
        print("✨ Mesajlaşma iyileştirmeleri migration tamamlandı!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    upgrade_database()
