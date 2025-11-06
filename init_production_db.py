#!/usr/bin/env python3
"""
Tevkil Platform - Production Database Initialization
Fly.io PostgreSQL için tüm tabloları oluşturur
"""
import os
import sys
from datetime import datetime

# ⚡ PostgreSQL URL Fix
database_url = os.getenv('DATABASE_URL', '')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    os.environ['DATABASE_URL'] = database_url

# Flask app import
from app import app, db

def init_database():
    """Tüm tabloları oluştur"""
    print("🚀 Tevkil Platform - Database Initialization")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Database connection test
            print("📊 Testing database connection...")
            db.engine.connect()
            print("✅ Database connection successful!")
            print(f"🔗 Connected to: {db.engine.url}")
            
            # Create all tables
            print("\n📦 Creating all database tables...")
            db.create_all()
            print("✅ All tables created successfully!")
            
            # List created tables
            print("\n📋 Database tables:")
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                for idx, table in enumerate(sorted(tables), 1):
                    print(f"   {idx}. {table}")
                print(f"\n✨ Total: {len(tables)} tables created")
            else:
                print("   ⚠️  No tables found!")
                
            print("\n" + "=" * 60)
            print("🎉 Database initialization completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            print(f"📍 Error type: {type(e).__name__}")
            import traceback
            print("\n🔍 Full traceback:")
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
