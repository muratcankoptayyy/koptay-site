from app import app
from models import db, PostImage

with app.app_context():
    try:
        # Try to query the table
        count = PostImage.query.count()
        print(f"✅ PostImage table exists. Count: {count}")
    except Exception as e:
        print(f"❌ Error querying table: {e}")
        # Try creating it again using create_all which is safer
        db.create_all()
        print("✅ db.create_all() executed")
