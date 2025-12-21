
from app import app, db
from models import JobPost, JobApplication

with app.app_context():
    print("Creating new tables...")
    db.create_all()
    print("Tables created successfully!")
