from app import app
from models import db, PostImage

with app.app_context():
    try:
        # Create table
        PostImage.__table__.create(db.session.bind)
        print("✅ PostImage table created successfully")
    except Exception as e:
        print(f"❌ Error creating table: {e}")
