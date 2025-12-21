from app import app
from models import db, OfficePost, User

with app.app_context():
    posts = OfficePost.query.all()
    print(f"Found {len(posts)} office posts.")
    for post in posts:
        user = User.query.get(post.user_id)
        if not user:
            print(f"WARNING: Post {post.id} has user_id {post.user_id} which DOES NOT EXIST in users table!")
        else:
            print(f"Post {post.id} belongs to User {user.id} ({user.email}) - OK")
