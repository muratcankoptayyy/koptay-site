#!/usr/bin/env python3
"""
Tevkil Capacitor Setup Script
Otomatik Capacitor kurulumu ve konfigürasyonu
"""

import os
import subprocess
import json
import shutil
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(step, message):
    """Adım mesajı yazdır"""
    print(f"\n{Colors.BLUE}[{step}]{Colors.END} {message}")

def print_success(message):
    """Başarı mesajı"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Hata mesajı"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """Uyarı mesajı"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def run_command(command, shell=True):
    """Terminal komutu çalıştır"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_requirements():
    """Gereksinimleri kontrol et"""
    print_step("1/8", "Gereksinimler kontrol ediliyor...")
    
    requirements = {
        'Node.js': 'node --version',
        'npm': 'npm --version',
        'Git': 'git --version'
    }
    
    all_ok = True
    for name, command in requirements.items():
        success, output = run_command(command)
        if success:
            version = output.strip()
            print_success(f"{name} kurulu: {version}")
        else:
            print_error(f"{name} bulunamadı! Lütfen kurun.")
            all_ok = False
    
    return all_ok

def install_capacitor():
    """Capacitor paketlerini yükle"""
    print_step("2/8", "Capacitor paketleri yükleniyor...")
    
    packages = [
        '@capacitor/core',
        '@capacitor/cli',
        '@capacitor/android',
        '@capacitor/ios',
        '@capacitor/push-notifications',
        '@capacitor/splash-screen',
        '@capacitor/app',
        '@capacitor/keyboard'
    ]
    
    command = f"npm install {' '.join(packages)} --save"
    success, output = run_command(command)
    
    if success:
        print_success("Capacitor paketleri yüklendi")
        return True
    else:
        print_error(f"Paket yükleme hatası: {output}")
        return False

def initialize_capacitor():
    """Capacitor projesini başlat"""
    print_step("3/8", "Capacitor başlatılıyor...")
    
    app_name = "Tevkil"
    app_id = "com.koptay.tevkil"
    web_dir = "templates"  # Flask templates klasörü
    
    command = f'npx cap init "{app_name}" "{app_id}" --web-dir={web_dir}'
    success, output = run_command(command)
    
    if success:
        print_success(f"Capacitor başlatıldı: {app_name} ({app_id})")
        return True
    else:
        print_error(f"Capacitor başlatma hatası: {output}")
        return False

def create_capacitor_config():
    """capacitor.config.json oluştur"""
    print_step("4/8", "Capacitor konfigürasyonu oluşturuluyor...")
    
    config = {
        "appId": "com.koptay.tevkil",
        "appName": "Tevkil",
        "webDir": "templates",
        "server": {
            "url": "https://tevkil.fly.dev",
            "cleartext": False,
            "androidScheme": "https"
        },
        "plugins": {
            "SplashScreen": {
                "launchShowDuration": 2000,
                "backgroundColor": "#1a56db",
                "androidScaleType": "CENTER_CROP",
                "showSpinner": False,
                "androidSpinnerStyle": "large",
                "iosSpinnerStyle": "small",
                "spinnerColor": "#ffffff"
            },
            "PushNotifications": {
                "presentationOptions": ["badge", "sound", "alert"]
            },
            "Keyboard": {
                "resize": "body",
                "style": "dark",
                "resizeOnFullScreen": True
            }
        }
    }
    
    try:
        with open('capacitor.config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print_success("capacitor.config.json oluşturuldu")
        return True
    except Exception as e:
        print_error(f"Config oluşturma hatası: {e}")
        return False

def add_android_platform():
    """Android platformu ekle"""
    print_step("5/8", "Android platformu ekleniyor...")
    
    command = "npx cap add android"
    success, output = run_command(command)
    
    if success:
        print_success("Android platformu eklendi")
        return True
    else:
        print_error(f"Android ekleme hatası: {output}")
        return False

def add_ios_platform():
    """iOS platformu ekle (opsiyonel)"""
    print_step("6/8", "iOS platformu ekleniyor (opsiyonel)...")
    
    # Mac kontrolü
    import platform
    if platform.system() != 'Darwin':
        print_warning("iOS platformu sadece Mac'te eklenebilir. Atlanıyor...")
        return True
    
    command = "npx cap add ios"
    success, output = run_command(command)
    
    if success:
        print_success("iOS platformu eklendi")
        return True
    else:
        print_warning(f"iOS ekleme hatası (normal): {output}")
        return True  # iOS opsiyonel

def create_android_assets():
    """Android için gerekli asset'leri oluştur"""
    print_step("7/8", "Android assets oluşturuluyor...")
    
    # strings.xml
    strings_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Tevkil</string>
    <string name="title_activity_main">Tevkil - Avukat İş Devri</string>
    <string name="package_name">com.koptay.tevkil</string>
    <string name="custom_url_scheme">tevkil</string>
