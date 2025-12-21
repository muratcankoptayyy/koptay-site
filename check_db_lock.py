
import sqlite3
import os
import time

def check_db_lock():
    db_path = 'instance/tevkil.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    print(f"Checking database at {db_path}...")
    try:
        conn = sqlite3.connect(db_path, timeout=5)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        mode = cursor.fetchone()
        print(f"Journal mode: {mode}")
        
        start = time.time()
        cursor.execute("SELECT count(*) FROM users")
        count = cursor.fetchone()[0]
        end = time.time()
        
        print(f"Successfully read {count} users in {end-start:.4f} seconds.")
        conn.close()
        print("Database is accessible and not locked.")
    except Exception as e:
        print(f"ERROR: Database seems locked or inaccessible: {e}")

if __name__ == "__main__":
    check_db_lock()
