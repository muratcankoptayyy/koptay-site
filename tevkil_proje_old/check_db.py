import sqlite3

conn = sqlite3.connect('tevkil.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM ilans")
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()