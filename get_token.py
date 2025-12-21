
import sqlite3

conn = sqlite3.connect('instance/tevkil.db')
cursor = conn.cursor()
cursor.execute("SELECT email, api_token FROM users LIMIT 1")
user = cursor.fetchone()
if user:
    print(f"User: {user[0]}")
    print(f"Token: {user[1]}")
else:
    print("No users found")
conn.close()
