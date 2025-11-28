import sqlite3

# Veritabanı bağlantısı
conn = sqlite3.connect('tevkil.db')
cursor = conn.cursor()

# İlanlar tablosu oluştur
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ilans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
''')

# Değişiklikleri kaydet ve kapat
conn.commit()
conn.close()
print("Veritabanı oluşturuldu: tevkil.db")