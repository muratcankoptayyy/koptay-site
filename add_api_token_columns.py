"""
Migration Script: Add API Token columns to users table
For Fly.io PostgreSQL Database
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def add_api_token_columns():
    """Add api_token, api_token_created_at, api_token_last_used columns to users table"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    # Fix PostgreSQL URL for SQLAlchemy
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"🔗 Connecting to database...")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                print("📊 Checking existing columns...")
                
                # Check if columns already exist
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name IN ('api_token', 'api_token_created_at', 'api_token_last_used')
                """))
                
                existing_columns = [row[0] for row in result]
                print(f"✅ Existing columns: {existing_columns}")
                
                # Add api_token column if not exists
                if 'api_token' not in existing_columns:
                    print("➕ Adding api_token column...")
                    conn.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN api_token VARCHAR(64) UNIQUE
                    """))
                    
                    # Create index
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_users_api_token 
                        ON users(api_token)
                    """))
                    print("✅ api_token column added with index")
                else:
                    print("⚠️ api_token column already exists")
                
                # Add api_token_created_at column if not exists
                if 'api_token_created_at' not in existing_columns:
                    print("➕ Adding api_token_created_at column...")
                    conn.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN api_token_created_at TIMESTAMP
                    """))
                    print("✅ api_token_created_at column added")
                else:
                    print("⚠️ api_token_created_at column already exists")
                
                # Add api_token_last_used column if not exists
                if 'api_token_last_used' not in existing_columns:
                    print("➕ Adding api_token_last_used column...")
                    conn.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN api_token_last_used TIMESTAMP
                    """))
                    print("✅ api_token_last_used column added")
                else:
                    print("⚠️ api_token_last_used column already exists")
                
                # Commit transaction
                trans.commit()
                print("\n🎉 Migration completed successfully!")
                return True
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"\n❌ Migration failed: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 API Token Columns Migration")
    print("=" * 60)
    
    success = add_api_token_columns()
    
    if success:
        print("\n✅ All done! Database is up to date.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
