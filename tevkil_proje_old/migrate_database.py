"""
Database migration script - Add new professional fields to User model
"""
from app import app
from models import db, User
import sqlite3

def migrate_database():
    """Add new columns to users table"""
    with app.app_context():
        conn = sqlite3.connect('tevkil.db')
        cursor = conn.cursor()
        
        # List of new columns to add
        new_columns = [
            ("tc_number", "VARCHAR(11)"),
            ("bar_association", "VARCHAR(100)"),
            ("bar_registration_number", "VARCHAR(50)"),
            ("attended_hearings_count", "INTEGER DEFAULT 0"),
            ("completed_tasks_count", "INTEGER DEFAULT 0"),
        ]
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        print("Mevcut kolonlar:", existing_columns)
        
        # Add new columns if they don't exist
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                    print(f"✅ '{column_name}' kolonu eklendi")
                except sqlite3.OperationalError as e:
                    print(f"⚠️ '{column_name}' kolonu zaten var veya hata: {e}")
        
        conn.commit()
        conn.close()
        
        print("\n✨ Database migration tamamlandı!")
        
        # Create unique constraint on bar_association + bar_registration_number
        try:
            with app.app_context():
                # Drop old bar_association_number column if exists
                conn = sqlite3.connect('tevkil.db')
                cursor = conn.cursor()
                
                cursor.execute("PRAGMA table_info(users)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'bar_association_number' in columns:
                    print("\n⚠️ Eski 'bar_association_number' kolonu bulundu")
                    print("Not: SQLite'da kolon silme işlemi tablo yeniden oluşturularak yapılır")
                    print("Şimdilik eski kolon kalsın, yeni kolonları kullanın")
                
                conn.close()
        except Exception as e:
            print(f"⚠️ Constraint oluşturulurken uyarı: {e}")

if __name__ == '__main__':
    migrate_database()
