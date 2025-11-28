"""
Temizlik Sonrası Durum Kontrolü
"""

import os
from pathlib import Path

def check_cleanup_status():
    print("=" * 80)
    print("🧹 TEMİZLİK SONRASI DURUM KONTROLÜ")
    print("=" * 80)
    print()
    
    # Silinmesi gereken dosyalar kontrol edilsin
    files_to_check = {
        'Backup Dosyaları': [
            'app.py.backup',
            'app_old_backup_20251109_162234.py',
            'app_old.py',
            'templates/dashboard.html.backup',
            'templates/posts_list_backup.html',
        ],
        'Eski Dosyalar': [
            'templates/settings_old.html',
            'templates/profile_old.html',
            'templates/index_very_old.html',
            'calculate_bold_position.py',
            'blueprints/main/routes_temp.py',
        ],
        'Gereksiz Template\'ler': [
            'templates/duzenle.html',
            'templates/ekle.html',
            'templates/pwa_base.html',
        ],
        'Phoenix Duplicate\'ler': [
            'templates/phoenix/admin/admin_analytics.html',
            'templates/phoenix/admin/admin_user_detail.html',
            'templates/phoenix/admin/whatsapp_ilan.html',
            'templates/phoenix/admin/whatsapp_setup.html',
            'templates/phoenix/security/2fa_setup.html',
            'templates/phoenix/security/security_logs.html',
            'templates/phoenix/security/verify_2fa.html',
        ],
        'Temp Test Dosyaları': [
            'test_template.py',
            'test_template_ilan.py',
            'test_udf_template.py',
            'analyze_template_offsets.py',
        ]
    }
    
    all_cleaned = True
    for category, files in files_to_check.items():
        print(f"📁 {category}:")
        category_cleaned = True
        for file in files:
            filepath = Path(file)
            if filepath.exists():
                print(f"  ❌ HALA VAR: {file}")
                category_cleaned = False
                all_cleaned = False
            else:
                print(f"  ✅ Silindi: {file}")
        
        if category_cleaned:
            print(f"  ✨ {category} tamamen temizlendi!")
        print()
    
    # Android build kontrol
    print("🤖 Android Build:")
    android_build = Path('android/app/build')
    if android_build.exists():
        print(f"  ⚠️  Build klasörü var (normal, development sırasında oluşur)")
    else:
        print(f"  ✅ Build klasörü temiz")
    print()
    
    # Veritabanı backup kontrol
    print("🗄️  Veritabanı Backup'ları:")
    db_backups = list(Path('.').glob('*.db.backup_*')) + list(Path('instance').glob('*.db.backup_*'))
    if db_backups:
        print(f"  ❌ {len(db_backups)} backup dosyası bulundu:")
        for backup in db_backups:
            print(f"     - {backup}")
    else:
        print(f"  ✅ Tüm backup'lar temizlendi")
    print()
    
    # .gitignore kontrol
    print("📋 .gitignore Durumu:")
    gitignore = Path('.gitignore')
    if gitignore.exists():
        content = gitignore.read_text(encoding='utf-8')
        checks = {
            '*.backup': '*.backup' in content,
            '*_old.*': '*_old.*' in content,
            'android/app/build/': 'android/app/build/' in content,
            '*.db.backup*': '*.db.backup*' in content,
            'ngrok.exe': 'ngrok.exe' in content,
        }
        
        all_present = all(checks.values())
        if all_present:
            print("  ✅ .gitignore güncel ve tam")
        else:
            print("  ⚠️  .gitignore eksik kurallar:")
            for rule, present in checks.items():
                if not present:
                    print(f"     ❌ {rule}")
    else:
        print("  ❌ .gitignore bulunamadı")
    print()
    
    # Proje boyutu
    print("📊 Proje İstatistikleri:")
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk('.'):
        # Skip specific folders
        if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', 'tevkil_env', 
                                         'android/app/build', 'android/.gradle']):
            continue
        
        for file in files:
            try:
                filepath = Path(root) / file
                file_count += 1
                total_size += filepath.stat().st_size
            except:
                pass
    
    print(f"  📁 Toplam Dosya: {file_count:,}")
    print(f"  💾 Toplam Boyut: {total_size / (1024*1024):.2f} MB")
    print()
    
    # Sonuç
    print("=" * 80)
    if all_cleaned:
        print("✅ TEMİZLİK BAŞARILI!")
        print("   Tüm gereksiz dosyalar temizlendi.")
    else:
        print("⚠️  TEMİZLİK KISMEN BAŞARILI")
        print("   Bazı dosyalar hala mevcut (yukarıda işaretlendi)")
    print("=" * 80)
    print()
    
    # Öneriler
    print("💡 SONRAKİ ADIMLAR:")
    print("  1. ✅ Git commit yapın (temizlik değişikliklerini kaydet)")
    print("  2. ✅ Uygulamayı test edin (python app.py)")
    print("  3. ✅ Tüm route'ların çalıştığını kontrol edin")
    print()

if __name__ == "__main__":
    check_cleanup_status()
