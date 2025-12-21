
import sqlite3
from app import app, db
from sqlalchemy import text

def update_database():
    with app.app_context():
        engine = db.engine
        connection = engine.connect()
        
        # 1. Update Conversation table
        print("Checking Conversation table...")
        try:
            # Check if columns exist
            result = connection.execute(text("PRAGMA table_info(conversations)"))
            columns = [row[1] for row in result]
            
            if 'job_post_id' not in columns:
                print("Adding job_post_id to conversations...")
                connection.execute(text("ALTER TABLE conversations ADD COLUMN job_post_id INTEGER REFERENCES job_posts(id)"))
            
            if 'office_post_id' not in columns:
                print("Adding office_post_id to conversations...")
                connection.execute(text("ALTER TABLE conversations ADD COLUMN office_post_id INTEGER REFERENCES office_posts(id)"))
                
        except Exception as e:
            print(f"Error updating conversations: {e}")

        # 2. Update Message table
        print("Checking Message table...")
        try:
            # Check if columns exist
            result = connection.execute(text("PRAGMA table_info(messages)"))
            columns = [row[1] for row in result]
            
            if 'latitude' not in columns:
                print("Adding latitude to messages...")
                connection.execute(text("ALTER TABLE messages ADD COLUMN latitude FLOAT"))
                
            if 'longitude' not in columns:
                print("Adding longitude to messages...")
                connection.execute(text("ALTER TABLE messages ADD COLUMN longitude FLOAT"))
                
            if 'duration' not in columns:
                print("Adding duration to messages...")
                connection.execute(text("ALTER TABLE messages ADD COLUMN duration INTEGER")) # Seconds
                
        except Exception as e:
            print(f"Error updating messages: {e}")

        connection.commit()
        connection.close()
        print("Database update completed.")

if __name__ == "__main__":
    update_database()
