#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deployment Hazırlık Scripti
Bu script deployment öncesi kontrolleri yapar
"""

import os
import sys
from app import app, db, User

def check_deployment_readiness():
    """Deployment için hazırlık kontrolü"""
    
    print("🔍 Deployment Hazırlık Kontrolleri\n")
    print("=" * 50)
    
    checks = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # 1. Debug mode kontrolü
    if app.config.get('DEBUG'):
        checks['warnings'].append("⚠️  DEBUG mode hala aktif! Production'da kapatın.")
    else:
        checks['passed'].append("✅ DEBUG mode kapalı")
    
    # 2. Secret key kontrolü
    if app.config.get('SECRET_KEY') == 'dev':
        checks['failed'].append("❌ SECRET_KEY güvenli değil! Değiştirin.")
    else:
        checks['passed'].append("✅ SECRET_KEY ayarlanmış")
    
    # 3. Database kontrolü
    try:
        with app.app_context():
            # Test sorgusu
            user_count = User.query.count()
            checks['passed'].append(f"✅ Database çalışıyor ({user_count} kullanıcı)")
    except Exception as e:
        checks['failed'].append(f"❌ Database hatası: {str(e)}")
    
    # 4. Gerekli dosyalar kontrolü
    required_files = [
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        'wsgi.py',
        '.gitignore'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            checks['passed'].append(f"✅ {file} mevcut")
        else:
            checks['warnings'].append(f"⚠️  {file} bulunamadı")
    
    # 5. Templates kontrolü
    templates = ['base.html', 'login.html', 'register.html', 'dashboard.html']
    missing_templates = []
    for template in templates:
        if not os.path.exists(f'templates/{template}'):
            missing_templates.append(template)
    
    if missing_templates:
        checks['warnings'].append(f"⚠️  Eksik template'ler: {', '.join(missing_templates)}")
    else:
        checks['passed'].append(f"✅ Tüm ana template'ler mevcut")
    
    # 6. Static dosyalar kontrolü
    if os.path.exists('static'):
        static_files = os.listdir('static')
        checks['passed'].append(f"✅ Static klasörü mevcut ({len(static_files)} dosya)")
    else:
        checks['warnings'].append("⚠️  Static klasörü bulunamadı")
    
    # Sonuçları yazdır
    print("\n📊 SONUÇLAR:")
    print("=" * 50)
    
    if checks['passed']:
        print("\n✅ BAŞARILI KONTROLLER:")
        for check in checks['passed']:
            print(f"  {check}")
    
    if checks['warnings']:
        print("\n⚠️  UYARILAR:")
        for warning in checks['warnings']:
            print(f"  {warning}")
    
    if checks['failed']:
        print("\n❌ BAŞARISIZ KONTROLLER:")
        for fail in checks['failed']:
            print(f"  {fail}")
    
    print("\n" + "=" * 50)
    
    if checks['failed']:
        print("\n🚫 Deployment için HAZIR DEĞİL!")
        print("Lütfen başarısız kontrolleri düzeltin.\n")
        return False
    elif checks['warnings']:
        print("\n⚠️  Deployment yapılabilir ama uyarıları kontrol edin.\n")
        return True
    else:
        print("\n✅ Deployment için HAZIR!\n")
        return True

def print_deployment_instructions():
    """Deployment talimatlarını yazdır"""
    
    print("\n📋 DEPLOYMENT ADIMLARI:\n")
    print("=" * 50)
    print("""
1️⃣  PythonAnywhere Deployment:
   - https://www.pythonanywhere.com
   - Ücretsiz hesap oluşturun
   - Bash console açın
   - git clone ile projeyi klonlayın
   - Virtual environment kurun
   - WSGI dosyasını yapılandırın
   - Detaylar için: DEPLOYMENT_GUIDE.md

2️⃣  Render.com Deployment:
   - https://render.com
   - GitHub hesabı ile giriş yapın
   - New Web Service oluşturun
   - Repository'nizi bağlayın
   - Otomatik deploy başlayacak

3️⃣  Railway Deployment:
   - https://railway.app
   - GitHub ile giriş yapın
   - New Project → Deploy from GitHub
   - Repository seçin
   - Otomatik deploy

📚 Daha fazla bilgi: DEPLOYMENT_GUIDE.md dosyasına bakın
    """)
    print("=" * 50)

if __name__ == '__main__':
    print("\n🚀 Ulusal Tevkil Ağı Projesi - Deployment Hazırlık\n")
    
    ready = check_deployment_readiness()
    
    if ready:
        print_deployment_instructions()
        
        print("\n💡 ÖNERİ:")
        print("Deployment öncesi son kontroller:")
        print("1. Tüm değişiklikler commit edildi mi?")
        print("2. GitHub'a push yapıldı mı?")
        print("3. .env dosyası .gitignore'da mı?")
        print("4. Production SECRET_KEY hazır mı?")
        print("5. CORS ayarları production domain'e göre güncellendi mi?\n")
    
    sys.exit(0 if ready else 1)
