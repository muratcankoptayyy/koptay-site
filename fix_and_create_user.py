
from app import app, db
from models import User
from sqlalchemy import text

# app = create_app() # Removed since app is imported directly

def fix_schema_and_create_user():
    with app.app_context():
        # 1. Fix Schema
        with db.engine.connect() as connection:
            # Check columns in tevkil_posts
            try:
                result = connection.execute(text("PRAGMA table_info(tevkil_posts)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'job_type' not in columns:
                    print("Adding job_type column...")
                    connection.execute(text("ALTER TABLE tevkil_posts ADD COLUMN job_type VARCHAR(50)"))
                    
                if 'price' not in columns:
                    print("Adding price column...")
                    connection.execute(text("ALTER TABLE tevkil_posts ADD COLUMN price FLOAT"))
                
                # Commit schema changes
                connection.commit()
                print("Schema check/update completed.")
            except Exception as e:
                print(f"Schema update error: {e}")

        # 2. Create/Update User
        try:
            email = "koptaymuratcan@gmail.com"
            password = "giriş"
            
            user = User.query.filter_by(email=email).first()
            
            if user:
                print(f"User {email} exists. Updating password...")
                user.set_password(password)
                user.is_active = True
                user.is_verified = True
            else:
                print(f"Creating user {email}...")
                user = User(
                    email=email,
                    full_name="Murat Can Koptay",
                    bar_association="İstanbul Barosu",
                    city="İstanbul",
                    is_active=True,
                    is_verified=True
                )
                user.set_password(password)
                db.session.add(user)
            
            db.session.commit()
            print(f"User {email} ready with password '{password}'.")
            
        except Exception as e:
            print(f"User creation error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_schema_and_create_user()
