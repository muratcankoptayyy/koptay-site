
import sqlite3
from app import app, db
from models import JobApplication, OfficePost, OfficePostImage

def fix_database():
    with app.app_context():
        # 1. Check if job_applications table exists and has post_id
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'job_applications' in tables:
            print("Checking job_applications table...")
            columns = [c['name'] for c in inspector.get_columns('job_applications')]
            if 'post_id' not in columns:
                print("Column 'post_id' missing in job_applications. Dropping table to recreate...")
                # Drop the table using raw SQL to avoid dependency issues
                with db.engine.connect() as conn:
                    conn.execute(db.text("DROP TABLE job_applications"))
                    conn.commit()
                print("Table dropped.")
            else:
                print("job_applications table looks correct.")
        
        # 2. Recreate missing tables
        print("Creating missing tables...")
        db.create_all()
        print("Database schema updated.")

if __name__ == "__main__":
    fix_database()
