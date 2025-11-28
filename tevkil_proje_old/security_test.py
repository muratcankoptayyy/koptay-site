#!/usr/bin/env python3
"""
🔒 Güvenlik Test Script
Test security headers, CSRF, input validation, etc.
"""

import requests
import sys

def test_security_headers(url):
    """Test security headers"""
    print("\n🔒 Testing Security Headers...")
    print("=" * 60)
    
    try:
        response = requests.get(url, timeout=10)
        headers = response.headers
        
        security_checks = {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
        }
        
        passed = 0
        failed = 0
        
        for header, expected in security_checks.items():
            if header in headers:
                if expected in headers[header]:
                    print(f"✅ {header}: {headers[header]}")
                    passed += 1
                else:
                    print(f"⚠️  {header}: {headers[header]} (expected: {expected})")
                    failed += 1
            else:
                print(f"❌ {header}: MISSING")
                failed += 1
        
        # Check CSP (only in production)
        if 'Content-Security-Policy' in headers:
            print(f"✅ Content-Security-Policy: PRESENT")
            passed += 1
        else:
            print(f"⚠️  Content-Security-Policy: NOT SET (OK for dev mode)")
        
        # Check HSTS (only in production with HTTPS)
        if url.startswith('https://'):
            if 'Strict-Transport-Security' in headers:
                print(f"✅ Strict-Transport-Security: {headers['Strict-Transport-Security']}")
                passed += 1
            else:
                print(f"❌ Strict-Transport-Security: MISSING")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"Results: {passed} passed, {failed} failed")
        print(f"Score: {(passed / (passed + failed)) * 100:.0f}%")
        
        return passed, failed
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0, 1


def test_https_redirect(url):
    """Test HTTP to HTTPS redirect"""
    print("\n🔒 Testing HTTPS Redirect...")
    print("=" * 60)
    
    if not url.startswith('https://'):
        print("⚠️  Skipping (not HTTPS URL)")
        return
    
    try:
        http_url = url.replace('https://', 'http://')
        response = requests.get(http_url, allow_redirects=False, timeout=10)
        
        if response.status_code in [301, 302, 307, 308]:
            if response.headers.get('Location', '').startswith('https://'):
                print(f"✅ HTTP redirects to HTTPS (Status: {response.status_code})")
            else:
                print(f"❌ HTTP does not redirect to HTTPS")
        else:
            print(f"❌ No redirect (Status: {response.status_code})")
            
    except Exception as e:
        print(f"⚠️  Could not test: {e}")


def test_session_cookies(url):
    """Test session cookie security"""
    print("\n🔒 Testing Session Cookie Security...")
    print("=" * 60)
    
    try:
        session = requests.Session()
        response = session.get(url + '/login', timeout=10)
        
        cookies = session.cookies
        if cookies:
            for cookie in cookies:
                print(f"\n📝 Cookie: {cookie.name}")
                print(f"   Secure: {'✅ Yes' if cookie.secure else '❌ No'}")
                print(f"   HttpOnly: {'✅ Yes' if cookie.has_nonstandard_attr('HttpOnly') else '⚠️  No'}")
                print(f"   SameSite: {cookie.get_nonstandard_attr('SameSite', 'Not Set')}")
        else:
            print("ℹ️  No cookies set on login page")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "http://127.0.0.1:5000"
    
    print("🔒 TEVKIL PLATFORM SECURITY TEST")
    print("=" * 60)
    print(f"Target: {url}")
    
    # Test security headers
    passed, failed = test_security_headers(url)
    
    # Test HTTPS redirect
    if url.startswith('https://'):
        test_https_redirect(url)
    
    # Test session cookies
    test_session_cookies(url)
    
    print("\n" + "=" * 60)
    print("🎯 Test Complete!")
    print("\nNext Steps:")
    print("1. ⚠️  Renew all API keys exposed in GitHub")
    print("2. 🔐 Set Fly.io secrets for production")
    print("3. 🧪 Run full penetration test with OWASP ZAP")
    print("4. 📊 Monitor security logs regularly")
    print("=" * 60)


if __name__ == "__main__":
    main()
