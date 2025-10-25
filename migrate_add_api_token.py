"""
Database Migration: Add API Token columns for mobile authentication
"""
from app import app, db
from models import User

def migrate():
    with app.app_context():
        print("🔄 Starting migration: Add API token columns...")
        
        try:
            # SQLite için ALTER TABLE
            with db.engine.connect() as conn:
                # Check if columns exist
                result = conn.execute(db.text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'api_token' not in columns:
                    print("  ➕ Adding api_token column...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN api_token VARCHAR(64)"))
                    conn.commit()
                    # Create unique index separately (SQLite limitation)
                    print("  ➕ Creating unique index on api_token...")
                    conn.execute(db.text("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_api_token ON users(api_token)"))
                    conn.commit()
                else:
                    print("  ✓ api_token column already exists")
                
                if 'api_token_created_at' not in columns:
                    print("  ➕ Adding api_token_created_at column...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN api_token_created_at DATETIME"))
                    conn.commit()
                else:
                    print("  ✓ api_token_created_at column already exists")
                
                if 'api_token_last_used' not in columns:
                    print("  ➕ Adding api_token_last_used column...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN api_token_last_used DATETIME"))
                    conn.commit()
                else:
                    print("  ✓ api_token_last_used column already exists")
            
            print("✅ Migration completed successfully!")
            print("\n📱 Mobile API endpoints are now available:")
            print("  POST /api/mobile/login  - Login with email/password, get token")
            print("  POST /api/mobile/verify - Verify token and get user info")
            print("  POST /api/mobile/logout - Revoke token (logout)")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    migrate()
