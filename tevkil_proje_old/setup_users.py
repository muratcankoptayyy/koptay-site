import sqlite3
from werkzeug.security import generate_password_hash

# Veritabanı bağlantısı
conn = sqlite3.connect('tevkil.db')
cursor = conn.cursor()

# Kullanıcılar tablosu oluştur
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

# Örnek kullanıcı ekle (şifre: "sifre123")
cursor.execute(
    "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
    ("avukat1", generate_password_hash("sifre123"))
)

conn.commit()
conn.close()
print("Kullanıcılar tablosu oluşturuldu, örnek kullanıcı eklendi.")