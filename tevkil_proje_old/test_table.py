import sqlite3

conn = sqlite3.connect('tevkil.db')
cursor = conn.cursor()

# Messages tablosu var mı?
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='messages'
""")
result = cursor.fetchone()

if result:
    print(f"✅ Messages tablosu bulundu: {result[0]}")
    
    # Kolonları listele
    cursor.execute("PRAGMA table_info(messages)")
    columns = cursor.fetchall()
    print(f"\n📊 Mevcut kolonlar ({len(columns)} adet):")
    for col in columns:
        print(f"  {col[1]:25} {col[2]:15}")
else:
    print("❌ Messages tablosu bulunamadı!")

conn.close()
