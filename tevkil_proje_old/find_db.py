from app import app, db
import os

with app.app_context():
    # Gerçek database path'ini al
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"📌 Database URI: {db_uri}")
    
    # Database engine'den gerçek path
    if hasattr(db.engine.url, 'database'):
        db_path = db.engine.url.database
        print(f"📂 Database dosyası: {db_path}")
        
        # Dosya var mı?
        if os.path.exists(db_path):
            print(f"✅ Dosya mevcut ({os.path.getsize(db_path)} bytes)")
        else:
            print("❌ Dosya bulunamadı!")
    
    # Tablolar
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\n📋 Tablolar: {', '.join(sorted(tables))}")
