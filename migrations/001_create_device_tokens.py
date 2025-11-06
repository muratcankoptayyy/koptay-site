"""
Device Tokens Table Migration
Creates table for storing push notification device tokens
"""

from app import app, db
from sqlalchemy import text

def upgrade():
    """Create device_tokens table"""
    with app.app_context():
        try:
            # Create device_tokens table
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS device_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token VARCHAR(500) UNIQUE NOT NULL,
                    platform VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            
            # Create index for faster lookups
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_device_tokens_user_id 
                ON device_tokens(user_id)
            """))
            
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_device_tokens_token 
                ON device_tokens(token)
            """))
            
            db.session.commit()
            print("✅ Device tokens table created successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating device tokens table: {e}")
            raise

if __name__ == '__main__':
    upgrade()
    print("🎉 Migration completed!")
