
from app import create_app, db
from sqlalchemy import text

app = create_app()

def update_schema():
    with app.app_context():
        with db.engine.connect() as connection:
            # Check if columns exist
            result = connection.execute(text("PRAGMA table_info(tevkil_posts)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'job_type' not in columns:
                print("Adding job_type column...")
                connection.execute(text("ALTER TABLE tevkil_posts ADD COLUMN job_type VARCHAR(50)"))
                
            if 'price' not in columns:
                print("Adding price column...")
                connection.execute(text("ALTER TABLE tevkil_posts ADD COLUMN price FLOAT"))
                
            print("Schema update completed.")

if __name__ == "__main__":
    update_schema()
