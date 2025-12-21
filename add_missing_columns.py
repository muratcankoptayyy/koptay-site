import os
from sqlalchemy import text
from app import app, db

def add_missing_columns():
    with app.app_context():
        print("Checking for missing columns...")
        
        # Check is_verified
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT is_verified FROM users LIMIT 1"))
                print("✅ is_verified column exists.")
        except Exception as e:
            print("❌ is_verified column missing. Adding it...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"))
                    conn.commit()
                print("✅ is_verified column added successfully.")
            except Exception as e2:
                print(f"❌ Failed to add is_verified column: {e2}")

        # Check is_active
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT is_active FROM users LIMIT 1"))
                print("✅ is_active column exists.")
        except Exception as e:
            print("❌ is_active column missing. Adding it...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
                    conn.commit()
                print("✅ is_active column added successfully.")
            except Exception as e2:
                print(f"❌ Failed to add is_active column: {e2}")

        # Check is_admin
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT is_admin FROM users LIMIT 1"))
                print("✅ is_admin column exists.")
        except Exception as e:
            print("❌ is_admin column missing. Adding it...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
                    conn.commit()
                print("✅ is_admin column added successfully.")
            except Exception as e2:
                print(f"❌ Failed to add is_admin column: {e2}")

        # Check notifications table columns
        print("\nChecking notifications table...")
        
        # Check related_job_post_id
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT related_job_post_id FROM notifications LIMIT 1"))
                print("✅ related_job_post_id column exists.")
        except Exception as e:
            print("❌ related_job_post_id column missing. Adding it...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN related_job_post_id INTEGER REFERENCES job_posts(id)"))
                    conn.commit()
                print("✅ related_job_post_id column added successfully.")
            except Exception as e2:
                print(f"❌ Failed to add related_job_post_id column: {e2}")

        # Check related_post_id
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT related_post_id FROM notifications LIMIT 1"))
                print("✅ related_post_id column exists.")
        except Exception as e:
            print("❌ related_post_id column missing. Adding it...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN related_post_id INTEGER REFERENCES tevkil_posts(id)"))
                    conn.commit()
                print("✅ related_post_id column added successfully.")
            except Exception as e2:
                print(f"❌ Failed to add related_post_id column: {e2}")

        # Check related_user_id
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT related_user_id FROM notifications LIMIT 1"))
                print("✅ related_user_id column exists.")
        except Exception as e:
            print("❌ related_user_id column missing. Adding it...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE notifications ADD COLUMN related_user_id INTEGER REFERENCES users(id)"))
                    conn.commit()
                print("✅ related_user_id column added successfully.")
            except Exception as e2:
                print(f"❌ Failed to add related_user_id column: {e2}")

if __name__ == "__main__":
    add_missing_columns()
