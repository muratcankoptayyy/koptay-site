"""
Proje Temizlik Analizi
Gereksiz dosyaları, duplicate'leri ve performans sorunlarını tespit eder
"""

import os
from pathlib import Path
from collections import defaultdict
import hashlib

def get_file_hash(filepath):
    """Dosyanın MD5 hash'ini hesapla"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def analyze_project():
    base_path = Path('.')
    
    # Kategoriler
    backup_files = []
    old_files = []
    duplicate_files = defaultdict(list)
    large_files = []
    unused_migrations = []
    test_files = []
    documentation_files = []
    temp_files = []
    
    # Hash bazlı duplicate tespiti için
    file_hashes = defaultdict(list)
    
    print("🔍 Proje dosyaları taranıyor...\n")
    
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk('.'):
        # Bazı klasörleri atla
        if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', '.venv', 'venv', 
                                         'android/app/build', 'android/gradle', 
                                         'themes/phoenix/node_modules']):
            continue
            
        for file in files:
            filepath = Path(root) / file
            file_count += 1
            
            try:
                size = filepath.stat().st_size
                total_size += size
                
                # Backup dosyaları
                if any(x in file.lower() for x in ['backup', '.bak', '.old']):
                    backup_files.append((str(filepath), size))
                
                # Old/eski dosyalar
                if any(x in file.lower() for x in ['_old', '_eski', 'old_', 'very_old']):
                    old_files.append((str(filepath), size))
                
                # Temp dosyalar
                if any(x in file.lower() for x in ['.tmp', 'temp_', '_temp', '~']):
                    temp_files.append((str(filepath), size))
                
                # Test dosyaları
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append((str(filepath), size))
                
                # Migration dosyaları
                if file.startswith('add_') or file.startswith('migrate_'):
                    unused_migrations.append((str(filepath), size))
                
                # Documentation
                if file.endswith('.md') or file.endswith('.txt'):
                    documentation_files.append((str(filepath), size))
                
                # Büyük dosyalar (>1MB)
                if size > 1024 * 1024:
                    large_files.append((str(filepath), size))
                
                # Duplicate tespiti (sadece belirli uzantılar için)
                if file.endswith(('.py', '.html', '.js', '.css')):
                    file_hash = get_file_hash(filepath)
                    if file_hash:
                        file_hashes[file_hash].append((str(filepath), size))
                        
            except Exception as e:
                pass
    
    # Duplicate'leri bul
    for hash_val, files in file_hashes.items():
        if len(files) > 1:
            duplicate_files[hash_val] = files
    
    # RAPORLAMA
    print("=" * 80)
    print("📊 PROJE TEMİZLİK ANALİZİ")
    print("=" * 80)
    print(f"\n📁 Toplam Dosya: {file_count:,}")
    print(f"💾 Toplam Boyut: {total_size / (1024*1024):.2f} MB\n")
    
    # 1. BACKUP DOSYALARI
    if backup_files:
        backup_size = sum(s for _, s in backup_files)
        print(f"\n🗑️  BACKUP DOSYALARI ({len(backup_files)} adet - {backup_size/(1024*1024):.2f} MB)")
        print("-" * 80)
        for file, size in sorted(backup_files, key=lambda x: x[1], reverse=True):
            print(f"  • {file:60} {size/(1024):.1f} KB")
    
    # 2. OLD/ESKİ DOSYALAR
    if old_files:
        old_size = sum(s for _, s in old_files)
        print(f"\n📦 ESKİ/OLD DOSYALAR ({len(old_files)} adet - {old_size/(1024*1024):.2f} MB)")
        print("-" * 80)
        for file, size in sorted(old_files, key=lambda x: x[1], reverse=True):
            print(f"  • {file:60} {size/(1024):.1f} KB")
    
    # 3. DUPLICATE DOSYALAR
    if duplicate_files:
        dup_count = sum(len(files) - 1 for files in duplicate_files.values())
        dup_size = sum(sum(s for _, s in files[1:]) for files in duplicate_files.values())
        print(f"\n🔄 DUPLICATE DOSYALAR ({dup_count} adet gereksiz - {dup_size/(1024*1024):.2f} MB kazanılabilir)")
        print("-" * 80)
        for i, (hash_val, files) in enumerate(list(duplicate_files.items())[:10], 1):
            print(f"  Grup {i} ({len(files)} aynı dosya):")
            for file, size in files:
                print(f"    • {file}")
    
    # 4. BÜYÜK DOSYALAR
    if large_files:
        print(f"\n📏 BÜYÜK DOSYALAR (>1MB) ({len(large_files)} adet)")
        print("-" * 80)
        for file, size in sorted(large_files, key=lambda x: x[1], reverse=True)[:20]:
            print(f"  • {file:60} {size/(1024*1024):.2f} MB")
    
    # 5. TEST DOSYALARI
    if test_files:
        test_size = sum(s for _, s in test_files)
        print(f"\n🧪 TEST DOSYALARI ({len(test_files)} adet - {test_size/(1024):.1f} KB)")
        print("-" * 80)
        print(f"  Test dosyaları development için gerekli olabilir")
        print(f"  Production'da gereksiz: {len(test_files)} dosya, {test_size/(1024):.1f} KB")
    
    # 6. MIGRATION SCRIPTLERI
    if unused_migrations:
        mig_size = sum(s for _, s in unused_migrations)
        print(f"\n🔧 MIGRATION SCRIPTLERI ({len(unused_migrations)} adet - {mig_size/(1024):.1f} KB)")
        print("-" * 80)
        print(f"  Eski migration scriptleri artık gereksiz olabilir")
        for file, size in sorted(unused_migrations)[:15]:
            print(f"  • {file}")
    
    # 7. DOKÜMANTASYON
    doc_size = sum(s for _, s in documentation_files)
    print(f"\n📄 DOKÜMANTASYON ({len(documentation_files)} adet - {doc_size/(1024*1024):.2f} MB)")
    print("-" * 80)
    print(f"  .md ve .txt dosyaları - çoğu gerekli ama bazıları eski olabilir")
    
    # ÖZET VE ÖNERİLER
    print("\n" + "=" * 80)
    print("💡 ÖNERİLER")
    print("=" * 80)
    
    potential_savings = 0
    recommendations = []
    
    if backup_files:
        backup_size = sum(s for _, s in backup_files)
        potential_savings += backup_size
        recommendations.append(f"✅ {len(backup_files)} backup dosyası silinebilir → {backup_size/(1024*1024):.2f} MB kazanç")
    
    if old_files:
        old_size = sum(s for _, s in old_files)
        potential_savings += old_size
        recommendations.append(f"✅ {len(old_files)} eski dosya silinebilir → {old_size/(1024*1024):.2f} MB kazanç")
    
    if duplicate_files:
        dup_count = sum(len(files) - 1 for files in duplicate_files.values())
        dup_size = sum(sum(s for _, s in files[1:]) for files in duplicate_files.values())
        potential_savings += dup_size
        recommendations.append(f"✅ {dup_count} duplicate dosya silinebilir → {dup_size/(1024*1024):.2f} MB kazanç")
    
    if temp_files:
        temp_size = sum(s for _, s in temp_files)
        potential_savings += temp_size
        recommendations.append(f"✅ {len(temp_files)} temp dosyası silinebilir → {temp_size/(1024):.1f} KB kazanç")
    
    if recommendations:
        for rec in recommendations:
            print(f"\n{rec}")
    
    print(f"\n{'='*80}")
    print(f"💰 TOPLAM POTANSİYEL KAZANÇ: {potential_savings/(1024*1024):.2f} MB")
    print(f"📊 Mevcut Boyut: {total_size/(1024*1024):.2f} MB")
    print(f"🎯 Temizlik Sonrası: {(total_size-potential_savings)/(1024*1024):.2f} MB")
    print(f"📉 Azalma Oranı: {(potential_savings/total_size*100):.1f}%")
    print("=" * 80)
    
    # SİLİNEBİLECEK DOSYALARIN LİSTESİ
    print("\n\n📋 SİLİNMESİ ÖNERİLEN DOSYALAR:")
    print("=" * 80)
    
    deletable = []
    
    # Kesinlikle silinebilir
    deletable.extend([f for f, _ in backup_files])
    deletable.extend([f for f, _ in old_files])
    deletable.extend([f for f, _ in temp_files])
    
    # Duplicate'lerden fazladan olanlar (ilkini tut)
    for files in duplicate_files.values():
        deletable.extend([f for f, _ in files[1:]])
    
    print(f"\n🗑️  Toplam {len(deletable)} dosya silinebilir:\n")
    for i, file in enumerate(sorted(deletable), 1):
        print(f"{i:3}. {file}")
    
    # PERFORMANS ÖNERİLERİ
    print("\n\n⚡ PERFORMANS ÖNERİLERİ:")
    print("=" * 80)
    
    perf_recommendations = [
        "1. 🗄️  Veritabanı backup dosyalarını (.db.backup_*) klasör dışına taşı",
        "2. 📦 app_old.py ve app_old_backup_*.py dosyalarını sil (app.py çalışıyor)",
        "3. 🧪 Test dosyalarını ayrı bir /tests klasörüne topla",
        "4. 📝 Eski .md dokümantasyonları /archive klasörüne taşı",
        "5. 🔄 Migration scriptlerini /migrations altında tek klasörde topla",
        "6. 🖼️  Android res/drawable içindeki splash görsellerini optimize et",
        "7. 📦 node_modules klasörünü .gitignore'a ekle (zaten var mı kontrol et)",
        "8. 🗜️  Static dosyaları (CSS/JS) minify et",
        "9. 🖼️  PNG icon'ları WebP formatına çevir (%30 daha küçük)",
        "10. 📋 Kullanılmayan template'leri sil veya arşivle"
    ]
    
    for rec in perf_recommendations:
        print(f"  {rec}")
    
    print("\n\n✅ Analiz tamamlandı!")
    
    return {
        'backup_files': backup_files,
        'old_files': old_files,
        'duplicate_files': duplicate_files,
        'temp_files': temp_files,
        'deletable': deletable,
        'potential_savings': potential_savings,
        'total_size': total_size
    }

if __name__ == "__main__":
    results = analyze_project()
