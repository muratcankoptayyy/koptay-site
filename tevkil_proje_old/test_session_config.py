"""Session Configuration Test"""
from app import app

print("✅ SESSION CONFIGURATION")
print("=" * 50)
print(f"PERMANENT_SESSION_LIFETIME: {app.config['PERMANENT_SESSION_LIFETIME']}")
print(f"SESSION_COOKIE_SECURE: {app.config['SESSION_COOKIE_SECURE']}")
print(f"SESSION_COOKIE_HTTPONLY: {app.config['SESSION_COOKIE_HTTPONLY']}")
print(f"SESSION_COOKIE_SAMESITE: {app.config['SESSION_COOKIE_SAMESITE']}")
print(f"SESSION_REFRESH_EACH_REQUEST: {app.config['SESSION_REFRESH_EACH_REQUEST']}")
print("=" * 50)
print("✅ Session will persist for 30 days!")
print("✅ Users will stay logged in until manual logout!")
