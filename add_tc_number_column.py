import sqlite3
import os

# Database path
db_path = os.path.join('instance', 'tevkil.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'tc_number' not in columns:
        print("Adding tc_number column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN tc_number VARCHAR(11)")
        conn.commit()
        print("Column added successfully.")
    else:
        print("Column tc_number already exists.")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
