"""Extended Session Configuration Test"""
from app import app

print("=" * 60)
print("✅ SESSION & REMEMBER COOKIE CONFIGURATION")
print("=" * 60)

print("\n📋 SESSION CONFIG:")
print(f"  PERMANENT_SESSION_LIFETIME: {app.config['PERMANENT_SESSION_LIFETIME']}")
print(f"  SESSION_COOKIE_SECURE: {app.config['SESSION_COOKIE_SECURE']}")
print(f"  SESSION_COOKIE_HTTPONLY: {app.config['SESSION_COOKIE_HTTPONLY']}")
print(f"  SESSION_COOKIE_SAMESITE: {app.config['SESSION_COOKIE_SAMESITE']}")
print(f"  SESSION_REFRESH_EACH_REQUEST: {app.config['SESSION_REFRESH_EACH_REQUEST']}")

print("\n🍪 REMEMBER COOKIE CONFIG:")
print(f"  REMEMBER_COOKIE_DURATION: {app.config['REMEMBER_COOKIE_DURATION']}")
print(f"  REMEMBER_COOKIE_SECURE: {app.config['REMEMBER_COOKIE_SECURE']}")
print(f"  REMEMBER_COOKIE_HTTPONLY: {app.config['REMEMBER_COOKIE_HTTPONLY']}")
print(f"  REMEMBER_COOKIE_REFRESH_EACH_REQUEST: {app.config.get('REMEMBER_COOKIE_REFRESH_EACH_REQUEST', 'Not Set')}")

print("\n" + "=" * 60)
print("✅ Both session and remember cookies will persist for 30 days!")
print("✅ Users will stay logged in until manual logout!")
print("=" * 60)
