
import sqlite3
import os

def fix_database():
    # Possible database paths
    paths = ['tevkil.db', 'instance/tevkil.db']
    db_path = None
    
    for path in paths:
        if os.path.exists(path):
            db_path = path
            break
            
    if not db_path:
        print("Database file not found!")
        # Create a new one in instance if not found? No, better to fail.
        # But wait, if it doesn't exist, app.py create_all() would create it.
        # Let's assume it exists because the app is running and giving errors about columns.
        return

    print(f"Connecting to database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check columns in tevkil_posts
    cursor.execute("PRAGMA table_info(tevkil_posts)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Add job_type if missing
    if 'job_type' not in columns:
        print("Adding job_type column...")
        try:
            cursor.execute("ALTER TABLE tevkil_posts ADD COLUMN job_type VARCHAR(50)")
            print("job_type added.")
        except Exception as e:
            print(f"Error adding job_type: {e}")

    # Add price if missing
    if 'price' not in columns:
        print("Adding price column...")
        try:
            cursor.execute("ALTER TABLE tevkil_posts ADD COLUMN price FLOAT")
            print("price added.")
        except Exception as e:
            print(f"Error adding price: {e}")
            
    # Add price_min if missing (it should be there but just in case)
    if 'price_min' not in columns:
        print("Adding price_min column...")
        try:
            cursor.execute("ALTER TABLE tevkil_posts ADD COLUMN price_min FLOAT")
        except Exception as e:
            print(f"Error adding price_min: {e}")

    # Add price_max if missing
    if 'price_max' not in columns:
        print("Adding price_max column...")
        try:
            cursor.execute("ALTER TABLE tevkil_posts ADD COLUMN price_max FLOAT")
        except Exception as e:
            print(f"Error adding price_max: {e}")

    conn.commit()
    conn.close()
    print("Database fix completed.")

if __name__ == "__main__":
    fix_database()
