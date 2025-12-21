from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('conversations')]
    print(f"Columns in conversations table: {columns}")
    
    if 'office_post_id' in columns:
        print("SUCCESS: office_post_id column exists.")
    else:
        print("FAILURE: office_post_id column is MISSING!")
