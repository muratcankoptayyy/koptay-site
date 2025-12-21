
import sqlite3
import os

def add_columns():
    db_path = os.path.join('instance', 'tevkil.db')
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Add latitude column
        try:
            cursor.execute("ALTER TABLE office_posts ADD COLUMN latitude FLOAT")
            print("Added latitude column")
        except sqlite3.OperationalError as e:
            print(f"latitude column might already exist: {e}")

        # Add longitude column
        try:
            cursor.execute("ALTER TABLE office_posts ADD COLUMN longitude FLOAT")
            print("Added longitude column")
        except sqlite3.OperationalError as e:
            print(f"longitude column might already exist: {e}")

        conn.commit()
        print("Migration completed successfully")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_columns()
