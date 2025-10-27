# Tevkil AAB Build Script
# PowerShell script to build signed release AAB

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  📦 TEVKIL AAB BUILD SCRIPT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check keystore.properties
$keystoreProps = "android\keystore.properties"
if (-not (Test-Path $keystoreProps)) {
    Write-Host "❌ HATA: keystore.properties bulunamadı!" -ForegroundColor Red
    Write-Host "📝 Lütfen önce keystore oluşturun:" -ForegroundColor Yellow
    Write-Host "   1. KEYSTORE_SETUP.md dosyasını okuyun" -ForegroundColor Yellow
    Write-Host "   2. keytool komutu ile keystore oluşturun" -ForegroundColor Yellow
    Write-Host "   3. android/keystore.properties dosyası oluşturun" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ keystore.properties bulundu" -ForegroundColor Green
Write-Host ""

# Step 1: Capacitor Copy
Write-Host "🔄 1/3: Capacitor assets kopyalanıyor..." -ForegroundColor Yellow
try {
    npx cap copy android
    if ($LASTEXITCODE -ne 0) { throw "Capacitor copy başarısız" }
    Write-Host "✅ Capacitor copy tamamlandı" -ForegroundColor Green
} catch {
    Write-Host "❌ Capacitor copy hatası: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Gradle Clean
Write-Host "🧹 2/3: Gradle clean..." -ForegroundColor Yellow
Push-Location android
try {
    .\gradlew clean
    if ($LASTEXITCODE -ne 0) { throw "Gradle clean başarısız" }
    Write-Host "✅ Clean tamamlandı" -ForegroundColor Green
} catch {
    Write-Host "❌ Clean hatası: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host ""

# Step 3: Bundle Release
Write-Host "🏗️ 3/3: Release AAB oluşturuluyor..." -ForegroundColor Yellow
Write-Host "   (Bu işlem 1-2 dakika sürebilir...)" -ForegroundColor Gray
try {
    .\gradlew bundleRelease
    if ($LASTEXITCODE -ne 0) { throw "Bundle release başarısız" }
    Write-Host "✅ AAB build tamamlandı" -ForegroundColor Green
} catch {
    Write-Host "❌ Build hatası: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location
Write-Host ""

# Check output
$aabPath = "android\app\build\outputs\bundle\release\app-release.aab"
if (Test-Path $aabPath) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ AAB BAŞARIYLA OLUŞTURULDU!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # File info
    $fileInfo = Get-Item $aabPath
    $sizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
    $sizeKB = [math]::Round($fileInfo.Length / 1KB, 0)
    
    Write-Host "📍 Konum: $aabPath" -ForegroundColor Cyan
    Write-Host "📦 Boyut: $sizeMB MB ($sizeKB KB)" -ForegroundColor Cyan
    Write-Host "📅 Tarih: $($fileInfo.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Cyan
    Write-Host ""
    
    # Next steps
    Write-Host "🚀 SONRAKI ADIMLAR:" -ForegroundColor Yellow
    Write-Host "   1. Play Console'a giriş yapın" -ForegroundColor White
    Write-Host "   2. Production → Testing → Internal testing" -ForegroundColor White
    Write-Host "   3. 'Create new release' tıklayın" -ForegroundColor White
    Write-Host "   4. AAB dosyasını sürükle-bırak yapın" -ForegroundColor White
    Write-Host "   5. Release notes ekleyin ve yayınlayın" -ForegroundColor White
    Write-Host ""
    
    # Open folder
    $openFolder = Read-Host "📂 AAB klasörünü açmak ister misiniz? (Y/N)"
    if ($openFolder -eq "Y" -or $openFolder -eq "y") {
        explorer.exe (Resolve-Path "android\app\build\outputs\bundle\release")
    }
    
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ❌ AAB OLUŞTURULAMADI!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔍 Olası nedenler:" -ForegroundColor Yellow
    Write-Host "   - Gradle build hatası (yukarıdaki log'lara bakın)" -ForegroundColor White
    Write-Host "   - Keystore şifresi yanlış" -ForegroundColor White
    Write-Host "   - JDK sürümü uyumsuz" -ForegroundColor White
    Write-Host "   - Gradle cache sorunu (./gradlew clean tekrar deneyin)" -ForegroundColor White
    exit 1
}
