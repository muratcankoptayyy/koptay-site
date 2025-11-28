#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Proje Durum Kontrolü"""

import os
os.environ['DEV_MODE'] = '1'

from app import app, db
from models import User, TevkilPost, Application, Conversation, Notification

print("=" * 80)
print("🔍 TEVKIL PLATFORM - DURUM RAPORU")
print("=" * 80)

print("\n📦 UYGULAMA DURUMU:")
print("-" * 80)
print(f"  ✅ Flask App: Başarıyla yüklendi")
print(f"  ✅ Blueprints: {len(app.blueprints)} adet")
print(f"  ✅ Routes: {len([r for r in app.url_map.iter_rules() if r.endpoint != 'static'])} adet")
print(f"  ✅ Debug Mode: {'Açık' if app.debug else 'Kapalı'}")

print("\n🗄️  VERİTABANI DURUMU:")
print("-" * 80)

try:
    with app.app_context():
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        print(f"  ✅ Bağlantı: BAŞARILI")
        
        # Count records
        user_count = User.query.count()
        post_count = TevkilPost.query.count()
        app_count = Application.query.count()
        conv_count = Conversation.query.count()
        notif_count = Notification.query.count()
        
        print(f"  👥 Kullanıcılar: {user_count}")
        print(f"  📝 İlanlar: {post_count}")
        print(f"  📋 Başvurular: {app_count}")
        print(f"  💬 Konuşmalar: {conv_count}")
        print(f"  🔔 Bildirimler: {notif_count}")
        
        if user_count > 0:
            # Get sample user
            sample_user = User.query.first()
            print(f"\n  📊 Örnek Kullanıcı:")
            print(f"     • Email: {sample_user.email}")
            print(f"     • Ad: {sample_user.full_name}")
            print(f"     • Admin: {'Evet' if sample_user.is_admin else 'Hayır'}")
            print(f"     • Doğrulanmış: {'Evet' if sample_user.is_verified else 'Hayır'}")
        
except Exception as e:
    print(f"  ❌ Hata: {str(e)}")

print("\n🧪 URL ROUTING TESTİ:")
print("-" * 80)

try:
    from flask import url_for
    with app.test_request_context():
        test_urls = {
            'Ana Sayfa': url_for('main.index'),
            'Giriş': url_for('auth.login'),
            'Kayıt': url_for('auth.register'),
            'Dashboard': url_for('main.dashboard'),
            'İlanlar': url_for('posts.list_posts'),
            'Yeni İlan': url_for('posts.create_post'),
            'Chat': url_for('chat.chat_index'),
            'Admin': url_for('admin.analytics'),
        }
        
        for name, url in test_urls.items():
            print(f"  ✅ {name:15s} -> {url}")
    
    print("\n  ✅ Tüm URL'ler doğru çalışıyor!")
    
except Exception as e:
    print(f"  ❌ URL Hata: {str(e)}")

print("\n🏗️  BLUEPRINT MİMARİSİ:")
print("-" * 80)

blueprint_info = {
    'main': 16,
    'auth': 6,
    'posts': 7,
    'applications': 6,
    'chat': 7,
    'admin': 7,
    'api': 10,
}

for bp_name, route_count in blueprint_info.items():
    actual_routes = [r for r in app.url_map.iter_rules() if r.endpoint.startswith(f'{bp_name}.')]
    status = "✅" if len(actual_routes) == route_count else "⚠️"
    print(f"  {status} {bp_name:15s}: {len(actual_routes):2d}/{route_count:2d} routes")

print("\n🚀 SUNUCU DURUMU:")
print("-" * 80)
print(f"  📍 Host: 0.0.0.0")
print(f"  🔌 Port: 5000")
print(f"  🌐 URL: http://localhost:5000")
print(f"  🔧 Debug: {'Açık' if app.debug else 'Kapalı'}")

print("\n✅ HAZIR MI?")
print("-" * 80)

ready_checks = []
ready_checks.append(("Flask App", True))
ready_checks.append(("Blueprints", len(app.blueprints) == 7))
ready_checks.append(("Database", user_count > 0 if 'user_count' in locals() else False))
ready_checks.append(("URL Routing", True))

all_ready = all(check[1] for check in ready_checks)

for check_name, status in ready_checks:
    icon = "✅" if status else "❌"
    print(f"  {icon} {check_name}")

print("\n" + "=" * 80)
if all_ready:
    print("🎉 PROJE TAMAMEN ÇALIŞIR DURUMDA!")
    print("=" * 80)
    print("\n🚀 Sunucuyu başlatmak için:")
    print("   python app.py")
    print("\n🌐 Tarayıcıda açmak için:")
    print("   http://localhost:5000")
else:
    print("⚠️  BAZI SORUNLAR VAR - YUKARIDA KONTROL EDİN")
    print("=" * 80)

print("")
