from app import app, db
from sqlalchemy import text

def fix_column_types():
    with app.app_context():
        print("🔧 Fixing column types...")
        
        with db.engine.connect() as conn:
            # tevkil_posts.price -> FLOAT
            try:
                print("Fixing tevkil_posts.price (TEXT -> DOUBLE PRECISION)...")
                # Handle empty strings or non-numeric values if any (convert to NULL)
                conn.execute(text("UPDATE tevkil_posts SET price = NULL WHERE price = ''"))
                conn.execute(text("ALTER TABLE tevkil_posts ALTER COLUMN price TYPE DOUBLE PRECISION USING price::double precision"))
                conn.commit()
                print("✅ Fixed tevkil_posts.price")
            except Exception as e:
                print(f"❌ Failed to fix tevkil_posts.price: {e}")

            # messages.latitude -> FLOAT
            try:
                print("Fixing messages.latitude (TEXT -> DOUBLE PRECISION)...")
                conn.execute(text("UPDATE messages SET latitude = NULL WHERE latitude = ''"))
                conn.execute(text("ALTER TABLE messages ALTER COLUMN latitude TYPE DOUBLE PRECISION USING latitude::double precision"))
                conn.commit()
                print("✅ Fixed messages.latitude")
            except Exception as e:
                print(f"❌ Failed to fix messages.latitude: {e}")

            # messages.longitude -> FLOAT
            try:
                print("Fixing messages.longitude (TEXT -> DOUBLE PRECISION)...")
                conn.execute(text("UPDATE messages SET longitude = NULL WHERE longitude = ''"))
                conn.execute(text("ALTER TABLE messages ALTER COLUMN longitude TYPE DOUBLE PRECISION USING longitude::double precision"))
                conn.commit()
                print("✅ Fixed messages.longitude")
            except Exception as e:
                print(f"❌ Failed to fix messages.longitude: {e}")

            # messages.duration -> INTEGER
            try:
                print("Fixing messages.duration (TEXT -> INTEGER)...")
                conn.execute(text("UPDATE messages SET duration = NULL WHERE duration = ''"))
                conn.execute(text("ALTER TABLE messages ALTER COLUMN duration TYPE INTEGER USING duration::integer"))
                conn.commit()
                print("✅ Fixed messages.duration")
            except Exception as e:
                print(f"❌ Failed to fix messages.duration: {e}")

if __name__ == "__main__":
    fix_column_types()
