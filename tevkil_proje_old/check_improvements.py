#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Konuşulup Yapılmayan İyileştirmeler - Kontrol Listesi
"""

import os
os.environ['DEV_MODE'] = '1'

from app import app, db
from models import User

print("=" * 80)
print("📋 KONUŞULUP YAPILMAYAN İYİLEŞTİRMELER")
print("=" * 80)

print("\n🔍 KONTROL EDİLİYOR...")
print("-" * 80)

issues = []
suggestions = []

# 1. User.is_verified alanı kontrolü
print("\n1️⃣  User.is_verified alanı kontrolü...")
try:
    with app.app_context():
        test_user = User.query.first()
        if hasattr(test_user, 'is_verified'):
            print("   ✅ is_verified alanı mevcut")
        else:
            print("   ❌ is_verified alanı eksik")
            issues.append({
                'title': 'User.is_verified alanı eksik',
                'severity': 'Minor',
                'impact': 'Kullanıcı doğrulama sistemi çalışmıyor',
                'fix': 'models.py dosyasına is_verified = db.Column(db.Boolean, default=False) ekle'
            })
except Exception as e:
    print(f"   ⚠️  Hata: {e}")

# 2. Kalan route'ların blueprint'lere taşınması
print("\n2️⃣  Kalan route'lar blueprint'lere taşınabilir mi?")
app_routes = [r for r in app.url_map.iter_rules() if '.' not in r.endpoint and r.endpoint != 'static']
if len(app_routes) > 0:
    print(f"   ⏭️  {len(app_routes)} route hala app.py'de (opsiyonel)")
    suggestions.append({
        'title': f'{len(app_routes)} route blueprint\'e taşınabilir',
        'priority': 'Low',
        'benefit': 'Daha iyi kod organizasyonu',
        'routes': ['settings (12)', 'notifications (5)', 'security (4)', 'messages (3)', 'whatsapp (2)', 'other (2)']
    })
else:
    print("   ✅ Tüm route'lar blueprint'lerde")

# 3. Unit testler
print("\n3️⃣  Unit test coverage...")
import os
test_files = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.startswith('test_') and file.endswith('.py'):
            test_files.append(file)

print(f"   📝 {len(test_files)} test dosyası bulundu")
if len(test_files) < 7:
    suggestions.append({
        'title': 'Blueprint testleri eklenebilir',
        'priority': 'Medium',
        'benefit': 'Kod güvenilirliği artar',
        'action': 'Her blueprint için test_<blueprint>_routes.py dosyası oluştur'
    })

# 4. API Documentation
print("\n4️⃣  API Dokümantasyonu...")
api_files = ['swagger.json', 'openapi.yaml', 'api_docs.md']
has_api_docs = any(os.path.exists(f) for f in api_files)
if not has_api_docs:
    print("   ⏭️  API dokümantasyonu yok (opsiyonel)")
    suggestions.append({
        'title': 'API Swagger/OpenAPI dokümantasyonu',
        'priority': 'Low',
        'benefit': 'Mobil geliştiriciler için daha kolay entegrasyon',
        'action': 'Flask-RESTX veya Flask-Swagger ile otomatik dokümantasyon'
    })
else:
    print("   ✅ API dokümantasyonu mevcut")

# 5. Environment variables (.env dosyası)
print("\n5️⃣  Environment variables kontrolü...")
env_file = '.env'
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
        required_vars = ['FLASK_SECRET_KEY', 'DATABASE_URL', 'MAIL_USERNAME', 'MAIL_PASSWORD']
        missing_vars = [var for var in required_vars if var not in env_content]
        
        if missing_vars:
            print(f"   ⚠️  Eksik environment variables: {', '.join(missing_vars)}")
            issues.append({
                'title': f'Eksik .env değişkenleri: {", ".join(missing_vars)}',
                'severity': 'Medium',
                'impact': 'Production deployment sorunları',
                'fix': 'Production için .env dosyasını tamamla'
            })
        else:
            print("   ✅ Temel environment variables mevcut")
else:
    print("   ⚠️  .env dosyası yok")
    issues.append({
        'title': '.env dosyası eksik',
        'severity': 'Medium',
        'impact': 'Production deployment sorunları',
        'fix': '.env.example dosyasından .env oluştur'
    })

# 6. Database migrations (Alembic)
print("\n6️⃣  Database migrations kontrolü...")
migrations_folder = 'migrations'
if os.path.exists(migrations_folder):
    print("   ✅ Alembic migrations mevcut")
else:
    print("   ⏭️  Alembic migrations yok (opsiyonel)")
    suggestions.append({
        'title': 'Alembic database migrations',
        'priority': 'Medium',
        'benefit': 'Veritabanı değişikliklerini güvenle yönet',
        'action': 'flask db init && flask db migrate && flask db upgrade'
    })

# 7. Error logging
print("\n7️⃣  Error logging sistemi...")
try:
    from utils.logger import get_logger
    print("   ✅ Logger sistemi mevcut")
except:
    print("   ❌ Logger sistemi eksik")
    issues.append({
        'title': 'Centralized logging sistemi eksik',
        'severity': 'Low',
        'impact': 'Hata takibi zorlaşır',
        'fix': 'Python logging modülü ile merkezi log sistemi kur'
    })

# 8. Rate limiting
print("\n8️⃣  Rate limiting kontrolü...")
try:
    from tevkil.extensions import limiter
    print("   ✅ Rate limiter mevcut")
except:
    print("   ⚠️  Rate limiter eksik")
    issues.append({
        'title': 'Rate limiting eksik',
        'severity': 'Medium',
        'impact': 'API abuse riski',
        'fix': 'Flask-Limiter ekle'
    })

# 9. CSRF Protection
print("\n9️⃣  CSRF protection kontrolü...")
try:
    from tevkil.extensions import csrf
    print("   ✅ CSRF protection mevcut")
except:
    print("   ❌ CSRF protection eksik")
    issues.append({
        'title': 'CSRF protection eksik',
        'severity': 'High',
        'impact': 'Güvenlik riski',
        'fix': 'Flask-WTF CSRF protection ekle'
    })

# 10. Code documentation
print("\n🔟  Code documentation...")
files_checked = 0
files_with_docstrings = 0
for root, dirs, files in os.walk('blueprints'):
    for file in files:
        if file.endswith('.py') and not file.startswith('__'):
            files_checked += 1
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if '"""' in content or "'''" in content:
                    files_with_docstrings += 1

