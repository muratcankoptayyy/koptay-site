from app import app, db
from sqlalchemy import inspect

def inspect_database():
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"Found {len(tables)} tables: {', '.join(tables)}\n")
        
        tables_to_check = ['users', 'tevkil_posts', 'notifications', 'conversations', 'messages', 'job_posts', 'office_posts']
        
        for table in tables_to_check:
            if table in tables:
                print(f"--- Table: {table} ---")
                columns = inspector.get_columns(table)
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
                print("")
            else:
                print(f"❌ Table {table} NOT FOUND!")

if __name__ == "__main__":
    inspect_database()
