"""
Otomatik Proje Temizlik Scripti
Gereksiz dosyaları güvenli şekilde siler ve projeyi optimize eder
"""

import os
import shutil
from pathlib import Path

def create_cleanup_script():
    """PowerShell cleanup script oluştur"""
    
    ps_script = """
# Tevkil Projesi - Otomatik Temizlik Scripti
# Gereksiz dosyaları siler ve projeyi optimize eder

Write-Host "🧹 TEVKIL PROJESİ TEMİZLİK BAŞLIYOR..." -ForegroundColor Cyan
Write-Host ""

$totalDeleted = 0
$totalSize = 0

# 1. BACKUP DOSYALARI
Write-Host "🗑️  Backup dosyaları siliniyor..." -ForegroundColor Yellow
$backupFiles = @(
    "app.py.backup",
    "app_old_backup_20251109_162234.py",
    "app_old.py",
    "tevkil.db.backup_20251021_171328",
    "tevkil.db.backup_20251021_172227",
    "tevkil.db.backup_20251021_172520",
    "tevkil.db.backup_20251021_202433",
    "tevkil_backup_20251021_170839.db",
    "templates\\dashboard.html.backup",
    "templates\\posts_list_backup.html",
    "instance\\tevkil.db.backup_20251021_171328",
    "instance\\tevkil.db.backup_20251021_172227",
    "instance\\tevkil.db.backup_20251021_172520",
    "instance\\tevkil.db.backup_20251021_202433"
)

foreach ($file in $backupFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Remove-Item $file -Force
        $totalDeleted++
        $totalSize += $size
        Write-Host "  ✅ Silindi: $file" -ForegroundColor Green
    }
}

# 2. ESKİ/OLD DOSYALAR
Write-Host "`n📦 Eski/Old dosyalar siliniyor..." -ForegroundColor Yellow
$oldFiles = @(
    "templates\\settings_old.html",
    "templates\\profile_old.html",
    "templates\\index_very_old.html",
    "calculate_bold_position.py",
    "blueprints\\main\\routes_temp.py"
)

foreach ($file in $oldFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Remove-Item $file -Force
        $totalDeleted++
        $totalSize += $size
        Write-Host "  ✅ Silindi: $file" -ForegroundColor Green
    }
}

# 3. ANDROID BUILD ARTIFACTS (DUPLICATE'LER)
Write-Host "`n🤖 Android build artifacts temizleniyor..." -ForegroundColor Yellow
if (Test-Path "android\\app\\build") {
    $size = (Get-ChildItem "android\\app\\build" -Recurse | Measure-Object -Property Length -Sum).Sum
    Remove-Item "android\\app\\build" -Recurse -Force -ErrorAction SilentlyContinue
    $totalSize += $size
    Write-Host "  ✅ Android build klasörü temizlendi: $([math]::Round($size/1MB, 2)) MB" -ForegroundColor Green
}

# 4. ANDROID DUPLICATE ASSETS
Write-Host "`n📱 Android duplicate assets siliniyor..." -ForegroundColor Yellow
if (Test-Path "android\\app\\src\\main\\assets\\public") {
    $size = (Get-ChildItem "android\\app\\src\\main\\assets\\public" -Recurse | Measure-Object -Property Length -Sum).Sum
    Remove-Item "android\\app\\src\\main\\assets\\public" -Recurse -Force -ErrorAction SilentlyContinue
    $totalSize += $size
    Write-Host "  ✅ Android assets duplicate'leri silindi: $([math]::Round($size/1KB, 2)) KB" -ForegroundColor Green
}

# 5. GEREKSIZ TEMPLATE'LER
Write-Host "`n📄 Gereksiz template'ler siliniyor..." -ForegroundColor Yellow
$unusedTemplates = @(
    "templates\\duzenle.html",
    "templates\\ekle.html",
    "templates\\pwa_base.html"
)

foreach ($file in $unusedTemplates) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Remove-Item $file -Force
        $totalDeleted++
        $totalSize += $size
        Write-Host "  ✅ Silindi: $file" -ForegroundColor Green
    }
}

# 6. PHOENIX DUPLICATE TEMPLATE'LER (Kullanılmıyor)
Write-Host "`n🔥 Phoenix duplicate template'ler siliniyor..." -ForegroundColor Yellow
$phoenixDuplicates = @(
    "templates\\phoenix\\admin\\admin_analytics.html",
    "templates\\phoenix\\admin\\admin_user_detail.html",
    "templates\\phoenix\\admin\\whatsapp_ilan.html",
    "templates\\phoenix\\admin\\whatsapp_setup.html",
    "templates\\phoenix\\security\\2fa_setup.html",
    "templates\\phoenix\\security\\security_logs.html",
    "templates\\phoenix\\security\\verify_2fa.html"
)

foreach ($file in $phoenixDuplicates) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Remove-Item $file -Force
        $totalDeleted++
        $totalSize += $size
        Write-Host "  ✅ Silindi: $file" -ForegroundColor Green
    }
}

# 7. GEREKSIZ TEST DOSYALARI (Ana test dosyaları kalsın, temp'ler gitsin)
Write-Host "`n🧪 Gereksiz test dosyaları siliniyor..." -ForegroundColor Yellow
$tempTests = @(
    "test_template.py",
    "test_template_ilan.py",
    "test_udf_template.py"
)

foreach ($file in $tempTests) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Remove-Item $file -Force
        $totalDeleted++
        $totalSize += $size
        Write-Host "  ✅ Silindi: $file" -ForegroundColor Green
    }
}

# 8. ANALYZE SCRIPT (kendini sil)
if (Test-Path "analyze_template_offsets.py") {
    Remove-Item "analyze_template_offsets.py" -Force
    $totalDeleted++
    Write-Host "  ✅ Silindi: analyze_template_offsets.py" -ForegroundColor Green
}

# ÖZET
Write-Host "`n" + ("="*80) -ForegroundColor Cyan
Write-Host "✅ TEMİZLİK TAMAMLANDI!" -ForegroundColor Green
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 İstatistikler:" -ForegroundColor White
Write-Host "  🗑️  Silinen Dosya: $totalDeleted" -ForegroundColor Yellow
Write-Host "  💾 Kazanılan Alan: $([math]::Round($totalSize/1MB, 2)) MB" -ForegroundColor Yellow
Write-Host ""

# GİTIGNORE KONTROLÜ
Write-Host "📋 .gitignore kontrol ediliyor..." -ForegroundColor Yellow
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/

# Virtual Environment
venv/
env/
ENV/
tevkil_env/

# Database
*.db
*.db-journal
instance/*.db
instance/*.db-journal
*.db.backup*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
package-lock.json
npm-debug.log*

# Android
android/app/build/
android/build/
android/.gradle/
android/local.properties
*.apk
*.ap_
*.aab

# Logs
*.log
logs/

# Environment
.env
.env.local

# Backups
*.backup
*_old.*
*_backup.*

# Temporary
*.tmp
temp/
tmp/
"@

Set-Content -Path ".gitignore" -Value $gitignoreContent -Force
Write-Host "  ✅ .gitignore güncellendi" -ForegroundColor Green

Write-Host "`n🎉 Proje optimize edildi ve temizlendi!" -ForegroundColor Green
Write-Host ""
"""
    
    with open('cleanup_project.ps1', 'w', encoding='utf-8') as f:
        f.write(ps_script)
    
    print("✅ cleanup_project.ps1 oluşturuldu!")
    print("\n📋 Kullanım:")
    print("   PowerShell'de çalıştırın: .\\cleanup_project.ps1")

if __name__ == "__main__":
    create_cleanup_script()
