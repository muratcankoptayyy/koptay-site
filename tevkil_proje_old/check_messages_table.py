import sqlite3

conn = sqlite3.connect('tevkil.db')
cursor = conn.cursor()

# Tabloları listele
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("📋 Tablolar:")
for table in tables:
    print(f"  - {table[0]}")

# Messages tablosunu kontrol et
print("\n📊 Messages tablosu kolonları:")
try:
    cursor.execute("PRAGMA table_info(messages)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]:20} {col[2]:15} {'NOT NULL' if col[3] else ''}")
except:
    print("  ❌ Messages tablosu bulunamadı")

conn.close()
