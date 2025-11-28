"""Add address column to users table"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE users ADD COLUMN address TEXT'))
            conn.commit()
        print("✅ Address column added successfully!")
    except Exception as e:
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            print("✅ Address column already exists!")
        else:
            print(f"❌ Error: {e}")
