import os
from flask import Flask
from sqlalchemy import text, inspect
from app import app, db
import models

from sqlalchemy.types import Integer, String, Text, Boolean, DateTime, Date, Float, JSON

def get_sql_type(column):
    """Maps SQLAlchemy types to PostgreSQL types."""
    try:
        col_type = column.type
        if isinstance(col_type, Integer):
            return "INTEGER"
        elif isinstance(col_type, String):
            if col_type.length:
                return f"VARCHAR({col_type.length})"
            return "VARCHAR"
        elif isinstance(col_type, Text):
            return "TEXT"
        elif isinstance(col_type, Boolean):
            return "BOOLEAN"
        elif isinstance(col_type, DateTime):
            return "TIMESTAMP"
        elif isinstance(col_type, Date):
            return "DATE"
        elif isinstance(col_type, Float):
            return "DOUBLE PRECISION"
        elif isinstance(col_type, JSON):
            return "JSON"
        
        # Fallback to string matching if isinstance fails (e.g. custom types)
        type_str = str(col_type).upper()
        if 'INTEGER' in type_str or 'INT' in type_str:
            return "INTEGER"
        elif 'VARCHAR' in type_str or 'STRING' in type_str:
            return "VARCHAR"
        elif 'TEXT' in type_str:
            return "TEXT"
        elif 'BOOLEAN' in type_str or 'BOOL' in type_str:
            return "BOOLEAN"
        elif 'TIMESTAMP' in type_str or 'DATETIME' in type_str:
            return "TIMESTAMP"
        elif 'DATE' in type_str:
            return "DATE"
        elif 'FLOAT' in type_str or 'DOUBLE' in type_str:
            return "DOUBLE PRECISION"
        elif 'JSON' in type_str:
            return "JSON"
            
        return "TEXT" # Ultimate Fallback
    except Exception as e:
        print(f"Error determining type for {column.name}: {e}")
        return "TEXT"

def sync_database():
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Get all models from SQLAlchemy
        # We access the registry to get all classes
        model_classes = [cls for cls in db.Model.registry._class_registry.values() 
                         if isinstance(cls, type) and issubclass(cls, db.Model) and hasattr(cls, '__tablename__')]
        
        print(f"Found {len(model_classes)} models.")

        for model in model_classes:
            table_name = model.__tablename__
            print(f"\nChecking table: {table_name}")

            if not inspector.has_table(table_name):
                print(f"❌ Table {table_name} does not exist. Creating...")
                try:
                    model.__table__.create(db.engine)
                    print(f"✅ Table {table_name} created.")
                except Exception as e:
                    print(f"❌ Failed to create table {table_name}: {e}")
                continue

            # Get existing columns in the database
            existing_columns = {col['name']: col for col in inspector.get_columns(table_name)}
            
            # Check each column defined in the model
            for column in model.__table__.columns:
                column_name = column.name
                
                if column_name not in existing_columns:
                    print(f"❌ Column {column_name} missing in {table_name}. Adding...")
                    
                    sql_type = get_sql_type(column)
                    
                    # Determine default value if possible (simple cases)
                    default_clause = ""
                    if column.default:
                        if column.default.arg is not None:
                            if isinstance(column.default.arg, bool):
                                default_clause = f" DEFAULT {str(column.default.arg).upper()}"
                            elif isinstance(column.default.arg, (int, float)):
                                default_clause = f" DEFAULT {column.default.arg}"
                            elif isinstance(column.default.arg, str):
                                default_clause = f" DEFAULT '{column.default.arg}'"
                    
                    # Construct ALTER TABLE statement
                    alter_stmt = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_type}{default_clause}"
                    
                    # Add Foreign Key constraint if applicable
                    if column.foreign_keys:
                        for fk in column.foreign_keys:
                            ref_table = fk.column.table.name
                            ref_col = fk.column.name
                            alter_stmt += f" REFERENCES {ref_table}({ref_col})"
                            break # Only handle one FK for now
                    
                    try:
                        with db.engine.connect() as conn:
                            conn.execute(text(alter_stmt))
                            conn.commit()
                        print(f"✅ Column {column_name} added to {table_name}.")
                    except Exception as e:
                        print(f"❌ Failed to add column {column_name} to {table_name}: {e}")
                else:
                    # print(f"✓ Column {column_name} exists.")
                    pass

if __name__ == "__main__":
    sync_database()
