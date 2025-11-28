from app import app, db

with app.app_context():
    # Tüm tabloları oluştur
    print("🔧 Tablo oluşturma başlıyor...")
    db.create_all()
    print("✅ Tablolar oluşturuldu!")
    
    # Kontrol et
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"\n📋 Mevcut tablolar ({len(tables)} adet):")
    for table in sorted(tables):
        print(f"  - {table}")
        
    if 'messages' in tables:
        print("\n✅ Messages tablosu başarıyla oluşturuldu!")
        # Kolonları göster
        columns = inspector.get_columns('messages')
        print(f"\n📊 Messages kolonları ({len(columns)} adet):")
        for col in columns:
            print(f"  {col['name']:20} {str(col['type']):15}")
    else:
        print("\n❌ Messages tablosu oluşturulamadı!")
        
    if 'conversations' in tables:
        print("\n✅ Conversations tablosu başarıyla oluşturuldu!")