coverage = (files_with_docstrings / files_checked * 100) if files_checked > 0 else 0
print(f"   📊 Docstring coverage: {coverage:.1f}% ({files_with_docstrings}/{files_checked})")
if coverage < 80:
    suggestions.append({
        'title': 'Docstring coverage artırılabilir',
        'priority': 'Low',
        'benefit': 'Kod okunabilirliği artar',
        'action': 'Her fonksiyon için docstring ekle'
    })

print("\n" + "=" * 80)
print("📊 ÖZET")
print("=" * 80)

if issues:
    print(f"\n❌ {len(issues)} SORUN BULUNDU:")
    print("-" * 80)
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. {issue['title']}")
        print(f"   Önem: {issue['severity']}")
        print(f"   Etki: {issue['impact']}")
        print(f"   Çözüm: {issue['fix']}")
else:
    print("\n✅ KRİTİK SORUN YOK!")

if suggestions:
    print(f"\n\n💡 {len(suggestions)} İYİLEŞTİRME ÖNERİSİ:")
    print("-" * 80)
    for i, sug in enumerate(suggestions, 1):
        print(f"\n{i}. {sug['title']}")
        print(f"   Öncelik: {sug['priority']}")
        print(f"   Fayda: {sug['benefit']}")
        if 'action' in sug:
            print(f"   Aksiyon: {sug['action']}")
        if 'routes' in sug:
            print(f"   Detay: {', '.join(sug['routes'])}")
else:
    print("\n\n✅ TÜM ÖNERİLER UYGULANMIŞ!")

print("\n" + "=" * 80)
print("🎯 TAVSİYE EDİLEN SONRAKI ADIMLAR:")
print("=" * 80)

priority_actions = []

# Kritik sorunları önceliklendir
critical_issues = [i for i in issues if i['severity'] in ['High', 'Critical']]
if critical_issues:
    for issue in critical_issues:
        priority_actions.append(f"🔴 URGENT: {issue['title']}")

# Orta seviye sorunları ekle
medium_issues = [i for i in issues if i['severity'] == 'Medium']
if medium_issues:
    for issue in medium_issues:
        priority_actions.append(f"🟡 IMPORTANT: {issue['title']}")

# Önerilerden yüksek öncelikli olanları ekle
high_priority_suggestions = [s for s in suggestions if s['priority'] in ['High', 'Medium']]
if high_priority_suggestions:
    for sug in high_priority_suggestions:
        priority_actions.append(f"🟢 RECOMMENDED: {sug['title']}")

if priority_actions:
    for i, action in enumerate(priority_actions[:5], 1):  # İlk 5 tavsiye
        print(f"{i}. {action}")
else:
    print("✅ Tüm kritik iyileştirmeler tamamlanmış!")
    print("⏭️  Opsiyonel: Kalan route'ları blueprint'lere taşıyabilirsiniz")
    print("⏭️  Opsiyonel: Unit testler ekleyebilirsiniz")
    print("⏭️  Opsiyonel: API dokümantasyonu ekleyebilirsiniz")

print("\n" + "=" * 80)
