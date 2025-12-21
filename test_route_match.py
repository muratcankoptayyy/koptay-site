from app import app
from flask import url_for

with app.test_request_context():
    url = url_for('messages.start_conversation', user_id=9, post_type='office', post_id=1)
    print(f"Generated URL: {url}")
    
    path = url.split('?')[0]
    print(f"Testing Path: {path}")

    # Match the URL
    adapter = app.url_map.bind('localhost')
    try:
        match = adapter.match(path)
        print(f"Matched Route: {match}")
    except Exception as e:
        print(f"Match Failed: {e}")
