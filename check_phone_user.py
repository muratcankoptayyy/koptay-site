
from app import app
from models import User

with app.app_context():
    print("Searching for users with phone number containing '3054037'...")
    users = User.query.filter(User.phone.like('%3054037%')).all()
    
    if users:
        for user in users:
            print(f"Found User: ID={user.id}, Name={user.full_name}, Email={user.email}, Phone={user.phone}")
    else:
        print("No user found with this phone number.")
        
    print("\nListing all users with phone numbers:")
    all_users = User.query.filter(User.phone != None).all()
    for user in all_users:
        print(f"User: {user.full_name}, Phone: {user.phone}")
