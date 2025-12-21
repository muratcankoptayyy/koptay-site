import requests
import json
import os

# Configuration
BASE_URL = "http://127.0.0.1:5000"
EMAIL = "ahmet@example.com"
PASSWORD = "123456"

def print_result(test_name, success, message=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"   Message: {message}")

def login():
    url = f"{BASE_URL}/api/mobile/login"
    payload = {"email": EMAIL, "password": PASSWORD}
    try:
        response = requests.post(url, json=payload)
        print(f"DEBUG: Login Response Status: {response.status_code}")
        print(f"DEBUG: Login Response Body: {response.text[:500]}") # Print first 500 chars
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                token = data.get('token')
                print_result("Login", True)
                return token
            else:
                print_result("Login", False, f"Unexpected response type: {type(data)}")
                return None
        else:
            print_result("Login", False, f"Status: {response.status_code}, Body: {response.text}")
            return None
    except Exception as e:
        print_result("Login", False, str(e))
        return None

def get_posts(token):
    url = f"{BASE_URL}/api/posts"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            posts = response.json().get('posts', [])
            print_result("Get Posts", True, f"Found {len(posts)} posts")
            return posts
        else:
            print_result("Get Posts", False, f"Status: {response.status_code}, Body: {response.text[:500]}")
            return []
    except Exception as e:
        print_result("Get Posts", False, str(e))
        return []

def create_post(token):
    url = f"{BASE_URL}/api/posts"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "title": "API Test Post with Images",
        "description": "This is a test post created by the automated test script to verify image upload functionality.",
        "category": "Test",
        "city": "Istanbul"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            post_id = response.json().get('post_id')
            print_result("Create Post", True, f"Post ID: {post_id}")
            return post_id
        else:
            print_result("Create Post", False, f"Status: {response.status_code}, Body: {response.text}")
            return None
    except Exception as e:
        print_result("Create Post", False, str(e))
        return None

def upload_image(token, post_id):
    url = f"{BASE_URL}/api/posts/{post_id}/images"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a dummy image file
    with open("test_image.txt", "w") as f:
        f.write("This is a dummy image content")
    
    # Rename to .jpg to simulate an image (backend checks extension)
    if os.path.exists("test_image.jpg"):
        os.remove("test_image.jpg")
    os.rename("test_image.txt", "test_image.jpg")
    
    try:
        # Note: requests automatically sets Content-Type for files, but we need to ensure Authorization header is present
        # When using files parameter, requests sends multipart/form-data
        with open('test_image.jpg', 'rb') as img_file:
            files = {'file': ('test_image.jpg', img_file, 'image/jpeg')}
            response = requests.post(url, files=files, headers=headers)
        
        if response.status_code == 201:
            image_data = response.json().get('image')
            print_result("Upload Image", True, f"Image URL: {image_data.get('url')}")
            return image_data.get('id')
        else:
            print_result("Upload Image", False, f"Status: {response.status_code}, Body: {response.text}")
            return None
    except Exception as e:
        print_result("Upload Image", False, str(e))
        return None
    finally:
        # File is closed by with block, safe to remove
        if os.path.exists("test_image.jpg"):
            try:
                os.remove("test_image.jpg")
            except Exception as e:
                print(f"Warning: Could not remove temp file: {e}")

def delete_image(token, image_id):
    url = f"{BASE_URL}/api/posts/images/{image_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print_result("Delete Image", True)
            return True
        else:
            print_result("Delete Image", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Delete Image", False, str(e))
        return False

def main():
    print("🚀 Starting API Tests...\n")
    
    # 1. Login
    token = login()
    if not token:
        print("\n❌ Aborting tests due to login failure.")
        return

    # 2. Get Posts
    get_posts(token)

    # 3. Create Post
    post_id = create_post(token)
    
    if post_id:
        # 4. Upload Image
        image_id = upload_image(token, post_id)
        
        # 5. Delete Image (if upload successful)
        if image_id:
            delete_image(token, image_id)
        
        # Note: Delete Post endpoint is not implemented in API yet
        print("ℹ️  Skipping Delete Post (Endpoint not implemented)")

    print("\n✨ Tests Completed.")

if __name__ == "__main__":
    main()
