
from app import create_app, db
from sqlalchemy import text
import sys

app = create_app()

def fix_schema():
    print("Checking database schema...")
    with app.app_context():
        with db.engine.connect() as connection:
            # Get current columns
            result = connection.execute(text("PRAGMA table_info(tevkil_posts)"))
            columns = [row[1] for row in result.fetchall()]
            print(f"Current columns: {columns}")
            
            # Add job_type if missing
            if 'job_type' not in columns:
                print("Adding job_type column...")
                try:
                    connection.execute(text("ALTER TABLE tevkil_posts ADD COLUMN job_type VARCHAR(50)"))
                    connection.commit()
                    print("job_type column added.")
                except Exception as e:
                    print(f"Error adding job_type: {e}")

            # Add price if missing
            if 'price' not in columns:
                print("Adding price column...")
                try:
                    connection.execute(text("ALTER TABLE tevkil_posts ADD COLUMN price FLOAT"))
                    connection.commit()
                    print("price column added.")
                except Exception as e:
                    print(f"Error adding price: {e}")

            # Verify changes
            result = connection.execute(text("PRAGMA table_info(tevkil_posts)"))
            new_columns = [row[1] for row in result.fetchall()]
            print(f"Updated columns: {new_columns}")
            
            if 'job_type' in new_columns and 'price' in new_columns:
                print("Schema verification: SUCCESS")
            else:
                print("Schema verification: FAILED")

if __name__ == "__main__":
    fix_schema()
