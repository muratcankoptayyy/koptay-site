"""
Migration: Add API token columns to users table
For mobile app authentication (persistent sessions)
"""
from sqlalchemy import text
from app import app, db

def migrate():
    """Add api_token columns to users table"""
    
    with app.app_context():
        # Check if columns already exist
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        print(f"Existing columns: {len(columns)}")
        
        if 'api_token' in columns:
            print("✅ api_token column already exists!")
            return
        
        print("Adding api_token columns...")
        
        # Add columns using raw SQL (works for both SQLite and PostgreSQL)
        try:
            with db.engine.connect() as conn:
                # Add api_token column
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN api_token VARCHAR(255) UNIQUE
                """))
                print("✅ Added api_token column")
                
                # Add api_token_created_at column
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN api_token_created_at TIMESTAMP
                """))
                print("✅ Added api_token_created_at column")
                
                # Add api_token_last_used column
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN api_token_last_used TIMESTAMP
                """))
                print("✅ Added api_token_last_used column")
                
                conn.commit()
                
            print("\n🎉 Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    migrate()
