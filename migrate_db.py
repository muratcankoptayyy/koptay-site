"""
Database Migration Script
Adds missing columns to the users table in production.
"""
from app import app, db
from sqlalchemy import text

def migrate():
    columns_to_add = [
        ('city', 'VARCHAR(50)'),
        ('district', 'VARCHAR(50)'),
        ('address', 'TEXT'),
        ('specializations', 'JSON'),
        ('bio', 'TEXT'),
        ('avatar_url', 'VARCHAR(255)'),
        ('education', 'JSON'),
        ('work_history', 'JSON'),
        ('skills', 'JSON'),
        ('birth_date', 'DATE'),
        ('birth_place', 'VARCHAR(100)'),
        ('drivers_license', 'VARCHAR(50)'),
        ('cv_references', 'JSON'),
        ('tc_number', 'VARCHAR(11)'),
        ('whatsapp_number', 'VARCHAR(20)'),
        ('lawyer_type', "VARCHAR(20) DEFAULT 'avukat'")
    ]

    with app.app_context():
        print("Starting database migration...")
        with db.engine.connect() as conn:
            for col_name, col_type in columns_to_add:
                try:
                    print(f"Attempting to add column '{col_name}'...")
                    conn.execute(text(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}'))
                    conn.commit()
                    print(f"✅ Added column: {col_name}")
                except Exception as e:
                    conn.rollback()
                    error_msg = str(e).lower()
                    if "duplicate column name" in error_msg or "already exists" in error_msg:
                        print(f"ℹ️ Column '{col_name}' already exists.")
                    else:
                        print(f"❌ Error adding '{col_name}': {e}")
        print("Migration completed.")

if __name__ == "__main__":
    migrate()