</resources>
'''
    
    android_values_dir = Path('android/app/src/main/res/values')
    android_values_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(android_values_dir / 'strings.xml', 'w', encoding='utf-8') as f:
            f.write(strings_xml)
        print_success("Android strings.xml oluşturuldu")
        return True
    except Exception as e:
        print_warning(f"Strings.xml oluşturulamadı: {e}")
        return False

def sync_project():
    """Capacitor sync"""
    print_step("8/8", "Proje senkronize ediliyor...")
    
    command = "npx cap sync"
    success, output = run_command(command)
    
    if success:
        print_success("Proje senkronize edildi")
        return True
    else:
        print_error(f"Sync hatası: {output}")
        return False

def create_npm_scripts():
    """package.json'a script'ler ekle"""
    print_step("BONUS", "npm scripts ekleniyor...")
    
    try:
        # package.json varsa oku, yoksa oluştur
        if os.path.exists('package.json'):
            with open('package.json', 'r', encoding='utf-8') as f:
                package = json.load(f)
        else:
            package = {
                "name": "tevkil-mobile",
                "version": "1.0.0",
                "description": "Tevkil - Avukat İş Devri Platformu",
                "main": "index.js"
            }
        
        # Scripts ekle
        if 'scripts' not in package:
            package['scripts'] = {}
        
        package['scripts'].update({
            "android:build": "npx cap sync && npx cap open android",
            "ios:build": "npx cap sync && npx cap open ios",
            "sync": "npx cap sync",
            "android:run": "npx cap run android",
            "ios:run": "npx cap run ios"
        })
        
        with open('package.json', 'w', encoding='utf-8') as f:
            json.dump(package, f, indent=2, ensure_ascii=False)
        
        print_success("npm scripts eklendi")
        print(f"\n{Colors.BLUE}Kullanım:{Colors.END}")
        print("  npm run android:build  → Android Studio'da aç")
        print("  npm run ios:build      → Xcode'da aç (Mac)")
        print("  npm run sync           → Değişiklikleri sync et")
        
        return True
    except Exception as e:
        print_warning(f"Scripts eklenemedi: {e}")
        return False

def main():
    """Ana fonksiyon"""
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}  TEVKIL MOBİL APP - CAPACITOR KURULUMU{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
    
    # Gereksinimler kontrolü
    if not check_requirements():
        print_error("\nGereksinimler eksik! SETUP_REQUIREMENTS.md'yi kontrol edin.")
        return False
    
    # Capacitor kurulumu
    steps = [
        install_capacitor,
        initialize_capacitor,
        create_capacitor_config,
        add_android_platform,
        add_ios_platform,
        create_android_assets,
        sync_project,
        create_npm_scripts
    ]
    
    for step in steps:
        if not step():
            print_error(f"\n{step.__name__} başarısız oldu!")
            return False
    
    # Başarı mesajı
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}  ✅ CAPACITOR KURULUMU TAMAMLANDI!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
    
    print(f"{Colors.BLUE}SONRAKI ADIMLAR:{Colors.END}\n")
    print("1. Android build için:")
    print("   npm run android:build")
    print("   → Android Studio açılacak\n")
    
    print("2. iOS build için (Mac):")
    print("   npm run ios:build")
    print("   → Xcode açılacak\n")
    
    print("3. Değişiklik yaptıktan sonra:")
    print("   npm run sync\n")
    
    print(f"{Colors.YELLOW}NOT:{Colors.END} Android Studio'da ilk build 5-10 dakika sürebilir.\n")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\n\nKurulum iptal edildi.")
        exit(1)
    except Exception as e:
        print_error(f"\n\nBeklenmeyen hata: {e}")
        exit(1)
