"""
Production database initialization script
Railway.app deploy sonrası çalıştırılacak
"""
from app import app, db

def init_db():
    """Initialize database tables"""
    with app.app_context():
        print("🔨 Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Veritabanı tablolarını listele
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n📋 Created tables: {', '.join(tables)}")
        print(f"\n🎉 Database is ready!")

if __name__ == '__main__':
    init_db()
